from odoo import fields, models

class LeaveType(models.Model):
    _name = 'leave.type'
    _description = 'Leave Type'

    name = fields.Char(string='Leave Type', required=True)