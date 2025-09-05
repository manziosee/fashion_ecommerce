from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_type = fields.Selection([
        ('b2c', 'B2C'),
        ('b2b', 'B2B')
    ], string="Customer Type", default='b2c')
    
    # eCommerce Integration
    website_order = fields.Boolean(string="Website Order", default=False)
    delivery_method = fields.Selection([
        ('standard', 'Standard Delivery'),
        ('express', 'Express Delivery'),
        ('pickup', 'Store Pickup')
    ], string="Delivery Method", default='standard')
    
    delivery_date = fields.Datetime(string="Expected Delivery Date")
    tracking_number = fields.Char(string="Tracking Number")
    
    # B2B Features
    payment_terms = fields.Selection([
        ('immediate', 'Immediate Payment'),
        ('15_days', '15 Days'),
        ('30_days', '30 Days'),
        ('60_days', '60 Days')
    ], string="Payment Terms", default='immediate')
    
    @api.onchange('customer_type')
    def _onchange_customer_type(self):
        """Apply B2B pricing and terms when customer type changes"""
        if self.customer_type == 'b2b':
            self.payment_terms = '30_days'
            # Apply B2B pricing to order lines
            for line in self.order_line:
                if line.product_id.b2b_price > 0:
                    line.price_unit = line.product_id.b2b_price
        else:
            self.payment_terms = 'immediate'
            # Revert to standard pricing
            for line in self.order_line:
                line.price_unit = line.product_id.list_price
    
    def action_confirm(self):
        """Override to add custom logic for fashion orders"""
        # Check stock availability before confirming
        for line in self.order_line:
            if line.product_id.qty_available < line.product_uom_qty:
                raise UserError(f"Insufficient stock for {line.product_id.name}. Available: {line.product_id.qty_available}, Required: {line.product_uom_qty}")
        
        result = super(SaleOrder, self).action_confirm()
        
        # Auto-create invoice for B2C website orders
        if self.customer_type == 'b2c' and self.website_order:
            self._create_invoices()
            
        return result
    
    def action_ship_order(self):
        """Action to mark order as shipped and generate tracking"""
        if not self.tracking_number:
            self.tracking_number = f"TRACK-{self.name}-{fields.Datetime.now().strftime('%Y%m%d')}"
        
        # Update delivery status
        self.delivery_date = fields.Datetime.now()
        
        # Send notification email to customer
        template = self.env.ref('fashion_ecommerce.email_template_order_shipped', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
