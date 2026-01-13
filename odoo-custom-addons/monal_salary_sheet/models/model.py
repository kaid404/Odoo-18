from odoo import models, fields, api
import calendar
from datetime import date, datetime


class StockField(models.TransientModel):
    _name = 'monal.salary.sheet'

    date_from = fields.Date(string='Date')
    daily_wager = fields.Boolean(string='Daily Wager')
    company = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)
    employee = fields.Many2many('hr.employee', string='Employee')
    department = fields.Many2many('hr.department', string='Department')
    filter_by = fields.Selection([
        ('company', 'Company '),
        ('employee', 'Employee'),
        ('department', 'Department'),
    ], string='Filter By', default=False)

    month = fields.Selection(selection=lambda self: self._get_month_selection(),string="Month", required=True)

    def _get_month_selection(self):
        months = [
            ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
            ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ]
        month_selection = []
        for year in range(2025, 2041):
            for code, name in months:
                month_selection.append((f'{year}-{code}', f'{name} {year}'))
        return month_selection

    # month = fields.Selection(
    #     [(str(i), calendar.month_name[i]) for i in range(1, 13)],
    #     string="Month",
    # )
    # year = fields.Integer(string="Year", required=True, default=lambda self: date.today().year)

    def print_report(self):
        year_str, month_str = self.month.split('-')

        year = int(year_str)
        month = int(month_str)

        date_from = None
        date_to = None

        if self.daily_wager and self.date_from:
            date_from = self.date_from
            date_to = self.date_from
        else:

            date_from = date(year, month, 1)
            last_day = calendar.monthrange(year, month)[1]
            date_to = date(year, month, last_day)

            # month_int = int(self.month)
            # date_from = date(self.year, month_int, 1)
            # last_day = calendar.monthrange(self.year, month_int)[1]
            # date_to = date(self.year, month_int, last_day)

        print(date_from)
        print(date_to)
        domain = [
            ('date_from', '=', date_from),
            ('date_to', '=', date_to),
            ('state', '!=', ['draft', 'cancel'])
        ]

        if self.filter_by == 'company' and self.company:
            domain.append(('company_id', '=', self.company.id))

        elif self.filter_by == 'employee' and self.employee:
            domain.append(('employee_id', 'in', self.employee.ids))

        elif self.filter_by == 'department' and self.department:
            domain.append(('employee_id.department_id', 'in', self.department.ids))

        payslips = self.env['hr.payslip'].search(domain)

        result = []
        for slip in payslips:
            employee = slip.employee_id

            working_days_in_month = 0

            if self.daily_wager:
                attendances = self.env['hr.attendance'].search([
                    ('check_in', '>=', self.date_from),
                    ('check_out', '<=', self.date_from),
                    ('employee_id', '=', employee.id)
                ])
            else:
                attendances = self.env['hr.attendance'].search([
                    ('check_in', '>=', datetime.combine(date_from, datetime.min.time())),
                    ('check_out', '<=', datetime.combine(date_to, datetime.max.time())),
                    ('employee_id', '=', employee.id)
                ])

            if self.daily_wager:
                absents = 0
                sundays = 0
                working_days_in_month = 1
            else:
                total_days_in_month = calendar.monthrange(year, month)[1]
                all_days = [date(year, month, d) for d in range(1, total_days_in_month + 1)]
                sundays = sum(1 for d in all_days if d.weekday() == 6)
                total_days = total_days_in_month - sundays
                working_days_in_month = total_days
                absents = total_days - len(attendances)
                if absents < 0:
                    absents = 0

            rules = {
                'BASIC': 'Basic Salary',
                'GROSS': 'Gross Salary',
                'UM': 'Umra Deduction',
                'ADV/BNK': 'Bank A/C',
                'ADV/CSH': 'Current Advan',
                'FA': 'Food over',
                'ABSF': 'Absnty',
                'EOBIEE': 'EOBI',
                'NET': 'Net Salary',
            }

            line_totals = {}
            loan_deduct_total = 0
            allowances_amount = 0
            fine_debt = 0
            crockery_deduction = 0
            for line in slip.line_ids:
                if line.code in rules:
                    line_totals[line.code] = line.total
                elif line.code in ['LOAN/MED', 'LOAN/EDU']:
                    loan_deduct_total += line.total
                elif line.code in ['RA', 'SC', 'NSA', 'ENCASH', 'HD']:
                    allowances_amount += line.total
                elif line.code in ['CUT', 'LAUN', 'CHI', 'NS', 'CM', 'CSHD', 'ACCM', 'FI', 'DEB', 'FA', 'UNI', 'MAD',
                                   'FOD', 'TXD', 'SISSI', 'ABS']:
                    fine_debt += line.total
                elif line.code in ['CM', 'CD']:
                    crockery_deduction += line.total

            line_totals['LOAN_DEDUCT'] = loan_deduct_total
            line_totals['ALLOW'] = allowances_amount
            line_totals['FINE'] = fine_debt
            line_totals['CD'] = crockery_deduction

            paid_leave_days = 0

            excluded_types = self.env['hr.leave.type'].search([
                ('name', '=', 'Unpaid'),
            ]) | self.env['hr.leave.type'].search([
                ('name', '=', 'Short Leave')
            ])

            allowed_leave_types = self.env['hr.leave.type'].search([
                ('id', 'not in', excluded_types.ids)
            ])

            if allowed_leave_types:
                leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', employee.id),
                    ('state', 'in', ['validate', 'validate1']),
                    ('holiday_status_id', 'in', allowed_leave_types.ids),
                    ('request_date_from', '<=', date_to),
                    ('request_date_to', '>=', date_from)
                ])
                paid_leave_days = sum(l.number_of_days for l in leaves)
                absents -= paid_leave_days

            basic_salary = line_totals.get('BASIC') or line_totals.get('GROSS') or 0

            salary_per_day = 0
            if working_days_in_month > 0:
                salary_per_day = basic_salary / working_days_in_month

            encashment_amount = line_totals.get('ENCASH') or 0

            encashment_per_day = basic_salary / 30

            if encashment_per_day > 0:
                encashment_days = encashment_amount / encashment_per_day
            else:
                encashment_days = 0

            presents = len(attendances)
            presents = sum(
                1 for att in attendances
                if (getattr(att, 'is_zero', False) or att.worked_hours > 6)
            )

            work_days = presents + paid_leave_days + sundays

            if not self.daily_wager:
                total_days_in_month = calendar.monthrange(year, month)[1]

                work_days = min(work_days, total_days_in_month)

            salary_days = presents + paid_leave_days + sundays + encashment_days

            loan_records = self.env['hr.advance.salary'].search([
                ('employee_id', '=', employee.id),
                ('state', 'in', ['paid']),
                ('payment', '=', 'partially')
            ])

            out_standing = 0.0
            pre_out_starting = 0.0
            current_month = False

            if getattr(slip, 'date_from', False):
                if isinstance(slip.date_from, str):
                    try:
                        current_month = fields.Date.from_string(slip.date_from).strftime('%Y-%m')
                    except Exception:
                        current_month = slip.date_from[:7]
                else:
                    current_month = slip.date_from.strftime('%Y-%m')

            ONE2M_NAMES = ['line_ids', 'advance_line_ids', 'installment_ids', 'payment_line_ids', 'lines']
            LINE_DATE_FIELDS = ['date', 'payment_date', 'date_pay', 'date_due', 'payment_on', 'paid_date']
            LINE_SKIP_FIELDS = ['skip', 'is_skip', 'skipped', 'skip_this', 'skip_line']
            LINE_DEDUCTION_FIELDS = ['deduction_amount', 'amount', 'amount_to_pay', 'deducted', 'deduction']
            LINE_REMAINING_FIELDS = ['remaining_amount', 'remaining', 'balance', 'balance_amount']

            for loan in loan_records:
                loan_lines = getattr(loan, 'advance_salary_line_ids', False) or getattr(loan, 'advance_line_ids',
                                                                                        False) or getattr(loan,
                                                                                                          'line_ids',
                                                                                                          False) or []

                loan_outstanding = loan.amount_to_pay or loan.total_amount or loan.loan_amount or 0.0
                out_standing += loan_outstanding

                skip_this_month = False
                deduction_amount = getattr(loan, 'deduction_amount', 0.0) or 0.0

                for line in loan_lines:
                    line_date = getattr(line, 'date', getattr(line, 'payment_date', False))
                    if not line_date:
                        continue

                    line_month = line_date.strftime('%Y-%m') if isinstance(line_date, date) else str(line_date)[:7]
                    if line_month == current_month:
                        if getattr(line, 'skip', False):
                            skip_this_month = True
                        break

                if skip_this_month:
                    pre_out_starting += loan_outstanding
                else:
                    pre_out_starting += loan_outstanding - deduction_amount

            data = {
                'period': f"{calendar.month_name[int(month)]} {year}" if not self.daily_wager else date_from.strftime(
                    '%d-%b-%Y'),
                'employee_name': employee.name,
                'emp_code': employee.barcode,
                'designation': employee.job_id.name,
                'department': employee.department_id.name,
                'presents': presents,
                'absents': absents,
                'sundays': sundays,
                'paid_leaves': paid_leave_days,
                'salary_per_day': round(salary_per_day, 2),
                'working_days': round(work_days),
                'encashment_days': round(encashment_days),
                'salary_days': round(salary_days),
                'outstanding': out_standing,
                'pre_outstanding': pre_out_starting,
                'lines': line_totals,
                'image_url': '/web/image?model=hr.employee&id=%s&field=image_1920' % employee.id,
            }

            result.append(data)

        def get_basic(x):
            return x['lines'].get('BASIC') or x['lines'].get('GROSS') or 0

        try:
            result.sort(key=lambda x: (int(x['department'].split('-')[0]), -get_basic(x)))
        except:
            result.sort(key=lambda x: (x['department'] or '', -get_basic(x)))

        final_data = {'payslips': result}

        return self.env.ref('monal_salary_sheet.action_hr_playslip_report').report_action(self, data=final_data)
