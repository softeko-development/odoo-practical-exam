# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class AlternativeHolidayRequest(models.Model):
    _name = 'alternative.holiday.request'
    _description = 'Alternative Holiday Request'
    _order = 'worked_date desc'
    _inherit = ['mail.thread']

    # Many2one to hr.employee (auto set to current user’s employee)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        required=True, tracking = True
    )

    worked_date = fields.Date(string='Worked Date', required=True, tracking=True)

    day_type = fields.Selection([
        ('weekend', 'Weekend'),
        ('public_holiday', 'Public Holiday'),
    ], string='Day Type', required=True, tracking=True)

    reason = fields.Text(string='Reason', tracking =True)

    requested_leave_date = fields.Date(string='Requested Leave Date', required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], string='Status', default='draft', tracking=True)

    manager_comments = fields.Text(string='Manager Comments', groups="hr.group_hr_manager")

    # Auto fill worked_date must be weekend/holiday is done later with constraint
    @api.constrains('worked_date')
    def _check_worked_date(self):
        for record in self:
            if record.worked_date and record.worked_date > fields.Date.today():
                raise ValidationError("Worked Date cannot be in the future.")
    @api.constrains('requested_leave_date')
    def _check_requested_leave_date(self):
        for record in self:
            if record.requested_leave_date and record.requested_leave_date < fields.Date.today():
                raise ValidationError("Leave request Date cannot be in the past.")

    def action_submit(self):
        for record in self:
            if record.state != 'draft':
                continue
            record.state = 'submitted'
            # Send notification to manager
            record._notify_manager()

    def action_approve(self):
        for record in self:
            if record.state != 'submitted':
                continue
            record.state = 'approved'
            # Auto-create leave allocation
            record._create_leave_allocation()

    def action_reject(self):
        for record in self:
            if record.state != 'submitted':
                continue
            record.state = 'rejected'

    def _create_leave_allocation(self):
        """Create a leave allocation in hr.leave for the approved requested leave date."""
        leave_type = self.env['hr.leave.type'].search([  # Ensure it's a daily leave type
            ('active', '=', True),        # Only active leave types
        ], limit=1)
        if not leave_type:
            raise ValidationError("No valid leave type found. Please configure a daily leave type in Time Off.")
        
        self.env['hr.leave'].with_context(bypass_overlap_check=True).create({
            'name': f"Alternative Holiday for {self.employee_id.name} ({self.worked_date})",
            'holiday_status_id': leave_type.id,
            'employee_id': self.employee_id.id,
            'date_from': self.requested_leave_date,
            'date_to': self.requested_leave_date,
            'number_of_days': 1,
            'state': 'confirm',  # Create in draft state for manual validation
        })


    def _notify_manager(self):
        """Send a notification to the employee's manager with request details."""
        if self.employee_id.parent_id and self.employee_id.parent_id.user_id:
            manager = self.employee_id.parent_id.user_id
            # Prepare detailed message body
            day_type_str = 'Weekend' if self.day_type == 'weekend' else 'Public Holiday'
            message_body = f"""
                <p>New alternative holiday request submitted by <strong>{self.employee_id.name}</strong>.</p>
                <ul>
                    <li><strong>Worked Date:</strong> {self.worked_date}</li>
                    <li><strong>Day Type:</strong> {day_type_str}</li>
                    <li><strong>Requested Leave Date:</strong> {self.requested_leave_date}</li>
                    <li><strong>Reason:</strong> {self.reason}</li>
                </ul>
                <p>Please review in <strong>Alternative Holiday Request > Manager > Requests To Approve</strong>.</p>
            """
            # Post to chatter
            self.message_post(
                body=f"New alternative holiday request submitted by {self.employee_id.name} for {self.requested_leave_date}.",
                partner_ids=[manager.partner_id.id],
                message_type='notification',
                subtype_id=self.env.ref('mail.mt_comment').id
            )
            # Send email
            template = self.env.ref('alternative_holiday.email_template_holiday_request_submission', raise_if_not_found=False)
            if template:
                template.send_mail(self.id, force_send=True, email_values={'recipient_ids': [(4, manager.partner_id.id)]})

    @api.constrains('worked_date', 'day_type')
    def _check_worked_date_type(self):
        """Ensure worked_date is a weekend or public holiday based on day_type."""
        for record in self:
            if record.worked_date:
                weekday = record.worked_date.weekday()
                is_weekend = weekday in (5, 6)  # Saturday or Sunday
                is_public_holiday = False
                # Check if the date is a public holiday
                public_holidays = self.env['resource.calendar.leaves'].search([
                    ('date_from', '<=', record.worked_date),
                    ('date_to', '>=', record.worked_date),
                    ('resource_id', '=', False),  # Global holidays
                ])
                if public_holidays:
                    is_public_holiday = True

                if record.day_type == 'weekend' and not is_weekend:
                    raise ValidationError("Worked Date must be a weekend (Saturday or Sunday) for 'Weekend' type.")
                if record.day_type == 'public_holiday' and not is_public_holiday:
                    raise ValidationError("Worked Date must be a public holiday for 'Public Holiday' type.")