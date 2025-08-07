# -*- coding: utf-8 -*-
from odoo import models, api

class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    @api.constrains('date_from', 'date_to', 'employee_id')
    def _check_date(self):
        # Skip overlap check for leaves created by alternative holiday requests
        if self.env.context.get('bypass_overlap_check'):
            return
        # Call the original validation logic for other cases
        super(HolidaysRequest, self)._check_date()