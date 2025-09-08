from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class FashionWebsite(http.Controller):
    
    def _get_base_product_domain(self):
        """Get base domain for fashion products"""
        return [
            ('website_published', '=', True), 
            ('sale_ok', '=', True),
            ('target_audience', '!=', False)
        ]
    
    def _get_category_info(self, audience):
        """Get category information for audience"""
        category_info = {
            'men': {
                'title': "Men's Clothing",
                'description': "Discover our premium collection of men's fashion."
            },
            'women': {
                'title': "Women's Clothing", 
                'description': "Elegant and trendy women's clothing collection."
            },
            'children': {
                'title': "Children's Clothing",
                'description': "Fun and comfortable clothing for kids."
            }
        }
        return category_info.get(audience, {'title': 'Fashion', 'description': 'Quality fashion collection'})

    @http.route('/', type='http', auth="public", website=True)
    def homepage(self, **kw):
        try:
            domain = self._get_base_product_domain()
            products = request.env['product.template'].search(domain, limit=8, order='create_date desc')
            return request.render("fashion_ecommerce.homepage", {'products': products})
        except Exception as e:
            _logger.error(f"Homepage error: {str(e)}")
            return request.render("fashion_ecommerce.homepage", {'products': []})

    def _get_audience_products(self, audience, page=1, limit=20):
        """Get products for specific audience with pagination"""
        domain = self._get_base_product_domain()
        domain.append(('target_audience', '=', audience))
        
        offset = (page - 1) * limit
        products = request.env['product.template'].search(domain, limit=limit, offset=offset, order='name')
        total_count = request.env['product.template'].search_count(domain)
        
        return products, total_count
    
    @http.route('/mens-clothing', type='http', auth="public", website=True)
    def mens_clothing(self, page=1, **kw):
        try:
            page = max(1, int(page))
            products, total_count = self._get_audience_products('men', page)
            category_info = self._get_category_info('men')
            
            return request.render("fashion_ecommerce.mens_clothing_page", {
                'products': products,
                'category_title': category_info['title'],
                'category_description': category_info['description'],
                'current_page': page,
                'total_pages': (total_count + 19) // 20
            })
        except (ValueError, TypeError):
            return request.redirect('/mens-clothing')
        except Exception as e:
            _logger.error(f"Men's clothing page error: {str(e)}")
            return request.redirect('/')

    @http.route('/womens-clothing', type='http', auth="public", website=True)
    def womens_clothing(self, page=1, **kw):
        try:
            page = max(1, int(page))
            products, total_count = self._get_audience_products('women', page)
            category_info = self._get_category_info('women')
            
            return request.render("fashion_ecommerce.womens_clothing_page", {
                'products': products,
                'category_title': category_info['title'],
                'category_description': category_info['description'],
                'current_page': page,
                'total_pages': (total_count + 19) // 20
            })
        except (ValueError, TypeError):
            return request.redirect('/womens-clothing')
        except Exception as e:
            _logger.error(f"Women's clothing page error: {str(e)}")
            return request.redirect('/')

    @http.route('/childrens-clothing', type='http', auth="public", website=True)
    def childrens_clothing(self, page=1, **kw):
        try:
            page = max(1, int(page))
            products, total_count = self._get_audience_products('children', page)
            category_info = self._get_category_info('children')
            
            return request.render("fashion_ecommerce.childrens_clothing_page", {
                'products': products,
                'category_title': category_info['title'],
                'category_description': category_info['description'],
                'current_page': page,
                'total_pages': (total_count + 19) // 20
            })
        except (ValueError, TypeError):
            return request.redirect('/childrens-clothing')
        except Exception as e:
            _logger.error(f"Children's clothing page error: {str(e)}")
            return request.redirect('/')

    @http.route('/shop', type='http', auth="public", website=True)
    def shop(self, target_audience=None, brand=None, color=None, size=None, page=1, **kw):
        try:
            page = max(1, int(page))
            limit = 20
            offset = (page - 1) * limit
            
            # Build domain with filters
            domain = self._get_base_product_domain()
            
            # Apply filters
            if target_audience and target_audience in ['men', 'women', 'children']:
                domain.append(('target_audience', '=', target_audience))
            if brand:
                domain.append(('brand', 'ilike', brand))
            if color:
                domain.append(('color', 'ilike', color))
            if size and size in ['xs', 's', 'm', 'l', 'xl', 'xxl', 'xxxl']:
                domain.append(('clothing_size', '=', size))
                
            products = request.env['product.template'].search(domain, limit=limit, offset=offset, order='name')
            total_count = request.env['product.template'].search_count(domain)
            
            # Get filter options
            all_products = request.env['product.template'].search(self._get_base_product_domain())
            brands = list(set(all_products.mapped('brand')))
            colors = list(set(all_products.mapped('color')))
            
            order = request.website.sale_get_order()
            
            return request.render("fashion_ecommerce.shop_page", {
                'products': products,
                'audience': target_audience,
                'brand': brand,
                'color': color,
                'size': size,
                'brands': sorted([b for b in brands if b]),
                'colors': sorted([c for c in colors if c]),
                'current_page': page,
                'total_pages': (total_count + limit - 1) // limit,
                'website_sale_current_pl': order
            })
            
        except (ValueError, TypeError):
            return request.redirect('/shop')
        except Exception as e:
            _logger.error(f"Shop page error: {str(e)}")
            return request.redirect('/')

class FashionWebsiteSale(WebsiteSale):
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=["POST"], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """Override to handle fashion-specific cart updates"""
        try:
            # Validate inputs
            product_id = int(product_id)
            add_qty = float(add_qty)
            
            if product_id <= 0 or add_qty < 0:
                raise ValidationError("Invalid product or quantity")
                
            result = super(FashionWebsiteSale, self).cart_update(product_id, add_qty, set_qty, **kw)
            
            # Redirect to cart page after adding item
            if isinstance(result, dict) and result.get('cart_quantity'):
                return request.redirect('/shop/cart')
            return result
            
        except (ValueError, TypeError, ValidationError) as e:
            _logger.warning(f"Cart update error: {str(e)}")
            return request.redirect('/shop')
        except Exception as e:
            _logger.error(f"Unexpected cart update error: {str(e)}")
            return request.redirect('/shop')
