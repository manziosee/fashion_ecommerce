from odoo import models, fields, api, tools
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    @api.model
    def _get_low_stock_products(self):
        """Get products with low stock levels"""
        products = self.env['product.template'].search([
            ('type', '=', 'product'),
            ('target_audience', '!=', False)  # Fashion products only
        ])
        
        low_stock_products = []
        for product in products:
            if product.qty_available <= product.min_stock_level:
                low_stock_products.append({
                    'product': product,
                    'current_stock': product.qty_available,
                    'min_stock': product.min_stock_level,
                    'shortage': product.min_stock_level - product.qty_available
                })
        
        return low_stock_products

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _action_done(self, cancel_backorder=False):
        """Override to update stock status after stock moves"""
        result = super(StockMove, self)._action_done(cancel_backorder)
        
        # Update stock status for fashion products
        for move in self:
            if move.product_id.product_tmpl_id.target_audience:
                move.product_id.product_tmpl_id._compute_stock_status()
                
        return result

class FashionInventoryReport(models.Model):
    _name = 'fashion.inventory.report'
    _description = 'Fashion Inventory Report'
    _auto = False
    
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
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    pt.id,
                    pt.id as product_id,
                    pt.brand,
                    pt.target_audience,
                    COALESCE(SUM(sq.quantity), 0) as qty_available,
                    pt.min_stock_level,
                    pt.max_stock_level,
                    CASE 
                        WHEN COALESCE(SUM(sq.quantity), 0) <= 0 THEN 'out_of_stock'
                        WHEN COALESCE(SUM(sq.quantity), 0) <= pt.min_stock_level THEN 'low_stock'
                        ELSE 'in_stock'
                    END as stock_status
                FROM product_template pt
                LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
                LEFT JOIN stock_quant sq ON sq.product_id = pp.id 
                    AND sq.location_id IN (
                        SELECT id FROM stock_location 
                        WHERE usage = 'internal'
                    )
                WHERE pt.target_audience IS NOT NULL
                AND pt.type = 'product'
                GROUP BY pt.id, pt.brand, pt.target_audience, pt.min_stock_level, pt.max_stock_level
            )
        """ % self._table)
