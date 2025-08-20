
from odoo import models, fields

class StockAlertWizard(models.TransientModel):
    _name = 'stock.alert.wizard'
    _description = 'Stock Alert Wizard'

    product_id = fields.Many2one('product.product', string="Product", readonly=True)
    qty_available = fields.Float("On Hand", readonly=True)
    reorder_min_qty = fields.Float("Minimum Required", readonly=True)
