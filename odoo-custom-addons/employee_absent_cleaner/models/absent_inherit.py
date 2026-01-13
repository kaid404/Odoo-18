from odoo import models
import logging
from datetime import datetime, time

_logger = logging.getLogger(__name__)


class EmployeeAttendanceAbsent(models.Model):
    _inherit = 'employee.attendance.absent'


    def delete_absent_entries(self):
        records = self.env['employee.attendance.absent'].sudo().search([])
        for rec in records:
            emp = rec.name
            absent_date = rec.date

            if not (emp and absent_date):
                continue

            start_dt = datetime.combine(absent_date, time(0, 0, 0))
            end_dt = datetime.combine(absent_date, time(23, 59, 59))

            attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', emp.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt),
            ], limit=1)
            _logger.info(f"attttttttttttttttttttttttttttttttttttttttttttttttttttttttendanceeeeeeeeeeeeeeeeeeee{attendance}")

            leave = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('date_from', '<=', absent_date),
                ('date_to', '>=', absent_date),
            ], limit=1)
            _logger.info(f"leaaaaaaaaavvvvvvvvvveeeeeeeeeee{leave}")


            if attendance or leave:
                _logger.info("deleeeeeeeeeeeeeeettttttttttttttttiiiiiiiiiiinnnnnnnnggggggg")
                rec.unlink()