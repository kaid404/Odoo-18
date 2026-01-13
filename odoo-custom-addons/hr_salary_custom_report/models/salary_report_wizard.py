from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import logging
from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import calendar

_logger = logging.getLogger(__name__)


class SalarySheetReportWizard(models.TransientModel):
    _name = 'salary.sheet.report.wizard'
    _description = 'Salary Sheet Report Wizard'

    period = fields.Selection(selection=lambda self: self._get_month_selection(), string='Period', required=True)
    from_date = fields.Date(
        'From Date',
        required=True
    )
    to_date = fields.Date(
        "To Date",
        required=True
    )
    select_employee = fields.Selection(
        [
            ('employee', 'Employee'),
            ('department', 'Department'),
            ('company', 'Company'),
        ],
        string="Report Type",
        default='employee',
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        domain=lambda self: [('id', '=', self.env.company.id)],
    )

    department_id = fields.Many2many(
        'hr.department',
        string="Departments",
        domain=lambda self: [('company_id', '=', self.env.company.id)]

    )

    employee_ids = fields.Many2many(
        'hr.employee',
        string="Employees",
        domain=lambda self: [('company_id', '=', self.env.company.id)]

    )

    @api.onchange('select_employee')
    def _onchange_select_employee(self):
        if self.select_employee == 'company':
            self.department_id = False
            self.employee_ids = False
        elif self.select_employee == 'department':
            self.employee_ids = False
        elif self.select_employee == 'employee':
            self.department_id = False

    def _get_month_selection(self):
        months = [
            ('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
            ('09', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ]
        month_selection = []
        for year in range(2025, 2035):
            for code, name in months:
                month_selection.append((f'{year}-{code}', f'{name} {year}'))
        return month_selection

    @api.onchange('period')
    def _onchange_month(self):
        if self.period:
            year, month = map(int, self.period.split('-'))
            self.from_date = f'{year}-{month:02d}-01'
            last_day = calendar.monthrange(year, month)[1]
            self.to_date = f'{year}-{month:02d}-{last_day}'

    def _get_default_period(self):
        return fields.Date.today().strftime('%Y-%m')

    # def _get_period_dates(self, period_value):
    #     year, month = map(int, period_value.split('-'))
    #     from_date = datetime(year, month, 1).date()
    #     to_date = from_date + relativedelta(months=1, days=-1)
    #     return from_date, to_date

    def get_total_days_in_month(self, from_date, to_date):

        delta = to_date - from_date
        return delta.days + 1

    def get_weekly_off_count(self, from_date, to_date):

        weekly_off_count = 0
        current_date = from_date

        while current_date <= to_date:
            if current_date.weekday() == 6:
                weekly_off_count += 1
            current_date += relativedelta(days=1)

        return weekly_off_count

    def get_attendance_data(self, employee, from_date, to_date):
        try:
            total_days_in_month = self.get_total_days_in_month(from_date, to_date)
            total_weekly_offs = self.get_weekly_off_count(from_date, to_date)

            attendance_records = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', from_date),
                ('check_in', '<=', to_date),
            ])

            attendance_dates = {}
            for attendance in attendance_records:
                attend_date = attendance.check_in.date()
                if from_date <= attend_date <= to_date:
                    work_hours = float(attendance.worked_hours or 0.0)
                    attendance_dates[attend_date] = work_hours

            present_days = 0
            days_with_less_work = 0
            for attend_date, work_hours in attendance_dates.items():
                if work_hours >= 6.0:
                    present_days += 1
                else:
                    days_with_less_work += 1

            leave_records = self.env['hr.leave'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'validate'),
                ('request_date_from', '<=', to_date),
                ('request_date_to', '>=', from_date),
            ])

            paid_leaves = 0
            unpaid_leaves = 0
            short_leaves = 0

            all_leave_dates = set()
            paid_leave_dates = set()
            unpaid_leave_dates = set()
            short_leave_dates = set()

            for leave in leave_records:
                leave_start = max(leave.request_date_from, from_date)
                leave_end = min(leave.request_date_to, to_date)

                current_leave_date = leave_start
                while current_leave_date <= leave_end:
                    is_short_leave = False
                    if leave.request_unit_half or leave.request_unit_hours:
                        is_short_leave = True

                    is_unpaid_leave = leave.holiday_status_id.unpaid or False

                    if is_short_leave:
                        short_leave_dates.add(current_leave_date)
                        short_leaves += 1
                    elif is_unpaid_leave:
                        unpaid_leave_dates.add(current_leave_date)
                        unpaid_leaves += 1
                    else:
                        paid_leave_dates.add(current_leave_date)
                        paid_leaves += 1

                    all_leave_dates.add(current_leave_date)
                    current_leave_date += relativedelta(days=1)

            total_leave_days = len(all_leave_dates)

            total_absent_without_sunday = total_days_in_month - present_days - total_leave_days
            unpaid_leaves = unpaid_leaves
            weekly_off_to_show = min(total_weekly_offs, total_absent_without_sunday)
            absent_days = total_absent_without_sunday - weekly_off_to_show + short_leaves
            work_days = present_days + paid_leaves + weekly_off_to_show
            leave_days_with_weekly_off = weekly_off_to_show

            return {
                'present_days': present_days,
                'absent_days': absent_days,
                'leave_days': leave_days_with_weekly_off,
                'paid_leaves': paid_leaves,
                'unpaid_leaves': unpaid_leaves,
                'short_leaves': short_leaves,
                'total_work_days': work_days,
                'total_month_days': total_days_in_month,
                'weekly_off': weekly_off_to_show,
                'days_with_less_work': days_with_less_work,
            }

        except Exception as e:
            _logger.error(f"Error getting attendance data for {employee.name}: {e}")
            return {
                'present_days': 0,
                'absent_days': 0,
                'leave_days': 0,
                'paid_leaves': 0,
                'unpaid_leaves': 0,
                'short_leaves': 0,
                'total_work_days': 0,
                'total_month_days': 0,
                'weekly_off': 0,
                'days_with_less_work': 0,
            }

    def get_salary_components(self, payslip, attendance_data):
        basic_salary = 0
        gross_salary = 0
        net_salary = payslip.net_wage or 0
        out_standing = 0
        salary_day = 0
        work_days = 0
        encashment = 0
        encashment_days = 0
        salary_days = 0
        allowance = 0
        umra_dept = 0
        food_over = 0
        absnty = 0
        eobi = 0
        loan_deduct = 0
        fine_debt = 0
        current_accm = 0
        credit_damage = 0
        pro_out_starting = 0
        crockery_deduction = 0
        bank_ac = 0
        wage = 0
        contract = payslip.contract_id or payslip.employee_id.contract_id

        if contract:
            wage = contract.wage or 0

        loan_records = self.env['hr.advance.salary'].search([
            ('employee_id', '=', payslip.employee_id.id),
            ('state', 'in', ['paid']),
            ('payment', '=', 'partially')
        ])

        current_month = False
        if getattr(payslip, 'date_from', False):
            if isinstance(payslip.date_from, str):
                try:
                    current_month = fields.Date.from_string(payslip.date_from).strftime('%Y-%m')
                except Exception:
                    current_month = payslip.date_from[:7]
            else:
                current_month = payslip.date_from.strftime('%Y-%m')

        out_standing = 0.0
        pro_out_starting = 0.0

        ONE2M_NAMES = ['line_ids', 'advance_line_ids', 'installment_ids', 'payment_line_ids', 'lines']
        LINE_DATE_FIELDS = ['date', 'payment_date', 'date_pay', 'date_due', 'payment_on', 'paid_date']
        LINE_SKIP_FIELDS = ['skip', 'is_skip', 'skipped', 'skip_this', 'skip_line']
        LINE_DEDUCTION_FIELDS = ['deduction_amount', 'amount', 'amount_to_pay', 'deducted', 'deduction']
        LINE_REMAINING_FIELDS = ['remaining_amount', 'remaining', 'balance', 'balance_amount']

        for loan in loan_records:
            loan_lines = getattr(loan, 'advance_salary_line_ids', False) or getattr(loan, 'advance_line_ids',
                                                                                    False) or getattr(loan, 'line_ids',
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
                pro_out_starting += loan_outstanding
                _logger.info(
                    f"✅ SKIP ACTIVE -> emp={payslip.employee_id.name} loan={loan.id} month={current_month} remaining={loan_outstanding}")
            else:
                pro_out_starting += loan_outstanding - deduction_amount
                _logger.info(
                    f"❌ SKIP NOT ACTIVE -> emp={payslip.employee_id.name} loan={loan.id} month={current_month} deduct={deduction_amount} remaining={loan_outstanding - deduction_amount}")

        for line in payslip.line_ids:
            if line.code == 'GROSS':
                gross_salary = line.total
            elif line.code == 'BASIC':
                basic_salary = line.total
            elif line.code == 'NET':
                net_salary = line.total
            elif line.code == 'ENCASH':
                encashment = line.total
            elif line.code == 'FA':
                food_over = line.total
            elif line.code == 'UM':
                umra_dept = line.total
            elif line.code in ['CM', 'CD']:
                crockery_deduction += line.total
            elif line.code in ['RA', 'SC', 'NSA', 'ENCASH','HD']:
                allowance += line.total
            elif line.code == 'ABSF':
                absnty = line.total
            elif line.code == 'EOBIEE':
                eobi = line.total
            elif 'ADV/BNK' in line.code:
                bank_ac += line.total or 0
            elif line.code in ['CUT', 'LAUN', 'CHI', 'NS', 'CSHD', 'ACCM', 'FI', 'DEB', 'UNI', 'MAD',
                               'FOD', 'TXD', 'SISSI', 'ABS']:
                fine_debt += line.total
            elif line.code in ['LOAN/SAL333', 'LOAN/EDU', 'LOAN/MED']:
                loan_deduct += line.total
            elif 'ADV/CSH' in line.code:
                current_accm += line.total

        work_days = attendance_data.get('total_work_days', 0)

        total_month_days = attendance_data.get('total_month_days', 0)
        total_sundays = attendance_data.get('weekly_off', 0)
        working_days_in_month = total_month_days - total_sundays

        salary_day = wage / working_days_in_month if working_days_in_month > 0 else 0

        encashment_days = encashment / salary_day if salary_day > 0 and encashment > 0 else 0
        salary_days = work_days + encashment_days

        return {
            'basic_salary': basic_salary,
            'gross_salary': gross_salary,
            'net_salary': net_salary,
            'out_standing': out_standing,
            'salary_day': round(salary_day),
            'work_days': round(work_days),
            'encashment': round(encashment),
            'encashment_days': round(encashment_days),
            'salary_days': round(salary_days),
            'allowance': allowance,
            'umra_dept': umra_dept,
            'food_over': food_over,
            'bank_ac': bank_ac,
            'absnty': absnty,
            'eobi': eobi,
            'loan_deduct': loan_deduct,
            'fine_debt': fine_debt,
            'current_accm': current_accm,
            'credit_damage': credit_damage,
            'pro_out_starting': pro_out_starting,
            'crockery_deduction': crockery_deduction,
            'wage': wage,
        }

    def action_print_report(self):
        self.ensure_one()

        # if self.select_employee == 'department' and not self.department_id:
        #     raise UserError("Please select departments for department-wise report.")
        # elif self.select_employee == 'employee' and not self.employee_ids:
        #     raise UserError("Please select employees for employee-wise report.")

        return self.env.ref('hr_salary_custom_report.action_salary_sheet_report_pdf').report_action(self)

    def action_print_report_xlsx(self):
        self.ensure_one()

        # if self.select_employee == 'department' and not self.department_id:
        #     raise UserError("Please select departments for department-wise report.")
        # elif self.select_employee == 'employee' and not self.employee_ids:
        #     raise UserError("Please select employees for employee-wise report.")

        return self.env.ref('hr_salary_custom_report.action_salary_sheet_report_xlsx').report_action(self)


class SalarySheetReport(models.AbstractModel):
    _name = 'report.hr_salary_custom_report.salary_sheet_report_template'
    _description = 'Salary Sheet Report'

    def format_amount_with_decimals(self, amount):
        """Format amount with comma as thousands separator and 2 decimal places"""
        if amount is None:
            return '0.00'
        try:
            return "{:,.2f}".format(float(amount))
        except (ValueError, TypeError):
            return '0.00'

    def format_amount(self, amount):
        """Format amount with comma as thousands separator"""
        if amount is None:
            return '0'
        try:
            return "{:,.0f}".format(float(amount))
        except (ValueError, TypeError):
            return '0'

    @api.model
    def _get_report_values(self, docids, data=None):
        wizard = self.env['salary.sheet.report.wizard'].browse(docids)
        report_data = self._get_report_data(wizard)

        return {
            'doc_ids': docids,
            'doc_model': 'salary.sheet.report.wizard',
            'docs': wizard,
            'data': report_data,
        }

    def _get_report_data(self, wizard):
        from_date = wizard.from_date
        to_date = wizard.to_date
        period_name = datetime.strptime(wizard.period + '-01', '%Y-%m-%d').strftime('%b %Y')

        employees = self.env['hr.employee']

        if wizard.select_employee == 'company':
            employees = self.env['hr.employee'].search([
                ('company_id', '=', wizard.company_id.id)
            ])
        elif wizard.select_employee == 'department':
            if wizard.department_id:
                employees = self.env['hr.employee'].search([
                    ('department_id', 'in', wizard.department_id.ids)
                ])
            else:
                employees = self.env['hr.employee'].search([
                    ('company_id', '=', wizard.company_id.id)
                ])
        elif wizard.select_employee == 'employee':
            if wizard.employee_ids:
                employees = wizard.employee_ids
            else:
                employees = self.env['hr.employee'].search([
                    ('company_id', '=', wizard.company_id.id)
                ])

        # Employee status tracking function
        def get_employee_status(emp, from_date, to_date):
            """
            Determine employee status for the period:
            - 'N' for new employees (joined in current month)
            - 'X' for employees who resigned in same month they joined
            - 'R' for employees who resigned in current month (but joined earlier)
            - '' for regular employees
            """
            contracts = self.env['hr.contract'].search([
                ('employee_id', '=', emp.id)
            ], order='date_start asc')

            if not contracts:
                return ''

            first_contract = contracts[0]
            latest_contract = contracts[-1]

            # Check if employee joined in current month
            joined_this_month = (first_contract.date_start >= from_date and
                                 first_contract.date_start <= to_date)

            # Check if employee resigned in current month
            resigned_this_month = False
            if (latest_contract.date_end and
                    latest_contract.date_end >= from_date and
                    latest_contract.date_end <= to_date and
                    latest_contract.state == 'close'):

                # Check if there are no new contracts after resignation
                new_contracts_after = self.env['hr.contract'].search([
                    ('employee_id', '=', emp.id),
                    ('date_start', '>', latest_contract.date_end)
                ])

                if not new_contracts_after:
                    resigned_this_month = True

            # Check if employee resigned in the same month they joined
            resigned_same_month = False
            if resigned_this_month:
                if (first_contract.date_start.year == latest_contract.date_end.year and
                        first_contract.date_start.month == latest_contract.date_end.month):
                    resigned_same_month = True

            if joined_this_month and resigned_same_month:
                return 'X'
            elif joined_this_month:
                return 'N'
            elif resigned_this_month:
                return 'R'
            else:
                return ''

        # Rest of the existing code remains same...
        domain = [
            ('state', 'in', ['verify', 'done', 'paid']),
            ('date_from', '>=', from_date),
            ('date_to', '<=', to_date),
            ('employee_id', 'in', employees.ids)
        ]
        payslip_records = self.env['hr.payslip'].search(domain)

        report_data = {
            'company_name': wizard.company_id.name,
            'period_name': period_name,
            'from_date': from_date.strftime('%d/%m/%Y'),
            'to_date': to_date.strftime('%d/%m/%Y'),
            'print_date': fields.Date.today().strftime('%d/%m/%Y'),
            'departments': [],
            'records': [],
            'has_data': False,
            'grand_totals': {},
            'grand_statistics': {},
        }

        if not payslip_records:
            report_data['message'] = f'No salary data found for {period_name}'
            return report_data

        grand_totals = {
            'present_days': 0,
            'absent_days': 0,
            'leave_days': 0,
            'paid_leaves': 0,
            'unpaid_leaves': 0,
            'wage': 0,
            'basic_salary': 0,
            'out_standing': 0,
            'salary_day': 0,
            'work_days': 0,
            'encashment': 0,
            'encashment_days': 0,
            'salary_days': 0,
            'allowance': 0,
            'gross_salary': 0,
            'umra_dept': 0,
            'bank_ac': 0,
            'food_over': 0,
            'absnty': 0,
            'eobi': 0,
            'loan_deduct': 0,
            'fine_debt': 0,
            'current_accm': 0,
            'crockery_deduction': 0,
            'pro_out_standing': 0,
            'net_salary': 0,
            'employee_count': 0,
        }

        def get_employee_statistics(employee_domain):
            all_employees = self.env['hr.employee'].search(employee_domain)

            total_new_joinings = 0
            total_resigned = 0

            for emp in all_employees:
                contracts = self.env['hr.contract'].search([
                    ('employee_id', '=', emp.id)
                ], order='date_start asc')

                if contracts:
                    first_contract = contracts[0]
                    latest_contract = contracts[-1]

                    if first_contract.date_start >= from_date and first_contract.date_start <= to_date:
                        total_new_joinings += 1

                    if (latest_contract.date_end and
                            latest_contract.date_end >= from_date and
                            latest_contract.date_end <= to_date and
                            latest_contract.state == 'close'):

                        new_contracts_after = self.env['hr.contract'].search([
                            ('employee_id', '=', emp.id),
                            ('date_start', '>', latest_contract.date_end)
                        ])

                        if not new_contracts_after:
                            total_resigned += 1

            return {
                'total_employees': len(all_employees),
                'new_joinings': total_new_joinings,
                'resigned_employees': total_resigned,
            }

        if wizard.select_employee == 'company':
            employee_domain = [('company_id', '=', wizard.company_id.id)]
        elif wizard.select_employee == 'department':
            if wizard.department_id:
                employee_domain = [('department_id', 'in', wizard.department_id.ids)]
            else:
                employee_domain = [('company_id', '=', wizard.company_id.id)]
        elif wizard.select_employee == 'employee':
            if wizard.employee_ids:
                employee_domain = [('id', 'in', wizard.employee_ids.ids)]
            else:
                employee_domain = [('company_id', '=', wizard.company_id.id)]

        report_data['grand_statistics'] = get_employee_statistics(employee_domain)

        if wizard.select_employee in ['employee', 'department', 'company']:
            grouped = {}
            for slip in payslip_records:
                dept = slip.employee_id.department_id or self.env['hr.department']
                dept_name = dept.name if dept else 'No Department'
                grouped.setdefault(dept, []).append(slip)

            for dept, dept_payslips in grouped.items():
                dept_employee_domain = [('department_id', '=', dept.id if dept else False)]
                dept_stats = get_employee_statistics(dept_employee_domain)

                dept_data = {
                    'department_name': dept.name if dept else 'No Department',
                    'employees': [],
                    'dept_totals': {
                        'present_days': 0,
                        'absent_days': 0,
                        'leave_days': 0,
                        'paid_leaves': 0,
                        'unpaid_leaves': 0,
                        'wage': 0,
                        'basic_salary': 0,
                        'out_standing': 0,
                        'salary_day': 0,
                        'work_days': 0,
                        'encashment': 0,
                        'encashment_days': 0,
                        'salary_days': 0,
                        'allowance': 0,
                        'gross_salary': 0,
                        'umra_dept': 0,
                        'bank_ac': 0,
                        'food_over': 0,
                        'absnty': 0,
                        'eobi': 0,
                        'loan_deduct': 0,
                        'fine_debt': 0,
                        'current_accm': 0,
                        'crockery_deduction': 0,
                        'pro_out_standing': 0,
                        'net_salary': 0,
                        'employee_count': 0,
                    },
                    'dept_statistics': dept_stats
                }

                # Collect all employee data first for sorting
                employee_data_list = []

                for seq, payslip in enumerate(dept_payslips, 1):
                    attendance_data = wizard.get_attendance_data(
                        payslip.employee_id, from_date, to_date)
                    salary_data = wizard.get_salary_components(payslip, attendance_data)
                    emp = payslip.employee_id

                    # Get employee status
                    emp_status = get_employee_status(emp, from_date, to_date)

                    employee_data = {
                        'sr_no': seq,
                        'emp_code': emp.barcode or emp.id,
                        'emp_name': emp.name,
                        'designation': emp.job_id.name or '',
                        'emp_status': emp_status,
                        'present_days': attendance_data['present_days'],
                        'absent_days': attendance_data['absent_days'],
                        'leave_days': attendance_data['leave_days'],
                        'pl': attendance_data['paid_leaves'],
                        'unpaid_leaves': attendance_data['unpaid_leaves'],
                        'wage': salary_data['wage'],  # Store actual value for sorting
                        'basic_salary': salary_data['basic_salary'],  # Store actual value for sorting
                        'out_standing': salary_data['out_standing'],
                        'salary_day': salary_data['salary_day'],
                        'work_days': salary_data['work_days'],
                        'encashment': salary_data['encashment'],
                        'encashment_days': salary_data['encashment_days'],
                        'salary_days': salary_data['salary_days'],
                        'allowance': salary_data['allowance'],
                        'gross_salary': salary_data['gross_salary'],
                        'umra_dept': salary_data['umra_dept'],
                        'bank_ac': salary_data['bank_ac'],
                        'food_over': salary_data['food_over'],
                        'absnty': salary_data['absnty'],
                        'eobi': salary_data['eobi'],
                        'loan_deduct': salary_data['loan_deduct'],
                        'fine_debt': salary_data['fine_debt'],
                        'current_accm': salary_data['current_accm'],
                        'crockery_deduction': salary_data['crockery_deduction'],
                        'pro_out_standing': salary_data['pro_out_starting'],
                        'net_salary': salary_data['net_salary'],
                        # Store actual values for totaling
                        '_wage': salary_data['wage'],
                        '_basic_salary': salary_data['basic_salary'],
                        '_out_standing': salary_data['out_standing'],
                        '_salary_day': salary_data['salary_day'],
                        '_encashment': salary_data['encashment'],
                        '_allowance': salary_data['allowance'],
                        '_gross_salary': salary_data['gross_salary'],
                        '_umra_dept': salary_data['umra_dept'],
                        '_bank_ac': salary_data['bank_ac'],
                        '_food_over': salary_data['food_over'],
                        '_absnty': salary_data['absnty'],
                        '_eobi': salary_data['eobi'],
                        '_loan_deduct': salary_data['loan_deduct'],
                        '_fine_debt': salary_data['fine_debt'],
                        '_current_accm': salary_data['current_accm'],
                        '_crockery_deduction': salary_data['crockery_deduction'],
                        '_pro_out_standing': salary_data['pro_out_starting'],
                        '_net_salary': salary_data['net_salary'],
                    }

                    employee_data_list.append(employee_data)

                # Sort employees by basic salary in descending order (highest first)
                employee_data_list.sort(key=lambda x: x['_wage'], reverse=True)

                # Now add formatted data to department
                for seq, emp_data in enumerate(employee_data_list, 1):
                    # Update sequence number after sorting
                    emp_data['sr_no'] = seq

                    # Format the amounts for display
                    formatted_emp_data = emp_data.copy()
                    formatted_emp_data['wage'] = self.format_amount(emp_data['_wage'])
                    formatted_emp_data['basic_salary'] = self.format_amount(emp_data['_basic_salary'])
                    formatted_emp_data['out_standing'] = self.format_amount(emp_data['_out_standing'])
                    formatted_emp_data['salary_day'] = self.format_amount(emp_data['_salary_day'])
                    formatted_emp_data['encashment'] = self.format_amount(emp_data['_encashment'])
                    formatted_emp_data['allowance'] = self.format_amount(emp_data['_allowance'])
                    formatted_emp_data['gross_salary'] = self.format_amount(emp_data['_gross_salary'])
                    formatted_emp_data['umra_dept'] = self.format_amount(emp_data['_umra_dept'])
                    formatted_emp_data['bank_ac'] = self.format_amount(emp_data['_bank_ac'])
                    formatted_emp_data['food_over'] = self.format_amount(emp_data['_food_over'])
                    formatted_emp_data['absnty'] = self.format_amount(emp_data['_absnty'])
                    formatted_emp_data['eobi'] = self.format_amount(emp_data['_eobi'])
                    formatted_emp_data['loan_deduct'] = self.format_amount(emp_data['_loan_deduct'])
                    formatted_emp_data['fine_debt'] = self.format_amount(emp_data['_fine_debt'])
                    formatted_emp_data['current_accm'] = self.format_amount(emp_data['_current_accm'])
                    formatted_emp_data['crockery_deduction'] = self.format_amount(emp_data['_crockery_deduction'])
                    formatted_emp_data['pro_out_standing'] = self.format_amount(emp_data['_pro_out_standing'])
                    formatted_emp_data['net_salary'] = self.format_amount(emp_data['_net_salary'])

                    dept_data['employees'].append(formatted_emp_data)

                    # Update department totals with actual values
                    dept_data['dept_totals']['present_days'] += emp_data['present_days']
                    dept_data['dept_totals']['absent_days'] += emp_data['absent_days']
                    dept_data['dept_totals']['leave_days'] += emp_data['leave_days']
                    dept_data['dept_totals']['paid_leaves'] += emp_data['pl']
                    dept_data['dept_totals']['unpaid_leaves'] += emp_data['unpaid_leaves']
                    dept_data['dept_totals']['wage'] += emp_data['_wage']
                    dept_data['dept_totals']['basic_salary'] += emp_data['_basic_salary']
                    dept_data['dept_totals']['out_standing'] += emp_data['_out_standing']
                    dept_data['dept_totals']['salary_day'] += emp_data['_salary_day']
                    dept_data['dept_totals']['work_days'] += emp_data['work_days']
                    dept_data['dept_totals']['encashment'] += emp_data['_encashment']
                    dept_data['dept_totals']['encashment_days'] += emp_data['encashment_days']
                    dept_data['dept_totals']['salary_days'] += emp_data['salary_days']
                    dept_data['dept_totals']['allowance'] += emp_data['_allowance']
                    dept_data['dept_totals']['gross_salary'] += emp_data['_gross_salary']
                    dept_data['dept_totals']['umra_dept'] += emp_data['_umra_dept']
                    dept_data['dept_totals']['bank_ac'] += emp_data['_bank_ac']
                    dept_data['dept_totals']['food_over'] += emp_data['_food_over']
                    dept_data['dept_totals']['absnty'] += emp_data['_absnty']
                    dept_data['dept_totals']['eobi'] += emp_data['_eobi']
                    dept_data['dept_totals']['loan_deduct'] += emp_data['_loan_deduct']
                    dept_data['dept_totals']['fine_debt'] += emp_data['_fine_debt']
                    dept_data['dept_totals']['current_accm'] += emp_data['_current_accm']
                    dept_data['dept_totals']['crockery_deduction'] += emp_data['_crockery_deduction']
                    dept_data['dept_totals']['pro_out_standing'] += emp_data['_pro_out_standing']
                    dept_data['dept_totals']['net_salary'] += emp_data['_net_salary']
                    dept_data['dept_totals']['employee_count'] += 1

                    # Update grand totals
                    grand_totals['present_days'] += emp_data['present_days']
                    grand_totals['absent_days'] += emp_data['absent_days']
                    grand_totals['leave_days'] += emp_data['leave_days']
                    grand_totals['paid_leaves'] += emp_data['pl']
                    grand_totals['unpaid_leaves'] += emp_data['unpaid_leaves']
                    grand_totals['wage'] += emp_data['_wage']
                    grand_totals['basic_salary'] += emp_data['_basic_salary']
                    grand_totals['out_standing'] += emp_data['_out_standing']
                    grand_totals['salary_day'] += emp_data['_salary_day']
                    grand_totals['work_days'] += emp_data['work_days']
                    grand_totals['encashment'] += emp_data['_encashment']
                    grand_totals['encashment_days'] += emp_data['encashment_days']
                    grand_totals['salary_days'] += emp_data['salary_days']
                    grand_totals['allowance'] += emp_data['_allowance']
                    grand_totals['gross_salary'] += emp_data['_gross_salary']
                    grand_totals['umra_dept'] += emp_data['_umra_dept']
                    grand_totals['bank_ac'] += emp_data['_bank_ac']
                    grand_totals['food_over'] += emp_data['_food_over']
                    grand_totals['absnty'] += emp_data['_absnty']
                    grand_totals['eobi'] += emp_data['_eobi']
                    grand_totals['loan_deduct'] += emp_data['_loan_deduct']
                    grand_totals['fine_debt'] += emp_data['_fine_debt']
                    grand_totals['current_accm'] += emp_data['_current_accm']
                    grand_totals['crockery_deduction'] += emp_data['_crockery_deduction']
                    grand_totals['pro_out_standing'] += emp_data['_pro_out_standing']
                    grand_totals['net_salary'] += emp_data['_net_salary']
                    grand_totals['employee_count'] += 1

                report_data['departments'].append(dept_data)

            report_data['departments'] = sorted(
                report_data['departments'],
                key=lambda d: d.get('department_name', '').lower()
            )

            # Format department totals
            for dept in report_data['departments']:
                for key, value in dept.get('dept_totals', {}).items():
                    if isinstance(value, (int, float)):
                        dept['dept_totals'][key] = self.format_amount(value)

            # Format grand totals
            for key, value in grand_totals.items():
                if isinstance(value, (int, float)):
                    grand_totals[key] = self.format_amount(value)

            report_data['grand_totals'] = grand_totals
            report_data['has_data'] = True
            return report_data
