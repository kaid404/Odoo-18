from datetime import datetime, date
from odoo import fields, models, api, _
import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'



    # def _get_accrued_leaves(self, employee, leave_type):
    #     for rec in self:
    #         _logger.info('222222222222222222222222222222222')
    #         """Compute how many leaves employee has earned so far this fiscal/allocation period."""
    #         today = fields.Date.today()
    #         ref_date = rec.date_from or fields.Date.today()
    #         ref_date = fields.Date.to_date(ref_date)
    #         allocation = self.env['hr.leave.allocation'].search([
    #             ('employee_id', '=', employee.id),
    #             ('holiday_status_id', '=', leave_type.id),
    #             ('state', '=', 'validate'),
    #             ('date_from', '<=', ref_date),
    #             ('date_to', '>=', ref_date)
    #         ], limit=1)
    #         _logger.info(f"allocationssssssssssssssssssssss{allocation}")
    #
    #         if not allocation:
    #             return 0.0
    #
    #         total_months = ((allocation.date_to.year - allocation.date_from.year) * 12 +
    #                         allocation.date_to.month - allocation.date_from.month) + 1
    #
    #         months_passed = ((ref_date.year - allocation.date_from.year) * 12 +
    #                          ref_date.month - allocation.date_from.month) + 1
    #         _logger.info(f"Total monthhhhhhhhhhhhhhhhhhhhhhh{total_months}")
    #         _logger.info(f"months passeddddddddddddddddddddddddd{months_passed}")
    #         _logger.info(f"Date frommmmmmmmmmmmmmmmmmmm{allocation.date_from}")
    #         _logger.info(f"Date Tooooooooooooooooooooooo{allocation.date_to}")
    #         _logger.info(f"Date Tooooooooooooooooooooooo{allocation.number_of_days}")
    #         if today < allocation.date_from:
    #             months_passed = 0
    #
    #         # ✅ Allow full if allocation is ending or passed
    #         if ref_date >= allocation.date_to:
    #             accrued = allocation.number_of_days
    #         else:
    #             per_month = allocation.number_of_days / total_months
    #             accrued = per_month * months_passed
    #
    #     return accrued

    def _get_accrued_leaves(self, employee, leave_type):
        """Compute how many leaves employee has earned up to the leave's start date."""
        for rec in self:
            # Use leave start date if available, otherwise fallback to today
            ref_date = rec.date_from or fields.Date.today()
            ref_date = fields.Date.to_date(ref_date)

            _logger.info(f"Calculating accrued leaves as of: {ref_date}")

            allocation = self.env['hr.leave.allocation'].search([
                ('employee_id', '=', employee.id),
                ('holiday_status_id', '=', leave_type.id),
                ('state', '=', 'validate'),
                ('date_from', '<=', ref_date),
                ('date_to', '>=', ref_date)
            ], limit=1)

            _logger.info(f"Allocation found: {allocation}")

            if not allocation:
                return 0.0

            total_months = ((allocation.date_to.year - allocation.date_from.year) * 12 +
                            allocation.date_to.month - allocation.date_from.month) + 1

            months_passed = ((ref_date.year - allocation.date_from.year) * 12 +
                             ref_date.month - allocation.date_from.month) + 1
            _logger.info(f"month passsssssssssssssssss{months_passed}")

            if ref_date < allocation.date_from:
                months_passed = 0

            per_month = allocation.number_of_days / total_months

            # ✅ Allow full if allocation is ending or passed the reference date
            if ref_date >= allocation.date_to:
                accrued = allocation.number_of_days
            else:
                accrued = per_month * months_passed

            _logger.info(f"Total months: {total_months}, Months passed: {months_passed}, Accrued: {accrued}")
            return accrued

    def action_approve(self):
        print('staaaaaaaaaaaaaaaaaaarrrrrrrtttttttttttt')
        for leave in self:
            if leave.holiday_status_id.name in ['Casual Leave','Annual Leave']:
                leave_type = leave.holiday_status_id
                employee = leave.employee_id
                print(leave_type)
                print(employee)

                today = fields.Date.today()
                accrued_leaves = self._get_accrued_leaves(employee, leave_type)
                print(f"accrued_leavesssssssssssssssssssssssssss {accrued_leaves}")
                validated_leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', employee.id),
                    ('holiday_status_id', '=', leave_type.id),
                    ('state', '=', 'validate'),
                    ('id', '!=', leave.id)
                ])
                used_leaves = sum(validated_leaves.mapped('number_of_days'))
                print(f"validated leaveesssssssssssssssssss{validated_leaves}")
                print(f"used leavessssssssssssssssssssss{used_leaves}")
                remaining_usable = accrued_leaves - used_leaves
                print(f"remaining leavesssssssssssssssssssssss{remaining_usable}")

                if leave.number_of_days > remaining_usable:
                    raise ValidationError(_(
                        f"You cannot take {leave.number_of_days:.2f} days. "
                        f"You’ve only accrued {accrued_leaves:.2f} days so far this year "
                        f"and already used {used_leaves:.2f}."
                    ))

        return super(HrLeave, self).action_approve()