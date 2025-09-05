from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class FashionEcommerce(WebsiteSale):
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=["POST"], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Enhanced cart update with stock validation"""
        product = request.env['product.product'].browse(int(product_id))
        
        # Check stock availability
        if product.qty_available < float(add_qty):
            return request.render('fashion_ecommerce.stock_unavailable', {
                'product': product,
                'available_qty': product.qty_available,
                'requested_qty': add_qty
            })
        
        # Call parent method
        result = super(FashionEcommerce, self).cart_update(product_id, add_qty, set_qty, **kw)
        
        # Mark as website order
        order = request.website.sale_get_order()
        if order:
            order.website_order = True
            order.customer_type = 'b2c'  # Default for website orders
            
        return result
    
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        """Enhanced checkout with delivery options"""
        order = request.website.sale_get_order()
        
        if not order or not order.order_line:
            return request.redirect('/shop')
        
        # Get delivery methods
        delivery_methods = [
            ('standard', 'Standard Delivery (3-5 days) - Free'),
            ('express', 'Express Delivery (1-2 days) - $10'),
            ('pickup', 'Store Pickup - Free')
        ]
        
        values = {
            'order': order,
            'delivery_methods': delivery_methods,
            'countries': request.env['res.country'].search([]),
        }
        
        return request.render('fashion_ecommerce.checkout_page', values)
    
    @http.route(['/shop/confirm_order'], type='http', auth="public", methods=["POST"], website=True, csrf=False)
    def confirm_order(self, **post):
        """Process order confirmation"""
        order = request.website.sale_get_order()
        
        if not order:
            return request.redirect('/shop')
        
        # Update delivery method
        if post.get('delivery_method'):
            order.delivery_method = post.get('delivery_method')
        
        # Update customer information
        if post.get('customer_type'):
            order.customer_type = post.get('customer_type')
        
        # Confirm the order
        try:
            order.action_confirm()
            
            # Create invoice for B2C orders
            if order.customer_type == 'b2c':
                invoices = order._create_invoices()
                if invoices:
                    invoices.action_post()
            
            return request.render('fashion_ecommerce.order_confirmation', {
                'order': order
            })
            
        except Exception as e:
            return request.render('fashion_ecommerce.order_error', {
                'error': str(e),
                'order': order
            })
    
    @http.route(['/shop/track/<string:tracking_number>'], type='http', auth="public", website=True)
    def track_order(self, tracking_number, **kw):
        """Order tracking page"""
        order = request.env['sale.order'].sudo().search([
            ('tracking_number', '=', tracking_number)
        ], limit=1)
        
        if not order:
            return request.render('fashion_ecommerce.tracking_not_found', {
                'tracking_number': tracking_number
            })
        
        return request.render('fashion_ecommerce.order_tracking', {
            'order': order,
            'tracking_number': tracking_number
        })
    
    @http.route(['/shop/b2b'], type='http', auth="user", website=True)
    def b2b_portal(self, **kw):
        """B2B customer portal"""
        partner = request.env.user.partner_id
        
        # Get B2B orders
        orders = request.env['sale.order'].search([
            ('partner_id', '=', partner.id),
            ('customer_type', '=', 'b2b')
        ], order='date_order desc', limit=10)
        
        # Get B2B products with special pricing
        products = request.env['product.template'].search([
            ('b2b_price', '>', 0),
            ('target_audience', '!=', False)
        ])
        
        return request.render('fashion_ecommerce.b2b_portal', {
            'partner': partner,
            'orders': orders,
            'products': products
        })
