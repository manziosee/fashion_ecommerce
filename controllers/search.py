from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class FashionSearch(http.Controller):
    
    @http.route('/shop/search', type='http', auth="public", website=True)
    def product_search(self, search=None, category=None, min_price=None, max_price=None, 
                      brand=None, color=None, size=None, rating=None, page=1, **kw):
        """Advanced product search with multiple filters"""
        try:
            page = max(1, int(page))
            limit = 20
            offset = (page - 1) * limit
            
            # Build search domain
            domain = [
                ('website_published', '=', True),
                ('sale_ok', '=', True),
                ('target_audience', '!=', False)
            ]
            
            # Text search
            if search:
                domain.extend([
                    '|', '|', '|',
                    ('name', 'ilike', search),
                    ('brand', 'ilike', search),
                    ('description', 'ilike', search),
                    ('description_sale', 'ilike', search)
                ])
            
            # Category filter
            if category and category in ['men', 'women', 'children']:
                domain.append(('target_audience', '=', category))
            
            # Price range filter
            if min_price:
                try:
                    domain.append(('list_price', '>=', float(min_price)))
                except ValueError:
                    pass
            
            if max_price:
                try:
                    domain.append(('list_price', '<=', float(max_price)))
                except ValueError:
                    pass
            
            # Brand filter
            if brand:
                domain.append(('brand', 'ilike', brand))
            
            # Color filter
            if color:
                domain.append(('color', 'ilike', color))
            
            # Size filter
            if size and size in ['xs', 's', 'm', 'l', 'xl', 'xxl', 'xxxl']:
                domain.append(('clothing_size', '=', size))
            
            # Get products
            products = request.env['product.template'].search(domain, limit=limit, offset=offset, order='name')
            total_count = request.env['product.template'].search_count(domain)
            
            # Get filter options for sidebar
            all_products = request.env['product.template'].search([
                ('website_published', '=', True),
                ('sale_ok', '=', True),
                ('target_audience', '!=', False)
            ])
            
            brands = sorted(list(set(all_products.mapped('brand'))))
            colors = sorted(list(set(all_products.mapped('color'))))
            
            # Price range
            prices = all_products.mapped('list_price')
            price_range = {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 1000
            }
            
            values = {
                'products': products,
                'search_term': search or '',
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'brand': brand,
                'color': color,
                'size': size,
                'rating': rating,
                'brands': [b for b in brands if b],
                'colors': [c for c in colors if c],
                'price_range': price_range,
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'total_products': total_count
            }
            
            return request.render('fashion_ecommerce.search_results', values)
            
        except Exception as e:
            _logger.error(f"Search error: {str(e)}")
            return request.redirect('/shop')
    
    @http.route('/shop/autocomplete', type='json', auth="public", website=True)
    def autocomplete_search(self, term):
        """Autocomplete search suggestions"""
        try:
            if not term or len(term) < 2:
                return []
            
            # Search in product names and brands
            products = request.env['product.template'].search([
                ('website_published', '=', True),
                ('sale_ok', '=', True),
                ('target_audience', '!=', False),
                '|',
                ('name', 'ilike', term),
                ('brand', 'ilike', term)
            ], limit=10)
            
            suggestions = []
            for product in products:
                suggestions.append({
                    'id': product.id,
                    'name': product.name,
                    'brand': product.brand or '',
                    'price': product.list_price,
                    'image': f'/web/image/product.template/{product.id}/image_256'
                })
            
            return suggestions
            
        except Exception as e:
            _logger.error(f"Autocomplete error: {str(e)}")
            return []