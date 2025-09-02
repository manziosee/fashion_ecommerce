from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    target_audience = fields.Selection([
        ('men', 'Men'),
        ('women', 'Women'),
        ('children', 'Children')
    ], string="Target Audience")
    
    # Fashion-specific fields
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
    
    # Enhanced for inventory management
    min_stock_level = fields.Float(string="Minimum Stock Level", default=10.0)
    max_stock_level = fields.Float(string="Maximum Stock Level", default=100.0)
