from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_get_last_price(self):
        self.ensure_one()
        
        if not self.product_id:
            raise UserError(_("Please select a product first."))
        
        if not self.order_id.partner_id:
            raise UserError(_("Please select a customer first."))
        
        product_tmpl_id = self.product_id.product_tmpl_id.id
        partner_id = self.order_id.partner_id.id
        
        if self.order_id.state != 'draft':
            raise UserError(_("You can only update prices in draft orders!"))
        else:
            domain = [
                ('product_tmpl_id', '=', product_tmpl_id),
                ('partner_id', '=', partner_id),
                ('state', 'in', ['sale', 'done']),
            ]
            
            last_sale = self.env['sale.report'].search(
                domain,
                order='order_reference desc',  
                limit=1 
            )
            
            if last_sale:
                self.write({'price_unit': last_sale.price_unit})
            else:
                raise UserError(_("This product has not been sold to this customer before!!!"))
            return True