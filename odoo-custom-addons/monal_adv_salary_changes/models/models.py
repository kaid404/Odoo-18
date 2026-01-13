from odoo import models, fields, api
from odoo.exceptions import ValidationError
import calendar
from datetime import datetime, date, timedelta


class HrAdvanceSalaryChanges(models.Model):
    _inherit = 'hr.advance.salary'

    advance_type = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string='Type', default='bank')

    salary_without_tax = fields.Float(string='Basic Salary', readonly=True)
    # resident_allowance_amount = fields.Float(string="Resident Allowance", readonly=True)
    # realocation_allowance_amount = fields.Float(string="Realocation Allowance", readonly=True)
    # bike_allowance_amount = fields.Float(string="Bike Allowance", readonly=True)
    # car_maintence_allowance_amount = fields.Float(string="Car Maintenance Allowance", readonly=True)
    house_allowance_amount = fields.Float(string="House Allowance", readonly=True)
    # car_allowance_amount = fields.Float(string="Car Allowance", readonly=True)
    # mobile_allowance_amount = fields.Float(string="Mobile Allowance", readonly=True)
    # miscellaneous_allowance_amount = fields.Float(string="Misc Allowance", readonly=True)
    # fuel_allowance_cash_amount = fields.Float(string="Fuel Cash Allowance", readonly=True)
    # food_allowance_amount = fields.Float(string="Food Allowance", readonly=True)
    # gun_allowance_amount = fields.Float(string="Gun Allowance", readonly=True)
    # hill_allowance_amount = fields.Float(string="Hill Allowance", readonly=True)
    loan_amount = fields.Float(string='Loan Amount', readonly=True)
    tax_amount = fields.Float(string='Tax Amount', readonly=True)
    eobi_amount = fields.Float(string='EOBI Amount', readonly=True)
    umra_amount = fields.Float(string='Umrah Deduction', readonly=True)
    already_taken_adv = fields.Float(string='Advance Already Taken', readonly=True)
    allowed_amount = fields.Float(string='Earned Salary', readonly=True)
    remaining_bank_limit = fields.Float(string='Bank Limit', readonly=True)

    def calculate_button_action(self):
        res = super().calculate_button_action()

        for rec in self:
            if rec.payment == 'fully':
                if rec.request_date:
                    day = rec.request_date.day

                    # if not rec.special_approval and day != 24:
                    #     rec.allowed_amount = 0
                    # else:
                    month = rec.request_date.month
                    year = rec.request_date.year

                    total_days_in_month = [
                        d for d in (date(year, month, 1) + timedelta(days=i)
                                    for i in range(calendar.monthrange(year, month)[1]))
                        if d.weekday() != 6
                    ]
                    days_in_month = len(total_days_in_month)

                    total_wage = rec.employee_id.contract_id.wage
                    wage_per_day = total_wage / days_in_month

                    start_date = date(year, month, 1)
                    end_date = date(year, month, day)

                    attendances = self.env['hr.attendance'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('check_in', '>=', datetime.combine(start_date, datetime.min.time())),
                        ('check_in', '<=', datetime.combine(end_date, datetime.max.time())),
                    ])

                    working_days = set()
                    employee_schedule = rec.employee_id.resource_calendar_id

                    if employee_schedule and employee_schedule.x_studio_is_zero:
                        for att in attendances:
                            if att.check_in:
                                working_days.add(att.check_in.date())
                    else:
                        for att in attendances:
                            if att.check_in and att.worked_hours > 6:
                                working_days.add(att.check_in.date())

                    total_working_days = len(working_days)

                    if total_working_days > days_in_month:
                        total_working_days = days_in_month

                    # working_days = set(a.check_in.date() for a in attendances if a.check_in)
                    # total_working_days = len(working_days)

                    new_wage = wage_per_day * total_working_days
                    rec.salary_without_tax = new_wage

                    contract = self.env['hr.contract'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('state', '=', 'open')
                    ], order='date_start desc', limit=1)

                    # resident_per_day = contract.x_studio_resident_allowance / days_in_month
                    house_per_day = contract.x_studio_house / days_in_month
                    # realocation_per_day = contract.x_studio_realocation / days_in_month
                    # bike_per_day = contract.x_studio_bike / days_in_month
                    # car_maintence_per_day = contract.x_studio_car_maintence / days_in_month
                    # car_allowance_per_day = contract.x_studio_car_allowance / days_in_month
                    # mobile_per_day = contract.x_studio_mobile_allowance / days_in_month
                    # miscellaneous_per_day = contract.x_studio_miscellaneous_allowance / days_in_month
                    # fuel_cash_per_day = contract.x_studio_fuel_allowance_cash_1 / days_in_month
                    # food_per_day = contract.x_studio_food_allowance / days_in_month
                    # gun_per_day = contract.x_studio_gun_allowance / days_in_month
                    # hill_per_day = contract.x_studio_hill / days_in_month

                    # rec.resident_allowance_amount = resident_per_day * total_working_days
                    rec.house_allowance_amount = house_per_day * total_working_days
                    # rec.realocation_allowance_amount = realocation_per_day * total_working_days
                    # rec.bike_allowance_amount = bike_per_day * total_working_days
                    # rec.car_maintence_allowance_amount = car_maintence_per_day * total_working_days
                    # rec.car_allowance_amount = car_allowance_per_day * total_working_days
                    # rec.mobile_allowance_amount = mobile_per_day * total_working_days
                    # rec.miscellaneous_allowance_amount = miscellaneous_per_day * total_working_days
                    # rec.fuel_allowance_cash_amount = fuel_cash_per_day * total_working_days
                    # rec.food_allowance_amount = food_per_day * total_working_days
                    # rec.gun_allowance_amount = gun_per_day * total_working_days
                    # rec.hill_allowance_amount = hill_per_day * total_working_days

                    allowances = contract.x_studio_house

                    # allowances = (
                    #         contract.x_studio_resident_allowance + contract.x_studio_realocation + contract.x_studio_bike + contract.x_studio_car_maintence +
                    #         contract.x_studio_house + contract.x_studio_car_allowance + contract.x_studio_mobile_allowance + contract.x_studio_miscellaneous_allowance +
                    #         contract.x_studio_fuel_allowance_cash_1 + contract.x_studio_gun_allowance + contract.x_studio_hill)

                    allowance_per_day = allowances / days_in_month

                    total_allowance_amount = allowance_per_day * total_working_days

                    wage_without_tax = new_wage + total_allowance_amount

                    loan_installments = self.env['hr.advance.salary'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('id', '!=', rec.id),
                        ('payment', '=', 'partially'),
                        ('state', '=', 'paid'),
                    ])

                    loan_deduction = 0.0

                    for loan in loan_installments:
                        for line in loan.advance_salary_line_ids:
                            line_month = line.date.month
                            line_year = line.date.year

                            if line_month == month and line_year == year and line.skip != True:
                                loan_deduction += line.amount

                    already_taken = self.env['hr.advance.salary'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('id', '!=', rec.id),
                        ('payment', '=', 'fully'),
                        ('state', 'in', ['paid', 'done']),
                        ('request_date', '>=', date(year, month, 1)),
                        ('request_date', '<=', date(year, month, calendar.monthrange(year, month)[1])),
                    ])

                    already_taken_amount = sum(already_taken.mapped('amount_to_pay'))

                    rec.already_taken_adv = already_taken_amount


                    bank_salary = contract.x_studio_bank_salary

                    max_bank_amount = bank_salary

                    already_taken_bank = self.env['hr.advance.salary'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('id', '!=', rec.id),
                        ('payment', '=', 'fully'),
                        ('advance_type', '=', 'bank'),
                        ('state', 'in', ['paid', 'done']),
                        ('request_date', '>=', date(year, month, 1)),
                        ('request_date', '<=', date(year, month, calendar.monthrange(year, month)[1])),
                    ])

                    if already_taken_bank:
                        already_taken_bank_amount = sum(already_taken_bank.mapped('amount_to_pay'))
                        rec.remaining_bank_limit = max_bank_amount - already_taken_bank_amount
                    else:
                        rec.remaining_bank_limit = max_bank_amount


                    umrah_deduction = 0

                    if contract.x_studio_umra_deduction:
                        umrah_deduction += contract.wage * 0.03

                    rec.umra_amount = umrah_deduction

                    rec.loan_amount = loan_deduction

                    eobi_deduc = 0

                    if not contract.x_studio_disallow_eobi:
                        # pass
                        eobi_deduc += self.env.company.basic_govt_wage * 0.01

                    rec.tax_amount = contract.x_studio_income_tax
                    rec.eobi_amount = eobi_deduc

                    deductions = contract.x_studio_income_tax + eobi_deduc + loan_deduction + umrah_deduction + already_taken_amount

                    # tax_amount = contract.x_studio_income_tax + contract.x_studio_employee_eobi + loan_deduction + umrah_deduction

                    adv_salary_wage = wage_without_tax - deductions

                    rec.allowed_amount = adv_salary_wage

        return res

    def action_confirm(self):
        res = super().action_confirm()

        for rec in self:
            if rec.payment == 'fully':
                if rec.request_date:
                    day = rec.request_date.day

                    if not rec.special_approval and day != 24:
                        raise ValidationError('You can only take Advance Salary on 24th date of the month.')
                    else:
                        month = rec.request_date.month
                        year = rec.request_date.year

                        total_days_in_month = [
                            d for d in (date(year, month, 1) + timedelta(days=i)
                                        for i in range(calendar.monthrange(year, month)[1]))
                            if d.weekday() != 6
                        ]
                        days_in_month = len(total_days_in_month)

                        # days_in_month = calendar.monthrange(year, month)[1]
                        total_wage = rec.employee_id.contract_id.wage
                        wage_per_day = total_wage / days_in_month
                        start_date = date(year, month, 1)
                        end_date = date(year, month, day)
                        attendances = self.env['hr.attendance'].search([
                            ('employee_id', '=', rec.employee_id.id),
                            ('check_in', '>=', datetime.combine(start_date, datetime.min.time())),
                            ('check_in', '<=', datetime.combine(end_date, datetime.max.time())),
                        ])

                        working_days = set()
                        employee_schedule = rec.employee_id.resource_calendar_id

                        if employee_schedule and employee_schedule.x_studio_is_zero:
                            for att in attendances:
                                if att.check_in:
                                    working_days.add(att.check_in.date())
                        else:
                            for att in attendances:
                                if att.check_in and att.worked_hours > 6:
                                    working_days.add(att.check_in.date())

                        total_working_days = len(working_days)

                        if total_working_days > days_in_month:
                            total_working_days = days_in_month

                        new_wage = wage_per_day * total_working_days

                        contract = self.env['hr.contract'].search([
                            ('employee_id', '=', rec.employee_id.id),
                            ('state', '=', 'open')
                        ], order='date_start desc', limit=1)

                        allowances = contract.x_studio_house

                        # allowances = (
                        #         contract.x_studio_resident_allowance + contract.x_studio_realocation + contract.x_studio_bike + contract.x_studio_car_maintence +
                        #         contract.x_studio_house + contract.x_studio_car_allowance + contract.x_studio_mobile_allowance + contract.x_studio_miscellaneous_allowance +
                        #         contract.x_studio_fuel_allowance_cash_1 + contract.x_studio_gun_allowance + contract.x_studio_hill)

                        allowance_per_day = allowances / days_in_month

                        total_allowance_amount = allowance_per_day * total_working_days

                        wage_without_tax = new_wage + total_allowance_amount

                        loan_installments = self.env['hr.advance.salary'].search([
                            ('employee_id', '=', rec.employee_id.id),
                            ('id', '!=', rec.id),
                            ('payment', '=', 'partially'),
                            ('state', '=', 'paid'),
                        ])

                        loan_deduction = 0.0

                        for loan in loan_installments:
                            for line in loan.advance_salary_line_ids:
                                line_month = line.date.month
                                line_year = line.date.year

                                if line_month == month and line_year == year and line.skip != True:
                                    loan_deduction += line.amount

                        already_taken = self.env['hr.advance.salary'].search([
                            ('employee_id', '=', rec.employee_id.id),
                            ('id', '!=', rec.id),
                            ('payment', '=', 'fully'),
                            ('state', 'in', ['paid', 'done']),
                            ('request_date', '>=', date(year, month, 1)),
                            ('request_date', '<=', date(year, month, calendar.monthrange(year, month)[1])),
                        ])

                        already_taken_amount = sum(already_taken.mapped('amount_to_pay'))

                        umrah_deduction = 0

                        if contract.x_studio_umra_deduction:
                            umrah_deduction += contract.wage * 0.03

                        eobi_deduc = 0

                        if not contract.x_studio_disallow_eobi:
                            eobi_deduc += self.env.company.basic_govt_wage * 0.01

                        deductions = contract.x_studio_income_tax + eobi_deduc + loan_deduction + umrah_deduction + already_taken_amount

                        adv_salary_wage = wage_without_tax - deductions

                        bank_salary = contract.x_studio_bank_salary

                        if rec.advance_type == 'bank':
                            max_bank_amount = bank_salary

                            already_taken_bank = self.env['hr.advance.salary'].search([
                                ('employee_id', '=', rec.employee_id.id),
                                ('id', '!=', rec.id),
                                ('payment', '=', 'fully'),
                                ('advance_type', '=', 'bank'),
                                ('state', 'in', ['paid', 'done']),
                                ('request_date', '>=', date(year, month, 1)),
                                ('request_date', '<=', date(year, month, calendar.monthrange(year, month)[1])),
                            ])

                            if already_taken_bank:
                                already_taken_bank_amount = sum(already_taken_bank.mapped('amount_to_pay'))

                                remaining_bank_amount = max_bank_amount - already_taken_bank_amount


                                if rec.request_amount > remaining_bank_amount:
                                    raise ValidationError(
                                        f"You’ve already taken {already_taken_bank_amount:.2f} from your Bank advance. "
                                        f"Your remaining eligible amount is {remaining_bank_amount:.2f}, "
                                        f"but you requested {rec.request_amount:.2f}."
                                    )

                            if rec.request_amount > max_bank_amount:
                                raise ValidationError(
                                    f"Your eligible Bank advance amount is {max_bank_amount:.2f}. "
                                    f"You cannot request more than this."
                                )

                        if rec.advance_type == 'cash':

                            max_bank_amount = bank_salary

                            already_taken_bank = self.env['hr.advance.salary'].search([
                                ('employee_id', '=', rec.employee_id.id),
                                ('id', '!=', rec.id),
                                ('payment', '=', 'fully'),
                                ('advance_type', '=', 'bank'),
                                ('state', 'in', ['paid', 'done']),
                                ('request_date', '>=', date(year, month, 1)),
                                ('request_date', '<=', date(year, month, calendar.monthrange(year, month)[1])),
                            ])
                            if already_taken_bank:

                                already_taken_bank_amount = sum(already_taken_bank.mapped('amount_to_pay'))
                                print(already_taken_bank_amount)
                                remaining_bank_limit = max_bank_amount - already_taken_bank_amount
                                print(remaining_bank_limit)
                                max_cash_amount = adv_salary_wage - remaining_bank_limit
                                print(max_cash_amount)
                                print('GEOOOOOOOOOOOOOOO')

                                if rec.request_amount > max_cash_amount:
                                    raise ValidationError(
                                        f"Your eligible Cash advance amount is {max_cash_amount:.2f}. "
                                        f"You cannot request more than this."
                                    )
                            else:
                                max_cash_amount = adv_salary_wage - max_bank_amount
                                print('this condition got hit.....')
                                if rec.request_amount > max_cash_amount:
                                    raise ValidationError(
                                        f"Your eligible Cash advance amount is {max_cash_amount:.2f}. "
                                        f"You cannot request more than this."
                                    )

                        if rec.request_amount > adv_salary_wage:
                            raise ValidationError(
                                f'Advance salary for {day}th cannot exceed salary of {total_working_days} working days.')

        return res


class HrContract(models.Model):
    _inherit = 'hr.contract'

    x_studio_resident_allowance = fields.Float(string="Resident Allowance", default=1000)
    x_studio_realocation = fields.Float(string="Relocation Allowance", default=1000)
    x_studio_bike = fields.Float(string="Bike Allowance", default=1000)
    x_studio_car_maintence = fields.Float(string="Car Maintenance Allowance", default=1000)
    x_studio_house = fields.Float(string="House Allowance", default=1000)
    x_studio_car_allowance = fields.Float(string="Car Allowance", default=1000)
    x_studio_mobile_allowance = fields.Float(string="Mobile Allowance", default=1000)
    x_studio_miscellaneous_allowance = fields.Float(string="Miscellaneous Allowance", default=1000)
    x_studio_fuel_allowance_cash_1 = fields.Float(string="Fuel Allowance (Cash)", default=1000)
    x_studio_food_allowance = fields.Float(string="Food Allowance", default=1000)
    x_studio_gun_allowance = fields.Float(string="Gun Allowance", default=1000)
    x_studio_hill = fields.Float(string="Hill Allowance", default=1000)

    x_studio_income_tax = fields.Float(string="Tax", default=2000.0)
    x_studio_employee_eobi = fields.Float(string="EOBI Amount", default=2000.0)
    x_studio_umra_deduction = fields.Boolean(string="Umrah Deduction")
    x_studio_disallow_eobi = fields.Boolean(string="Disallow EOBI")

    x_studio_bank_salary = fields.Float(string="Bank Salary", default=1000)