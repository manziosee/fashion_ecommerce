from odoo import http
from odoo.http import request

class FashionWebsite(http.Controller):

    @http.route('/', type='http', auth="public", website=True)
    def homepage(self, **kw):
        products = request.env['product.template'].search([])
        return request.render("fashion_ecommerce.homepage", {'products': products})

    @http.route('/shop', type='http', auth="public", website=True)
    def shop(self, target_audience=None, **kw):
        domain = []
        if target_audience:
            domain = [('target_audience', '=', target_audience)]
        products = request.env['product.template'].search(domain)
        return request.render("fashion_ecommerce.shop_page", {'products': products, 'audience': target_audience})
