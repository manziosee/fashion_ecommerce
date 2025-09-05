from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class FashionWebsite(http.Controller):

    @http.route('/', type='http', auth="public", website=True)
    def homepage(self, **kw):
        # Get only fashion products (with target_audience field)
        domain = [
            ('website_published', '=', True), 
            ('sale_ok', '=', True),
            ('target_audience', '!=', False)
        ]
        products = request.env['product.template'].search(domain, limit=8)
        return request.render("fashion_ecommerce.homepage", {'products': products})

    @http.route('/shop', type='http', auth="public", website=True)
    def shop(self, target_audience=None, **kw):
        # Base domain for fashion products only
        domain = [
            ('website_published', '=', True), 
            ('sale_ok', '=', True),
            ('target_audience', '!=', False)
        ]
        
        # Add target audience filter if specified
        if target_audience:
            domain.append(('target_audience', '=', target_audience))
            
        products = request.env['product.template'].search(domain)
        
        # Get current cart for cart functionality
        order = request.website.sale_get_order()
        
        return request.render("fashion_ecommerce.shop_page", {
            'products': products, 
            'audience': target_audience,
            'website_sale_current_pl': order
        })

class FashionWebsiteSale(WebsiteSale):
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=["POST"], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Override to handle fashion-specific cart updates"""
        result = super(FashionWebsiteSale, self).cart_update(product_id, add_qty, set_qty, **kw)
        
        # Redirect to cart page after adding item
        if isinstance(result, dict) and result.get('cart_quantity'):
            return request.redirect('/shop/cart')
        return result
