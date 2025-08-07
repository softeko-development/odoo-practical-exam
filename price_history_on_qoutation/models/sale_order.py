from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def action_view_sale_report(self):
        self.ensure_one()
        
        if not self.product_id:
            raise UserError(_("Please select a product first."))
        
        if not self.order_id.partner_id:
            raise UserError(_("Please select a customer first."))
        
        
        product_tmpl_id = self.product_id.product_tmpl_id.id
        partner_id = self.order_id.partner_id.id
        
        
        domain = [
            ('product_tmpl_id', '=', product_tmpl_id),
            ('partner_id', '=', partner_id),
            ('state', 'in', ['sale', 'done']),
        ]
        
        
        return {
            'name': _('Price History: %s') % self.product_id.display_name,
            'type': 'ir.actions.act_window',
            'res_model': 'sale.report',
            'view_mode': 'list',
            'views': [
                (False, 'list'),
                (False, 'pivot'),
                (False, 'graph'),
            ],
            'domain': domain,
            'target': 'new',
        }