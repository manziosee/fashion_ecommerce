# -*- coding: utf-8 -*-
{
    'name': 'Fashion Ecommerce',
    'version': '17.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Ecommerce + inventory with audience filters',
    'description': (
        'Adds target audience on products (Men/Women/Children), '
        'customer type on sales (B2C/B2B), a custom website landing page, '
        'and /shop filtering by URL parameter without inheriting QWeb templates.'
    ),
    'author': 'Manzi osee',
    'license': 'LGPL-3',
    
    # Dependencies for the module
    'depends': [
    'base', 'product', 'sale_management', 'stock', 'account', 'website', 'website_sale'
],

    # XML/CSV data files
    'data': [
        'security/ir.model.access.csv',
        'data/product_categories.xml',
        'data/demo_data.xml',
        'data/website_configuration.xml',
        'views/product_views.xml',
        'views/sale_order_views.xml',
        'views/ecommerce_templates.xml',
        'views/website_templates.xml',
        'views/website_pages.xml',
    ],

    # Frontend assets (CSS/JS)
    'assets': {
        'web.assets_frontend': [
            'fashion_ecommerce/static/src/css/fashion.css',
        ],
    },

    'application': True,
    'installable': True,
}
