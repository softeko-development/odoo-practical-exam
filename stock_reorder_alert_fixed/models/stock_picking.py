
from odoo import models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        for move in self.move_ids_without_package:
            product = move.product_id
            reordering_rule = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', product.id)], limit=1)
            if reordering_rule and product.qty_available < reordering_rule.product_min_qty:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Stock Alert'),
                    'res_model': 'stock.alert.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_product_id': product.id,
                        'default_qty_available': product.qty_available,
                        'default_reorder_min_qty': reordering_rule.product_min_qty,
                    }
                }
        return res
