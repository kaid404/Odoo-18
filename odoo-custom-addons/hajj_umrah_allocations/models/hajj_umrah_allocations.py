from odoo import models, fields, api
from datetime import datetime

from odoo.exceptions import ValidationError


class HajjUmrahAllocations(models.Model):
    _inherit = 'hr.leave'

    # @api.constrains('holiday_status_id', 'number_of_days')
    def hajj_umrah_leave_allocation(self):
        for rec in self:
            if rec.holiday_status_id.name == 'Hajj/Umrah Leave':
                if not rec.employee_id or not rec.employee_id.contract_id or not rec.employee_id.contract_id.date_start:
                    raise ValidationError(
                        "Hajj/Umrah leave can't be requested by employees without an active contract or a start date."
                    )
                contract = rec.employee_id.contract_id
                contract_start_date = contract.date_start
                job_days = (datetime.today().date() - contract_start_date).days

                if job_days <= 365:
                    raise ValidationError(
                        "Employees must complete at least one year of service before requesting Hajj/Umrah Leave."
                    )

                existing_leaves = self.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.name', '=', 'Hajj/Umrah Leave'),
                    ('id', '!=', rec.id),
                    ('state', 'in', ['validate', 'validate1'])
                ])

                total_days_taken = sum(existing_leaves.mapped('number_of_days'))
                total_with_current = total_days_taken + rec.number_of_days

                if total_with_current > 15:
                    raise ValidationError(
                        f"Hajj/Umrah leave total can't exceed 15 days in total.")

    # def action_approve(self):
    #     self.hajj_umrah_leave_allocation()
    #     return super().action_approve()

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.hajj_umrah_leave_allocation()
        return record

    def write(self, vals):
        # if 'state' in vals and vals['state'] == 'refuse':
        #     return super().write(vals)

        res = super().write(vals)
        self.hajj_umrah_leave_allocation()
        return res
