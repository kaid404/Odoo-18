from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrAdvanceSalary(models.Model):
    _inherit = 'hr.advance.salary'

    special_approval = fields.Boolean(string='Special Approval', default=False, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('line_manager', 'Line Manager'),
        ('hr_approval', 'HR'),
        ('finance_director', 'Finance Director'),
        ('finance__asst_director', 'Finance Assistant Director'),
        ('executive_director', 'Executive Director'),
        ('ceo', 'CEO'),
        ('paid', 'Paid'),
        ('done', 'Done'),
        ('refuse', 'Refuse'),
    ], default="draft", track_visibility='always')

    def action_approve1(self):
        self.write({'state': 'line_manager',
                    # 'approved1_date': datetime.today(),
                    # 'approved1_by': self.env.uid
                    })

    def action_approve2(self):
        self.write({'state': 'finance_director',
                    'approved2_date': datetime.today(),
                    'approved2_by': self.env.uid})

    def action_hr_approve(self):
        self.write({'state': 'hr_approval'
                    })

    def action_executive_director_approve(self):
        self.write({'state': 'executive_director'
                    })

    def action_paid_adv_salary(self):
        res = super().action_paid()
        return res
    # def action_special_approval(self):
    #     self.state = 'special_approve'
    #
    # def action_finance_approval(self):
    #     self.state = 'finance_appr'

    @api.constrains('payment', 'loan_type')
    def _check_loan_type_required(self):
        for rec in self:
            if rec.payment == 'partially' and not rec.loan_type:
                raise ValidationError("Loan Type is required In Loan Case")

    # @api.constrains('request_amount', 'payment', 'employee_id', 'loan_type', 'payment', 'payment_start_date',
    #                 'duration_month','loan_calculation','deduction_amount','reason')
    # def _check_advance_salary(self):
    #     for rec in self:
    #         rec.display_name = rec.name
    #         if rec.payment == 'fully':
    #             today_date = date.today()
    #             day_of_month = today_date.day
    #             # user = self.env['res.groups'].search([('name', '=', 'Special Approval')]).users
    #
    #             # if self.env.user.id in user.ids:
    #             #     user = user
    #             # else:
    #             #     user = False
    #             previous_advance = self.env['hr.advance.salary'].search([
    #                 ('employee_id', '=', rec.employee_id.id),
    #                 ('id', '!=', rec.id),  # Exclude the current record
    #                 ('amount_to_pay', '>', 0),
    #                 ('state', 'not in', ['write_off', 'refuse']),
    #             ], limit=1)
    #             if previous_advance:
    #                 raise ValidationError(
    #                     f'Employee already has a pending advance salary (Remaining Amount: {previous_advance.amount_to_pay}). Please clear it before applying for a new advance.'
    #                 )
    #
    #             if rec.request_amount <= 0:
    #                 raise ValidationError('Advance amount must be greater than zero.')
    #             if rec.request_amount > 50000:
    #                 rec.special_approval = True
    #                 # raise ValidationError('Special Approval Needs to Get Advance More then 50 K')
    #             if not (10 <= day_of_month <= 20):
    #                 rec.special_approval = True
    #             #     raise ValidationError(
    #             #         'Advance salary requests can only be made between the 11th and 20th of the month.')
    #             wage = rec.employee_id.contract_id.wage
    #             # user = self.env.user
    #             max_advance_allowed = wage / 2
    #             # is_special_approval = user.has_group('adv_loan_check.special_approval')
    #
    #             if rec.request_amount > max_advance_allowed:
    #                 rec.special_approval = True
    #
    #         else:
    #             if rec.payment == 'partially' and rec.loan_type == 'pf':
    #                 contract_start_date = rec.employee_id.contract_id.date_start
    #                 if not contract_start_date:
    #                     raise ValidationError('Employee\'s joining date is not defined.')
    #                 today_date = date.today()
    #                 date_1 = (today_date - contract_start_date).days
    #                 # user = self.env['res.groups'].search([('name', '=', 'Special Approval')]).users
    #                 previous_loans = self.env['hr.advance.salary'].search([
    #                     ('employee_id', '=', rec.employee_id.id),
    #                     ('state', '=', 'done'),
    #                 ], limit=1, order="id desc")
    #                 for loan in previous_loans:
    #                     if loan.amount_to_pay > 0:
    #                         raise ValidationError(
    #                             f'Employee already has a pending loan (Remaining Amount: {loan.amount_to_pay}). Please clear it before applying for a new loan.'
    #                         )
    #                     elif loan.state == 'done' and loan.write_date:  # Assuming 'paid' indicates fully paid
    #                         last_payment_date = loan.write_date.date()
    #                         # if (today_date - last_payment_date).days < last_payment_date + relativedelta(months=2):
    #                         if today_date < last_payment_date + relativedelta(months=2):
    #                             raise ValidationError(
    #                                 f'Employee can only apply for a new loan 2 months after fully repaying the previous loan (Last loan cleared on: {last_payment_date}).'
    #                             )
    #
    #                 if date_1 < 365:
    #                     rec.special_approval = True
    #                 if rec.request_amount <= 0:
    #                     raise ValidationError('Advance amount must be greater than zero.')
    #
    #                 wage = rec.employee_id.contract_id.wage
    #                 pf_grand_total = rec.employee_id.grand_total
    #                 if not wage:
    #                     raise ValidationError('Employees Wage is not defined.')
    #                 # if not pf_grand_total:
    #                 #     raise ValidationError('Employees PF Amount is not defined.')
    #
    #                 max_advance_allowed = wage / 2
    #
    #                 if rec.request_amount > max_advance_allowed:
    #                     rec.special_approval = True
    #                     # raise ValidationError(
    #                     #     f'Advance Loan amount cannot exceed 50% of employee\'s wage ({wage}).'
    #                     # )
    #                 if pf_grand_total < max_advance_allowed:
    #                     if rec.request_amount > pf_grand_total:
    #                         rec.special_approval = True
    #                         # raise ValidationError(
    #                         #     f'Advance Loan amount cannot exceed 50% of employee\'s wage and also this amount should be present in PF Amount ({pf_grand_total}).'
    #                         #
    #                         # )
    #
    #             elif rec.payment == 'partially' and rec.loan_type == 'gratuity':
    #                 contract_start_date = rec.employee_id.contract_id.date_start
    #                 if not contract_start_date:
    #                     raise ValidationError('Employee\'s joining date is not defined.')
    #                 today_date = date.today()
    #                 date_1 = (today_date - contract_start_date).days
    #                 # user = self.env['res.groups'].search([('name', '=', 'Special Approval')]).users
    #
    #                 # if self.env.user.id in user.ids:
    #                 #     user = user
    #                 # else:
    #                 #     user = False
    #                 previous_loans = self.env['hr.advance.salary'].search([
    #                     ('employee_id', '=', rec.employee_id.id),
    #                     # Exclude current record
    #
    #                     ('state', '=', 'done'),
    #                 ], limit=1, order="id desc")
    #                 for loan in previous_loans:
    #                     if loan.amount_to_pay > 0:
    #                         raise ValidationError(
    #                             f'Employee already has a pending loan (Remaining Amount: {loan.amount_to_pay}). Please clear it before applying for a new loan.'
    #                         )
    #                     elif loan.state == 'done' and loan.write_date:  # Assuming 'paid' indicates fully paid
    #                         last_payment_date = loan.write_date.date()
    #                         _logger.info('aaaaaaaaaaaaaaaaa')
    #                         _logger.info('aaaaaaaaaaaaaaaaa')
    #                         _logger.info('aaaaaaaaaaaaaaaaa', loan.state)
    #                         _logger.info('aaaaaaaaaaaaaaaaa', loan.write_date)
    #                         # if (today_date - last_payment_date).days < last_payment_date + relativedelta(months=2):
    #                         if today_date < last_payment_date + relativedelta(months=2):
    #                             raise ValidationError(
    #                                 f'Employee can only apply for a new loan 2 months after fully repaying the previous loan (Last loan cleared on: {last_payment_date}).'
    #                             )
    #
    #                 if date_1 < 365:
    #                     rec.special_approval = True
    #                     # raise ValidationError('At least one year of service is required to request a loan.')
    #
    #                 if rec.request_amount <= 0:
    #                     raise ValidationError('Advance amount must be greater than zero.')
    #
    #                 wage = rec.employee_id.contract_id.wage
    #                 gratuity_amount = rec.employee_id.total_gratuity
    #                 if not wage:
    #                     raise ValidationError('Employees Wage is not defined.')
    #                 # if not gratuity_amount:
    #                 #     raise ValidationError('Employees Gratuity Amount is not defined.')
    #
    #                 max_advance_allowed = wage / 2
    #
    #                 if rec.request_amount > max_advance_allowed:
    #                     rec.special_approval = True
    #                     # raise ValidationError(
    #                     #     f'Advance Loan amount cannot exceed 50% of employee\'s wage ({wage}).'
    #                     # )
    #                 if gratuity_amount < max_advance_allowed:
    #                     if rec.request_amount > gratuity_amount:
    #                         rec.special_approval = True
