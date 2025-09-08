from odoo import models, fields, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    target_audience = fields.Selection([
        ('men', 'Men'),
        ('women', 'Women'),
        ('children', 'Children')
    ], string="Target Audience")
    
    brand = fields.Char(string="Brand")
    season = fields.Selection([
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
        ('all_season', 'All Season')
    ], string="Season")
    
    clothing_size = fields.Selection([
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
        ('xxxl', 'XXXL')
    ], string="Size")
    
    color = fields.Char(string="Color")
    material = fields.Char(string="Material")
    
    # Inventory Management
    min_stock_level = fields.Float(string="Minimum Stock Level", default=10.0)
    max_stock_level = fields.Float(string="Maximum Stock Level", default=100.0)
    stock_status = fields.Selection([
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock')
    ], string="Stock Status", compute="_compute_stock_status", store=True)
    
    # B2B Pricing
    b2b_price = fields.Float(string="B2B Price", help="Special price for B2B customers")
    b2b_min_qty = fields.Float(string="B2B Minimum Quantity", default=1.0)
    
    # Reviews
    fashion_review_ids = fields.One2many('fashion.product.review', 'product_id', string='Reviews')
    review_count = fields.Integer(string='Review Count', compute='_compute_review_stats', store=True)
    average_rating = fields.Float(string='Average Rating', compute='_compute_review_stats', store=True)
    
    @api.depends('qty_available', 'min_stock_level')
    def _compute_stock_status(self):
        for product in self:
            if product.qty_available <= 0:
                product.stock_status = 'out_of_stock'
            elif product.qty_available <= product.min_stock_level:
                product.stock_status = 'low_stock'
            else:
                product.stock_status = 'in_stock'
    
    @api.depends('fashion_review_ids.state', 'fashion_review_ids.rating')
    def _compute_review_stats(self):
        for product in self:
            published_reviews = product.fashion_review_ids.filtered(lambda r: r.state == 'published')
            product.review_count = len(published_reviews)
            if published_reviews:
                total_rating = sum(int(review.rating) for review in published_reviews)
                product.average_rating = round(total_rating / len(published_reviews), 1)
            else:
                product.average_rating = 0.0
    
    def action_replenish_stock(self):
        """Action to create purchase order for stock replenishment"""
        if self.qty_available > self.min_stock_level:
            raise UserError("Stock level is sufficient. No replenishment needed.")
        
        # Validate max stock level
        if self.max_stock_level <= self.qty_available:
            raise UserError("Maximum stock level must be greater than current stock.")
        
        if self.max_stock_level <= self.min_stock_level:
            raise UserError("Maximum stock level must be greater than minimum stock level.")
        
        # Create procurement for replenishment
        qty_to_order = max(0, self.max_stock_level - self.qty_available)
        
        if qty_to_order <= 0:
            raise UserError("No quantity to order calculated.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Replenish Stock',
            'res_model': 'stock.warehouse.orderpoint',
            'view_mode': 'form',
            'context': {
                'default_product_id': self.product_variant_id.id,
                'default_product_min_qty': self.min_stock_level,
                'default_product_max_qty': self.max_stock_level,
                'default_qty_to_order': qty_to_order,
            },
            'target': 'new',
        }
