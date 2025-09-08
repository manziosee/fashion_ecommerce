from odoo import models, fields, api
from odoo.exceptions import ValidationError

class FashionProductReview(models.Model):
    _name = 'fashion.product.review'
    _description = 'Fashion Product Review'
    _rec_name = 'title'
    _order = 'create_date desc'

    title = fields.Char(string='Review Title', required=True)
    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    rating = fields.Selection([
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars')
    ], string='Rating', required=True)
    review_text = fields.Text(string='Review')
    date_review = fields.Datetime(string='Review Date', default=fields.Datetime.now)
    verified_purchase = fields.Boolean(string='Verified Purchase', default=False)
    helpful_count = fields.Integer(string='Helpful Count', default=0)
    
    # Moderation fields
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft')
    
    @api.constrains('rating')
    def _check_rating(self):
        for record in self:
            if record.rating not in ['1', '2', '3', '4', '5']:
                raise ValidationError("Rating must be between 1 and 5 stars")
    
    @api.model
    def create(self, vals):
        # Check if customer has purchased this product
        if vals.get('partner_id') and vals.get('product_id'):
            purchase_lines = self.env['sale.order.line'].search([
                ('order_id.partner_id', '=', vals['partner_id']),
                ('product_id.product_tmpl_id', '=', vals['product_id']),
                ('order_id.state', 'in', ['sale', 'done'])
            ])
            if purchase_lines:
                vals['verified_purchase'] = True
        
        return super().create(vals)
    
    def action_publish(self):
        """Publish the review"""
        self.state = 'published'
    
    def action_reject(self):
        """Reject the review"""
        self.state = 'rejected'
    
    @api.model
    def get_product_reviews(self, product_id, limit=10):
        """Get published reviews for a product"""
        return self.search([
            ('product_id', '=', product_id),
            ('state', '=', 'published')
        ], limit=limit)
    
    @api.model
    def get_average_rating(self, product_id):
        """Calculate average rating for a product"""
        reviews = self.search([
            ('product_id', '=', product_id),
            ('state', '=', 'published')
        ])
        if not reviews:
            return 0
        
        total_rating = sum(int(review.rating) for review in reviews)
        return round(total_rating / len(reviews), 1)