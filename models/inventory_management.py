from odoo import models, fields, api, tools
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.model
    def _get_low_stock_products(self):
        """Get products with low stock levels using optimized query"""
        # Use SQL query to avoid N+1 problem
        query = """
            SELECT pt.id, pt.name, pt.min_stock_level,
                   COALESCE(SUM(sq.quantity), 0) as current_stock,
                   (pt.min_stock_level - COALESCE(SUM(sq.quantity), 0)) as shortage
            FROM product_template pt
            LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
            LEFT JOIN stock_quant sq ON sq.product_id = pp.id 
                AND sq.location_id IN (
                    SELECT id FROM stock_location WHERE usage = 'internal'
                )
            WHERE pt.type = 'product' 
                AND pt.target_audience IS NOT NULL
                AND pt.min_stock_level > 0
            GROUP BY pt.id, pt.name, pt.min_stock_level
            HAVING COALESCE(SUM(sq.quantity), 0) <= pt.min_stock_level
            ORDER BY shortage DESC
        """
        
        self.env.cr.execute(query)
        results = self.env.cr.dictfetchall()
        
        low_stock_products = []
        for result in results:
            product = self.env['product.template'].browse(result['id'])
            low_stock_products.append({
                'product': product,
                'current_stock': result['current_stock'],
                'min_stock': result['min_stock_level'],
                'shortage': result['shortage']
            })
        
        return low_stock_products

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _action_done(self, cancel_backorder=False):
        """Override to update stock status after stock moves"""
        result = super(StockMove, self)._action_done(cancel_backorder)
        
        # Batch update stock status for fashion products
        fashion_products = self.mapped('product_id.product_tmpl_id').filtered('target_audience')
        if fashion_products:
            fashion_products._compute_stock_status()
                
        return result

class FashionInventoryReport(models.Model):
    _name = 'fashion.inventory.report'
    _description = 'Fashion Inventory Report'
    _auto = False
    _rec_name = 'product_id'
    
    product_id = fields.Many2one('product.template', string='Product')
    brand = fields.Char(string='Brand')
    target_audience = fields.Selection([
        ('men', 'Men'),
        ('women', 'Women'),
        ('children', 'Children')
    ], string='Target Audience')
    qty_available = fields.Float(string='Quantity Available')
    min_stock_level = fields.Float(string='Minimum Stock')
    max_stock_level = fields.Float(string='Maximum Stock')
    stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock')
    ], string='Stock Status')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Optimized SQL with proper indexing hints
        query = f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                SELECT
                    pt.id,
                    pt.id as product_id,
                    pt.brand,
                    pt.target_audience,
                    COALESCE(stock_data.qty_available, 0) as qty_available,
                    pt.min_stock_level,
                    pt.max_stock_level,
                    CASE 
                        WHEN COALESCE(stock_data.qty_available, 0) <= 0 THEN 'out_of_stock'
                        WHEN COALESCE(stock_data.qty_available, 0) <= pt.min_stock_level THEN 'low_stock'
                        ELSE 'in_stock'
                    END as stock_status
                FROM product_template pt
                LEFT JOIN (
                    SELECT 
                        pp.product_tmpl_id,
                        SUM(sq.quantity) as qty_available
                    FROM product_product pp
                    INNER JOIN stock_quant sq ON sq.product_id = pp.id
                    INNER JOIN stock_location sl ON sl.id = sq.location_id AND sl.usage = 'internal'
                    GROUP BY pp.product_tmpl_id
                ) stock_data ON stock_data.product_tmpl_id = pt.id
                WHERE pt.target_audience IS NOT NULL
                AND pt.type = 'product'
            )
        """
        self.env.cr.execute(query)
