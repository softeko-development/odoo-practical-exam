from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LeaveRequest(models.Model):
    _name = 'leave.request'
    _description = 'Leave Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', 
        required=True, default=lambda self: self.env.user.employee_id)
    leave_type_id = fields.Many2one('leave.type', string='Leave Type', required=True)
    date_from = fields.Date(string='From Date', required=True)
    date_to = fields.Date(string='To Date', required=True)
    reason = fields.Text(string='Reason')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft', string='Status', tracking=True)
    manager_comments = fields.Text(string='Manager Comments')
    manager_id = fields.Many2one(
        'hr.employee', string='Manager', 
        compute='_compute_manager_id', store=True)

    @api.depends('employee_id')
    def _compute_manager_id(self):
        for record in self:
            record.manager_id = record.employee_id.parent_id

    def action_submit(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Request must be in Draft state to submit.'))
        self.state = 'submitted'
        self.message_post(body=_('Leave request submitted by %s') % self.employee_id.name)

    def action_approve(self):
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Request must be in Submitted state to approve.'))
        self.state = 'approved'
        self.message_post(body=_('Leave request approved by %s') % self.env.user.name)
        
        # Notify HR group
        hr_group = self.env.ref('leave_approval_notify_hr.group_leave_hr')
        hr_users = hr_group.users
        if hr_users:
            # Create activity for HR users
            for user in hr_users:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary='New Approved Leave Request',
                    note=f'Leave request from {self.employee_id.name} has been approved.',
                    user_id=user.id
                )
            
            # Send email notification
            template = self.env.ref('leave_approval_notify_hr.email_template_leave_approved')
            template.send_mail(self.id, force_send=True)

    def action_reject(self):
        self.ensure_one()
        if self.state != 'submitted':
            raise UserError(_('Request must be in Submitted state to reject.'))
        self.state = 'rejected'
        self.message_post(body=_('Leave request rejected by %s') % self.env.user.name)

    def action_convert_to_leave(self):
        self.ensure_one()
        if self.state != 'approved':
            raise UserError(_('Only approved requests can be converted to official leave.'))
        
        # Create hr.leave record
        leave = self.env['hr.leave'].create({
            'employee_id': self.employee_id.id,
            'holiday_status_id': self.env['hr.leave.type'].search([('name', '=', self.leave_type_id.name)], limit=1).id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'request_date_from': self.date_from,
            'request_date_to': self.date_to,
            'name': self.reason or 'Leave Request',
        })
        self.message_post(body=_('Converted to official leave record: %s') % leave.display_name)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'form',
            'res_id': leave.id,
            'target': 'current',
        }