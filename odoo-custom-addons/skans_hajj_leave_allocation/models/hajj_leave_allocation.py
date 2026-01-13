from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import ValidationError


class HajjUmrahAllocations(models.Model):
    _inherit = 'hr.leave'

    def hajj_umrah_leave_allocation(self):
        for rec in self:
            if rec.holiday_status_id.name == 'Hajj Leave':
                if not rec.employee_id or not rec.employee_id.contract_id or not rec.employee_id.contract_id.date_start:
                    raise ValidationError(
                        "Hajj leave can't be requested by employees without an active contract or a start date."
                    )
                contract = rec.employee_id.contract_id
                contract_start_date = contract.date_start
                job_days = (datetime.today().date() - contract_start_date).days

                if job_days <= 730:
                    raise ValidationError(
                        "Employees must complete at least two year of service before requesting Hajj Leave."
                    )

                existing_leaves = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.name', '=', 'Hajj Leave'),
                    ('id', '!=', rec.id),
                    ('state', 'in', ['validate', 'validate1'])
                ])

                total_days_taken = sum(existing_leaves.mapped('number_of_days'))
                if total_days_taken > 40:
                    raise ValidationError("You can only take Hajj leave once during your service period.")

                total_with_current = total_days_taken + rec.number_of_days

                if total_with_current > 40:
                    raise ValidationError(
                        f"Hajj leave total can't exceed 40 days in total.")

   

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.hajj_umrah_leave_allocation()
        return record

    def write(self, vals):
        res = super().write(vals)
        self.hajj_umrah_leave_allocation()
        return res



