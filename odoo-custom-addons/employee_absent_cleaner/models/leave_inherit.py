from odoo import models
from datetime import timedelta


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def create(self, vals):
        record = super().create(vals)

        date = record.date_from.date()

        absent_record = record.env['employee.attendance.absent'].search([
            ('employee_id', '=', record.employee_id.id),
            ('date', '=', date),
        ])
        if absent_record:
            absent_record.unlink()

        return record
