from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FashionWishlist(models.Model):
    _name = 'fashion.wishlist'
    _description = 'Fashion Product Wishlist'
    _rec_name = 'product_id'
    _order = 'create_date desc'

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    date_added = fields.Datetime(string='Date Added', default=fields.Datetime.now)
    
    # Product details for quick access
    product_name = fields.Char(related='product_id.name', store=True)
    product_price = fields.Float(related='product_id.list_price', store=True)
    product_brand = fields.Char(related='product_id.brand', store=True)
    product_image = fields.Image(related='product_id.image_1920')
    
    _sql_constraints = [
        ('unique_partner_product', 'unique(partner_id, product_id)', 
         'Product already exists in wishlist!')
    ]
    
    @api.model
    def toggle_wishlist(self, product_id, partner_id=None):
        """Add or remove product from wishlist"""
        if not partner_id:
            partner_id = self.env.user.partner_id.id
            
        existing = self.search([
            ('partner_id', '=', partner_id),
            ('product_id', '=', product_id)
        ])
        
        if existing:
            existing.unlink()
            return {'action': 'removed', 'in_wishlist': False}
        else:
            self.create({
                'partner_id': partner_id,
                'product_id': product_id
            })
            return {'action': 'added', 'in_wishlist': True}
    
    @api.model
    def get_wishlist_products(self, partner_id=None):
        """Get all wishlist products for a customer"""
        if not partner_id:
            partner_id = self.env.user.partner_id.id
            
        wishlist_items = self.search([('partner_id', '=', partner_id)])
        return wishlist_items.mapped('product_id')