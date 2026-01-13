from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date
from odoo.tools.translate import _

from odoo.exceptions import UserError


class SpecialApprovalTO(models.Model):
    _inherit = 'hr.leave'


    causal_leave_check = fields.Boolean(string='Special Case')

    special_approval_check = fields.Boolean(string='Check')

    def action_special_approval(self):
        for leave in self:
            if not leave.holiday_status_id:
                raise ValidationError('Time Off type is required.')
            leave.action_validate()

    @api.constrains('number_of_days', 'holiday_status_id', 'causal_leave_check')
    def days_off_casual_leaves(self):
        today = date.today()
        print(self.special_approval_check)

        for leave in self:
            time_offs = self.env['hr.leave'].search([
                ('employee_id', '=', leave.employee_id.id),
                ('request_date_from', '>=', today),
                ('request_date_to', '<=', today),
                ('state', 'in', ['validate1', 'validate']),
                ('id', '!=', leave.id)
            ], limit=10)

            total_days = sum(days.number_of_days for days in time_offs)

            total_days_off = total_days + leave.number_of_days

            leave_type_name = leave.holiday_status_id.name
            employee_type = leave.employee_id.employee_type_2

            if leave.causal_leave_check:
                if leave_type_name == 'Casual Leave':
                    print('casual thing')
                    if employee_type == 'school':
                        print('schoool boy')
                        if total_days_off > 1:
                            leave.special_approval_check = True
                        else:
                            leave.special_approval_check = False

                    elif employee_type == 'college':
                        print('college boy')
                        if total_days_off > 2:
                            leave.special_approval_check = True
                        else:
                            leave.special_approval_check = False
                    else:
                        leave.special_approval_check = False
                # elif leave_type_name != 'Casual Leave':
                else:
                    print('not casual')
                    print(total_days_off)
                    if total_days_off > 2:
                        print('making it true')
                        leave.special_approval_check = True
                        print(leave.special_approval_check)
                    else:
                        leave.special_approval_check = False
            else:
                leave.special_approval_check = False

        print(self.special_approval_check)

    def days_off_approval(self):
        today = date.today()

        today_date = today.replace(day=1)
        for leave in self:
            time_offs = self.env['hr.leave'].search([
                ('employee_id', '=', leave.employee_id.id),
                ('request_date_from', '>=', today_date),
                ('request_date_to', '<', today_date),
                ('state', 'in', ['validate1', 'validate']),
                ('id', '!=', leave.id)
            ])

            total_days = sum(days.number_of_days for days in time_offs)

            total_days_off = total_days + leave.number_of_days

            leave_type_name = leave.holiday_status_id.name
            employee_type = leave.employee_id.employee_type_2

            if leave_type_name == 'Casual Leave':
                if employee_type == 'school':
                    if total_days_off > 1:
                        raise ValidationError(
                            f'School employees can not take more than 1 casual leave at a time')

                    else:
                        pass

                elif employee_type == 'college':
                    if total_days_off > 2:
                        raise ValidationError(
                            f'College employees can not take more than 2 casual leaves at a time')

                else:
                    pass

            else:
                pass

    def day_off_special_approval(self):
        today = date.today()

        start_date = today.replace(day=1)

        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1)
        else:
            end_date = today.replace(month=today.month + 1, day=1)

        for leave in self:
            time_offs = self.env['hr.leave'].search([
                ('employee_id', '=', leave.employee_id.id),
                ('request_date_from', '>=', start_date),
                ('request_date_to', '<', end_date),
                ('state', 'in', ['validate1', 'validate']),
                ('id', '!=', leave.id)
            ])

            total_days = sum(days.number_of_days for days in time_offs)

            total_days_off = total_days + leave.number_of_days

            leave_type_name = leave.holiday_status_id.name
            employee_type = leave.employee_id.employee_type_2

            if leave_type_name != 'Casual Leave':
                if total_days_off > 2:
                    raise ValidationError("You need special approval to request more than 2 days off this month.")
                else:
                    pass
            else:
                pass

    def action_approve(self):
        # self.days_off_casual_leaves()
        self.days_off_approval()
        self.day_off_special_approval()
        return super().action_approve()

    # @api.model
    # def create(self, vals):
    #     record = super(SpecialApprovalTO, self).create(vals)
    #     record.days_off_casual_leaves()
    #     return record
    #
    # def write(self, vals):
    #     res = super(SpecialApprovalTO, self).write(vals)
    #     self.days_off_casual_leaves()
    #     return res


    def action_refuse(self):
        current_employee = self.env.user.employee_id
        if any(holiday.state not in ['confirm', 'validate', 'validate1'] for holiday in self):
            raise UserError(_('Time off request must be confirmed or validated in order to refuse it.'))

        self._notify_manager()
        validated_holidays = self.filtered(lambda hol: hol.state == 'validate1')
        validated_holidays.write({'state': 'refuse', 'first_approver_id': current_employee.id})
        (self - validated_holidays).write({'state': 'refuse', 'second_approver_id': current_employee.id})
        self.mapped('meeting_id').write({'active': False})
        for holiday in self:
            if holiday.employee_id.user_id:
                holiday.message_post(
                    body=_('Your %(leave_type)s planned on %(date)s has been refused',
                           leave_type=holiday.holiday_status_id.display_name, date=holiday.date_from),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.activity_update()
        return True