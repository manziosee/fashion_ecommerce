from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, AccessError
import logging

_logger = logging.getLogger(__name__)

class FashionWishlistController(http.Controller):
    
    @http.route('/shop/wishlist', type='http', auth="user", website=True)
    def wishlist_page(self, **kw):
        """Display user's wishlist"""
        try:
            partner = request.env.user.partner_id
            wishlist_items = request.env['fashion.wishlist'].search([
                ('partner_id', '=', partner.id)
            ])
            
            return request.render('fashion_ecommerce.wishlist_page', {
                'wishlist_items': wishlist_items,
                'partner': partner
            })
            
        except Exception as e:
            _logger.error(f"Wishlist page error: {str(e)}")
            return request.redirect('/shop')
    
    @http.route('/shop/wishlist/toggle', type='json', auth="user", website=True)
    def toggle_wishlist(self, product_id):
        """Add/remove product from wishlist"""
        try:
            product_id = int(product_id)
            partner_id = request.env.user.partner_id.id
            
            result = request.env['fashion.wishlist'].toggle_wishlist(product_id, partner_id)
            return result
            
        except (ValueError, ValidationError) as e:
            _logger.warning(f"Wishlist toggle error: {str(e)}")
            return {'error': str(e)}
        except Exception as e:
            _logger.error(f"Unexpected wishlist error: {str(e)}")
            return {'error': 'An error occurred'}
    
    @http.route('/shop/wishlist/remove/<int:item_id>', type='http', auth="user", website=True, csrf=False)
    def remove_from_wishlist(self, item_id, **kw):
        """Remove item from wishlist"""
        try:
            wishlist_item = request.env['fashion.wishlist'].browse(item_id)
            if wishlist_item.partner_id.id == request.env.user.partner_id.id:
                wishlist_item.unlink()
            
            return request.redirect('/shop/wishlist')
            
        except Exception as e:
            _logger.error(f"Remove wishlist error: {str(e)}")
            return request.redirect('/shop/wishlist')

class FashionReviewController(http.Controller):
    
    @http.route('/shop/product/<int:product_id>/reviews', type='http', auth="public", website=True)
    def product_reviews(self, product_id, **kw):
        """Display product reviews"""
        try:
            product = request.env['product.template'].browse(product_id)
            if not product.exists():
                return request.redirect('/shop')
            
            reviews = request.env['fashion.product.review'].get_product_reviews(product_id)
            average_rating = request.env['fashion.product.review'].get_average_rating(product_id)
            
            return request.render('fashion_ecommerce.product_reviews', {
                'product': product,
                'reviews': reviews,
                'average_rating': average_rating,
                'total_reviews': len(reviews)
            })
            
        except Exception as e:
            _logger.error(f"Product reviews error: {str(e)}")
            return request.redirect('/shop')
    
    @http.route('/shop/product/<int:product_id>/review/add', type='http', auth="user", website=True)
    def add_review_form(self, product_id, **kw):
        """Display add review form"""
        try:
            product = request.env['product.template'].browse(product_id)
            if not product.exists():
                return request.redirect('/shop')
            
            # Check if user already reviewed this product
            existing_review = request.env['fashion.product.review'].search([
                ('product_id', '=', product_id),
                ('partner_id', '=', request.env.user.partner_id.id)
            ])
            
            return request.render('fashion_ecommerce.add_review_form', {
                'product': product,
                'existing_review': existing_review
            })
            
        except Exception as e:
            _logger.error(f"Add review form error: {str(e)}")
            return request.redirect('/shop')
    
    @http.route('/shop/product/<int:product_id>/review/submit', type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def submit_review(self, product_id, **post):
        """Submit product review"""
        try:
            product = request.env['product.template'].browse(product_id)
            if not product.exists():
                return request.redirect('/shop')
            
            # Validate inputs
            title = post.get('title', '').strip()
            rating = post.get('rating')
            review_text = post.get('review_text', '').strip()
            
            if not title or not rating:
                raise ValidationError("Title and rating are required")
            
            if rating not in ['1', '2', '3', '4', '5']:
                raise ValidationError("Invalid rating")
            
            # Check if user already reviewed this product
            existing_review = request.env['fashion.product.review'].search([
                ('product_id', '=', product_id),
                ('partner_id', '=', request.env.user.partner_id.id)
            ])
            
            if existing_review:
                # Update existing review
                existing_review.write({
                    'title': title,
                    'rating': rating,
                    'review_text': review_text,
                    'state': 'draft'  # Reset to draft for moderation
                })
            else:
                # Create new review
                request.env['fashion.product.review'].create({
                    'title': title,
                    'product_id': product_id,
                    'partner_id': request.env.user.partner_id.id,
                    'rating': rating,
                    'review_text': review_text,
                    'state': 'published'  # Auto-publish for now
                })
            
            return request.redirect(f'/shop/product/{product_id}/reviews')
            
        except ValidationError as e:
            _logger.warning(f"Review submission validation error: {str(e)}")
            return request.render('fashion_ecommerce.review_error', {
                'error': str(e),
                'product_id': product_id
            })
        except Exception as e:
            _logger.error(f"Review submission error: {str(e)}")
            return request.redirect('/shop')