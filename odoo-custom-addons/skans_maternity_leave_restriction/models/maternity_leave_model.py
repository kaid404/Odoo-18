from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _check_maternity_leave(self):
        for leave in self:
            if leave.holiday_status_id.name == 'Maternity Leave':
                employee = leave.employee_id

                if employee.gender != 'female':
                    raise ValidationError("Maternity Leave can only be taken by female employees.")

                if not employee.contract_id or not employee.contract_id.date_start:
                    raise ValidationError("Employee does not have a valid contract with a start date.")

                contract = leave.employee_id.contract_id
                contract_start_date = contract.date_start
                job_days = (datetime.today().date() - contract_start_date).days

                if job_days <= 730:
                    raise ValidationError(
                        "Employees must complete at least two year of service before requesting Maternity Leave."
                    )

                previous_leaves = self.search([
                    ('employee_id', '=', employee.id),
                    ('holiday_status_id.name', '=', 'Maternity Leave'),
                    ('id', '!=', leave.id),
                    ('state', 'in', ['validate', 'validate1'])
                ])

                days_taken = sum(previous_leaves.mapped('number_of_days'))
                total_days_with_current = days_taken + leave.number_of_days
                if total_days_with_current > 90:
                    raise ValidationError("Maternity Leave can be taken only twice in total service.")

                current_year = leave.date_from.year
                print(current_year)
                yearly_leaves = previous_leaves.filtered(lambda l: l.date_from.year == current_year)
                days_taken_year = sum(yearly_leaves.mapped('number_of_days'))
                print(days_taken_year)
                total_year_days = sum(yearly_leaves.mapped('number_of_days')) + leave.number_of_days
                if total_year_days > 45:
                    raise ValidationError(
                        f"An employee can take a maximum of 45 days of Maternity Leave in total. "
                        f"Current attempted ({leave.number_of_days}) exceeds the limit."
                        f"Existing Leaves are : {days_taken_year} days."

                    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._check_maternity_leave()
        return record

    def write(self, vals):
        res = super().write(vals)
        self._check_maternity_leave()
        return res
                # total_existing_days = sum(previous_leaves.mapped('number_of_days'))
                # total_days = sum(previous_leaves.mapped('number_of_days')) + leave.number_of_days
                # _logger.info(f"Employee {employee.name} total maternity leave days = {total_days}")

                # if total_days > 45:
                #     raise ValidationError(
                #         f"An employee can take a maximum of 45 days of Maternity Leave in total. "
                #         f"Current attempted ({leave.number_of_days}) exceeds the limit."
                #         f"Existing Leaves are : {total_existing_days} days."
                #
                #     )

# class LeaveAllocation(models.Model):
#     _inherit = 'hr.leave.allocation'
#
#     # @api.constrains('holiday_status_id', 'number_of_days')
#     def _check_maternity_allocation(self):
#         maternity_type_exists = self.env['hr.leave.type'].search_count([('name', '=', 'Maternity Leave')])
#         if not maternity_type_exists:
#             raise ValidationError("The 'Maternity Leave' time off type is not defined. Please create it first.")
#         for record in self:
#             employee = record.employee_id
#             # if record.employee_id.gender != 'female':
#             #     raise ValidationError("Maternity leave can only be allocated to female employees.")
#             if record.holiday_status_id.name == 'Maternity Leave':
#                 if employee and employee.contract_id and employee.contract_id.date_start:
#                     if record.number_of_days > 45:
#                         raise ValidationError("Maternity leave allocation cannot exceed 45 days.")
#
#
#     # def action_approve(self):
#     #     self._check_maternity_allocation()
#     #     return super().action_approve()
#
#     @api.model
#     def create(self, vals):
#         rec = super().create(vals)
#         self._check_maternity_allocation()
#         return rec
#
#
#     def write(self, vals):
#         res = super().write(vals)
#         self._check_maternity_allocation()
#         return res
