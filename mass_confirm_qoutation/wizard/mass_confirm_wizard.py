from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MassConfirmWizard(models.TransientModel):
    _name = 'mass.confirm.wizard'
    _description = 'Mass Confirm Quotations Wizard'

    customer_id = fields.Many2one('res.partner', string='Customer')
    user_id = fields.Many2one('res.users', string='Salesperson')
    date_from = fields.Date(string='From Date')
    date_to = fields.Date(string='To Date')
    only_in_stock = fields.Boolean(string='Only Quotations with Products in Stock')
    send_email = fields.Boolean(string='Send Confirmation Email to Customers')
    quotation_ids = fields.Many2many(
        'sale.order',
        string='Quotations to Confirm',
        compute='_compute_quotation_ids'
    )
    quotation_count = fields.Integer(
        string='Number of Quotations',
        compute='_compute_quotation_ids'
    )

    @api.depends('customer_id', 'user_id', 'date_from', 'date_to', 'only_in_stock')
    def _compute_quotation_ids(self):
        for wizard in self:
            domain = [('state', '=', 'draft')]
            
            if wizard.customer_id:
                domain.append(('partner_id', '=', wizard.customer_id.id))
            if wizard.user_id:
                domain.append(('user_id', '=', wizard.user_id.id))
            if wizard.date_from:
                domain.append(('date_order', '>=', wizard.date_from))
            if wizard.date_to:
                domain.append(('date_order', '<=', wizard.date_to))
            
            quotations = self.env['sale.order'].search(domain)
            
            if wizard.only_in_stock:
                quotations = quotations.filtered(
                    lambda q: all(line.product_id.type != 'product' or 
                                line.product_id.virtual_available >= line.product_uom_qty
                                for line in q.order_line)
                )
            
            wizard.quotation_ids = [(6, 0, quotations.ids)]
            wizard.quotation_count = len(quotations)

    def action_confirm(self):
        """Confirm all selected quotations"""
        if not self.quotation_ids:
            raise UserError(_("No quotations selected for confirmation!"))
        
        success = self.env['sale.order']
        failed = self.env['sale.order']
        template = self.env.ref('sale.email_template_edi_sale', raise_if_not_found=False)
        
        for quotation in self.quotation_ids:
            try:
                quotation.action_confirm()
                quotation.message_post(
                    body=_("Quotation confirmed via Mass Confirm Wizard")
                )
                
                if self.send_email and template:
                    template.send_mail(quotation.id, force_send=True)
                
                success |= quotation
            except Exception as e:
                failed |= quotation
        
        message = _("""
            <b>Confirmation Summary:</b><br/>
            • Successfully confirmed: %(success_count)d<br/>
            • Failed: %(failed_count)d
        """) % {
            'success_count': len(success),
            'failed_count': len(failed),
        }
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': True,
            }
        }

    def action_cancel(self):
        """Cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}