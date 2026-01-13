from odoo import models, fields, api
from datetime import date


class TOUnavailedLeaves(models.Model):
    _inherit = 'hr.leave'

    @api.onchange('employee_id')
    def get_total_unused_leave_days(self):
        today = date.today()

        # if not (today.month == 7 and today.day == 1):
        #     return

        # fiscal_start = date(today.year - 1, 7, 1)
        # fiscal_end = date(today.year, 6, 30)
        fiscal_start = date(2024, 7, 1)
        fiscal_end = date(2025, 6, 30)

        employees = self.env['hr.employee'].search([])

        for emp in employees:
            allocations = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('date_from', '>=', fiscal_start),
                ('date_to', '<=', fiscal_end),
            ])
            total_allocated = sum(allocations.mapped('number_of_days_display'))

            used = self.env['hr.leave'].search([
                ('employee_id', '=', emp.id),
                ('state', '=', 'validate'),
                ('request_date_from', '>=', fiscal_start),
                ('request_date_to', '<=', fiscal_end),
            ])
            total_used = sum(used.mapped('number_of_days'))

            unused = total_allocated - total_used
            print(unused)

            sick_type = self.env['hr.leave.type'].search([('name', '=', 'Sick Time Off')], limit=1)


            # if unused > 0:
            #     self.env['hr.leave'].create({
            #         'name': f'Converted Unused Leave to Sick - FY {fiscal_end.year}',
            #         'employee_id': emp.id,
            #         'holiday_status_id': sick_type.id,
            #         'request_date_from': today,
            #         'request_date_to': today,
            #         'number_of_days': unused,
            #         'state': 'confirm',
            #         'notes': 'Auto-converted unused annual leave to sick time off. CEO approval required.',
            #     })
