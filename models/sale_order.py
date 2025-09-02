from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_type = fields.Selection([
        ('b2c', 'B2C'),
        ('b2b', 'B2B')
    ], string="Customer Type")
