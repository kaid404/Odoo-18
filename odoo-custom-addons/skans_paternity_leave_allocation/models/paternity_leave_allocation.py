from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import ValidationError


class PaternityAllocations(models.Model):
    _inherit = 'hr.leave'

    def paternity_leave_allocation(self):
        for rec in self:
            if rec.holiday_status_id.name == 'Paternity Leave':
                if not rec.employee_id or not rec.employee_id.contract_id or not rec.employee_id.contract_id.date_start:
                    raise ValidationError(
                        "Paternity Leave can't be requested by employees without an active contract or a start date."
                    )

                existing_leaves = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.name', '=', 'Paternity Leave'),
                    ('id', '!=', rec.id),
                    ('state', 'in', ['validate', 'validate1'])
                ])

                days_taken = sum(existing_leaves.mapped('number_of_days'))
                total_days_with_current = days_taken + rec.number_of_days
                if total_days_with_current > 20:
                    raise ValidationError(
                        "Paternity Leave can't be taken more than two times in total service."
                    )
                current_year = rec.date_from.year
                yearly_leaves = existing_leaves.filtered(lambda l: l.date_from.year == current_year)
                days_taken_year = sum(yearly_leaves.mapped('number_of_days'))
                total_year_days = sum(yearly_leaves.mapped('number_of_days')) + rec.number_of_days
                if total_year_days > 10:
                    raise ValidationError(
                        f"You have already taken {days_taken_year} days this year and are requesting "
                        f"{rec.number_of_days} more. Paternity Leave cannot exceed 10 days in a calendar year."
                    )
   

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.paternity_leave_allocation()
        return record

    def write(self, vals):
        res = super().write(vals)
        self.paternity_leave_allocation()
        return res



