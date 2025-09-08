from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)

class FashionEcommerce(WebsiteSale):
    
    def _validate_product_id(self, product_id):
        """Validate product ID input"""
        try:
            product_id = int(product_id)
            if product_id <= 0:
                raise ValidationError("Invalid product ID")
            return product_id
        except (ValueError, TypeError):
            raise ValidationError("Product ID must be a valid integer")
    
    def _validate_quantity(self, qty):
        """Validate quantity input"""
        try:
            qty = float(qty)
            if qty < 0:
                raise ValidationError("Quantity cannot be negative")
            return qty
        except (ValueError, TypeError):
            raise ValidationError("Quantity must be a valid number")
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=["POST"], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Enhanced cart update with stock validation"""
        try:
            # Validate inputs
            product_id = self._validate_product_id(product_id)
            add_qty = self._validate_quantity(add_qty)
            
            product = request.env['product.product'].browse(product_id)
            if not product.exists():
                raise ValidationError("Product not found")
            
            # Check stock availability
            if product.qty_available < add_qty:
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
                order.customer_type = 'b2c'
                
            return result
            
        except ValidationError as e:
            _logger.warning(f"Cart update validation error: {str(e)}")
            return request.render('fashion_ecommerce.validation_error', {'error': str(e)})
        except Exception as e:
            _logger.error(f"Unexpected error in cart update: {str(e)}")
            return request.render('fashion_ecommerce.general_error', {'error': 'An unexpected error occurred'})
    
    def _get_delivery_methods(self):
        """Get delivery methods from system parameters"""
        return [
            ('standard', 'Standard Delivery (3-5 days) - Free'),
            ('express', 'Express Delivery (1-2 days) - $10'),
            ('pickup', 'Store Pickup - Free')
        ]
    
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        """Enhanced checkout with delivery options"""
        try:
            order = request.website.sale_get_order()
            
            if not order or not order.order_line:
                return request.redirect('/shop')
            
            values = {
                'order': order,
                'delivery_methods': self._get_delivery_methods(),
                'countries': request.env['res.country'].search([], limit=250),
            }
            
            return request.render('fashion_ecommerce.checkout_page', values)
            
        except Exception as e:
            _logger.error(f"Checkout error: {str(e)}")
            return request.redirect('/shop')
    
    def _validate_delivery_method(self, method):
        """Validate delivery method"""
        valid_methods = [m[0] for m in self._get_delivery_methods()]
        if method not in valid_methods:
            raise ValidationError(f"Invalid delivery method: {method}")
        return method
    
    @http.route(['/shop/confirm_order'], type='http', auth="public", methods=["POST"], website=True, csrf=False)
    def confirm_order(self, **post):
        """Process order confirmation"""
        try:
            order = request.website.sale_get_order()
            
            if not order:
                return request.redirect('/shop')
            
            # Validate and update delivery method
            if post.get('delivery_method'):
                delivery_method = self._validate_delivery_method(post.get('delivery_method'))
                order.delivery_method = delivery_method
            
            # Update customer information
            if post.get('customer_type') in ['b2c', 'b2b']:
                order.customer_type = post.get('customer_type')
            
            # Confirm the order
            order.action_confirm()
            
            # Create invoice for B2C orders
            if order.customer_type == 'b2c':
                try:
                    invoices = order._create_invoices()
                    if invoices:
                        invoices.action_post()
                except Exception as invoice_error:
                    _logger.warning(f"Invoice creation failed: {str(invoice_error)}")
            
            return request.render('fashion_ecommerce.order_confirmation', {
                'order': order
            })
            
        except ValidationError as e:
            _logger.warning(f"Order confirmation validation error: {str(e)}")
            return request.render('fashion_ecommerce.validation_error', {
                'error': str(e),
                'order': order
            })
        except UserError as e:
            _logger.warning(f"Order confirmation user error: {str(e)}")
            return request.render('fashion_ecommerce.order_error', {
                'error': str(e),
                'order': order
            })
        except Exception as e:
            _logger.error(f"Unexpected error in order confirmation: {str(e)}")
            return request.render('fashion_ecommerce.order_error', {
                'error': 'An unexpected error occurred while processing your order',
                'order': order
            })
    
    def _validate_tracking_number(self, tracking_number):
        """Validate tracking number format"""
        if not tracking_number or len(tracking_number.strip()) < 5:
            raise ValidationError("Invalid tracking number format")
        return tracking_number.strip()
    
    @http.route(['/shop/track/<string:tracking_number>'], type='http', auth="public", website=True)
    def track_order(self, tracking_number, **kw):
        """Order tracking page"""
        try:
            tracking_number = self._validate_tracking_number(tracking_number)
            
            # Use regular search instead of sudo for security
            order = request.env['sale.order'].search([
                ('tracking_number', '=', tracking_number),
                ('website_order', '=', True)  # Only website orders can be tracked publicly
            ], limit=1)
            
            if not order:
                return request.render('fashion_ecommerce.tracking_not_found', {
                    'tracking_number': tracking_number
                })
            
            return request.render('fashion_ecommerce.order_tracking', {
                'order': order,
                'tracking_number': tracking_number
            })
            
        except ValidationError as e:
            _logger.warning(f"Tracking validation error: {str(e)}")
            return request.render('fashion_ecommerce.tracking_not_found', {
                'tracking_number': tracking_number,
                'error': str(e)
            })
        except Exception as e:
            _logger.error(f"Tracking error: {str(e)}")
            return request.render('fashion_ecommerce.tracking_not_found', {
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
