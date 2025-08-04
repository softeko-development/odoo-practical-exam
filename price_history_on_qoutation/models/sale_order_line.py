# models/sale_order_line.py

from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    history_line_ids = fields.One2many(
        'sale.order.line.history', 'order_line_id', string='Price History', compute='_compute_price_history', store=False)

    @api.depends('product_id', 'order_id.partner_id')
    def _compute_price_history(self):
        for line in self:
            line.history_line_ids = False
            continue

            domain = [
                ('product_id', '=', line.product_id.id),
                ('order_partner_id', '=', line.order_id.partner_id.id),
                ('order_id.state', 'in', ['sale', 'done']),
                ('id', '!=', line.id)
            ]
            history = self.search(domain, order='create_date desc', limit=10)
            history_data = []
            for h in history:
                history_data.append((0, 0, {
                    'order_date': h.order_id.date_order,
                    'order_name': h.order_id.name,
                    'product_uom_qty': h.product_uom_qty,
                    'price_unit': h.price_unit,
                    'salesperson_id': h.order_id.user_id.id,
                }))
            line.history_line_ids = history_data

class SaleOrderLineHistory(models.TransientModel):
    _name = 'sale.order.line.history'
    _description = 'Product Price History'

    order_line_id = fields.Many2one('sale.order.line')
    order_date = fields.Datetime(string='Order Date')
    order_name = fields.Char(string='Quotation/SO Ref')
    product_uom_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Unit Price')
    salesperson_id = fields.Many2one('res.users', string='Salesperson')
