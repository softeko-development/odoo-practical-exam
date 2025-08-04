from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_mass_confirm(self):
        """Mass confirm selected quotations"""
        draft_orders = self.filtered(lambda o: o.state in ['draft', 'sent'])
        draft_orders.action_confirm()
        return True