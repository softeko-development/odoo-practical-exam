from odoo import models, fields, api
import base64
import csv
from io import StringIO


class MassLeaveAllocationWizard(models.TransientModel):
    _name = 'mass.leave.allocation.wizard'
    _description = 'Mass Leave Allocation Wizard'

    leave_type_id = fields.Many2one('hr.leave.type', string='Leave Type', required=True)
    number_of_days = fields.Float(string='Number of Days', required=True)
    allocation_mode = fields.Selection([
        ('all', 'All Employees'),
        ('by_department', 'By Department'),
        ('by_job', 'By Job')
    ], string='Allocation Mode', required=True)
    department_id = fields.Many2one('hr.department', string='Department')
    job_id = fields.Many2one('hr.job', string='Job')
    allocation_reason = fields.Text(string='Reason')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    allocation_log_ids = fields.One2many('mass.leave.allocation.log', 'wizard_id', string='Logs')

    def action_preview(self):
        domain = []
        if self.allocation_mode == 'by_department' and self.department_id:
            domain.append(('department_id', '=', self.department_id.id))
        elif self.allocation_mode == 'by_job' and self.job_id:
            domain.append(('job_id', '=', self.job_id.id))
        employees = self.env['hr.employee'].search(domain) if domain else self.env['hr.employee'].search([])
        self.employee_ids = [(6, 0, employees.ids)]
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'Preview Updated', 'message': f'{len(employees)} employees found', 'type': 'success'}
        }

    def action_allocate(self):
        if not self.employee_ids:
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'No Employees Selected', 'type': 'danger'}}

        leave_model = self.env['hr.leave.allocation']  # ✅ Correct model
        log_entries = []

        for emp in self.employee_ids:
            leave_allocation = leave_model.create({
                'name': self.allocation_reason or 'Bulk Allocation',
                'holiday_status_id': self.leave_type_id.id,
                'employee_id': emp.id,
                'number_of_days': self.number_of_days,
                'allocation_type': 'regular',  # ✅ Valid for hr.leave.allocation
                'state': 'confirm',
            })

            # Approve allocation to make it effective
            leave_allocation.action_approve()

            log_entries.append((0, 0, {'employee_id': emp.id, 'leave_id': leave_allocation.id}))

        self.sudo().allocation_log_ids = log_entries

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {'title': 'Success', 'message': f'Leaves allocated to {len(self.employee_ids)} employees', 'type': 'success'}
        }

    def action_export_csv(self):
        if not self.allocation_log_ids:
            return {'type': 'ir.actions.client', 'tag': 'display_notification',
                    'params': {'title': 'No Logs', 'message': 'No data to export', 'type': 'warning'}}

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Employee', 'Leave Type', 'Days'])
        for log in self.allocation_log_ids:
            writer.writerow([log.employee_id.name, log.leave_id.holiday_status_id.name, log.leave_id.number_of_days])
        csv_data = output.getvalue()
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': 'leave_allocation_report.csv',
            'type': 'binary',
            'datas': base64.b64encode(csv_data.encode()).decode(),
            'mimetype': 'text/csv',
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'new',
        }




class MassLeaveAllocationLog(models.Model):
    _name = 'mass.leave.allocation.log'
    _description = 'Mass Leave Allocation Log'

    active = fields.Boolean(default=True)  # ✅ This line is very important!

    leave_id = fields.Many2one('hr.leave', string='Leave')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    # add your other fields if needed


    def unlink(self):
        # Archive instead of delete to avoid validation errors
        self.write({'active': False})
        return True