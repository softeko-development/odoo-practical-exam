from odoo import models,_
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_mass_confirm(self):
        """Mass confirm selected quotations"""
        # Check for orders in 'sale' state
        done_orders = self.filtered(lambda o: o.state == 'sale')
        if done_orders:
            raise UserError(_(
                "The following orders are already confirmed:\n%s"
            ) % '\n'.join(done_orders.mapped('name')))
        #filter qoutation   
        draft_orders = self.filtered(lambda o: o.state in ['draft', 'sent'])
        draft_orders.action_confirm()
        return True