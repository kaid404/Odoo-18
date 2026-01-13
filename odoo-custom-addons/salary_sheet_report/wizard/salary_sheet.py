from odoo import models, api, fields
from datetime import date, timedelta
from calendar import monthrange, month_name
import calendar
from odoo.exceptions import ValidationError


class SalarySheet(models.TransientModel):
    _name = 'salary.sheet'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='Batch')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    check = fields.Boolean(string='Check', default=False)
    check2 = fields.Boolean(string='Check', default=False)
    date_from = fields.Date(string='From')
    date_to = fields.Date(string="To")

    @api.onchange('payslip_run_id')
    def onchange_payslip_run_id(self):
        if self.payslip_run_id:
            self.check = True

    @api.onchange('date_from', 'date_to')
    def onchange_dates(self):
        if self.date_from or self.date_to:
            self.check2 = True

    def salary_sheet_xlsx(self):
        month = ''
        if self.date_from and self.date_to:
            if self.date_from.month == self.date_to.month:
                month = f"{calendar.month_name[self.date_to.month]}-{self.date_from.year}"
            else:
                month = f"{calendar.month_name[self.date_from.month]}-{self.date_from.year} To {calendar.month_name[self.date_to.month]}-{self.date_to.year}"
        else:
            month = f"{self.payslip_run_id.name}"

        domain = [('state', 'not in', ['draft', 'cancel'])]
        if self.payslip_run_id:
            domain += [('payslip_run_id', '=', self.payslip_run_id.id)]
        if self.employee_ids:
            domain += [('employee_id', 'in', self.employee_ids.ids)]
        if self.date_from and self.date_to:
            domain += [('date_from', '>=', self.date_from), ('date_to', '<=', self.date_to)]
        payslip_records = self.env['hr.payslip'].search(domain)

        allowance_headers = list(
            set(payslip_records.line_ids.filtered(lambda l: l.category_id.name == 'Allowance').mapped('name')))
        deduction_headers = list(
            set(payslip_records.line_ids.filtered(lambda l: l.category_id.name == 'Deduction').mapped('name')))

        total_actual_salary = 0
        total_gross_salary = 0
        total_net_payable = 0

        employee_list = []
        for emp in payslip_records.mapped('employee_id'):
            allowance_totals = {name: 0 for name in allowance_headers}
            deduction_totals = {name: 0 for name in deduction_headers}

            worked_days = 0
            actual_salary = 0
            gross_salary = 0
            earnings = 0
            deductions = 0
            net_payable = 0
            for rec in payslip_records.filtered(lambda x: x.employee_id.id == emp.id):
                for line in rec.line_ids:
                    if line.category_id.name == 'Allowance' and line.name in allowance_headers:
                        allowance_totals[line.name] += line.total
                    if line.category_id.name == 'Deduction' and line.name in deduction_headers:
                        deduction_totals[line.name] += line.total

                present_days = self.env['hr.attendance'].search_count([
                    ('employee_id', '=', emp.id),
                    ('checkin_date', '>=', rec.date_from),
                    ('checkin_date', '<=', rec.date_to),
                ])
                day_off = 0
                absent = 0
                total_days = (rec.date_to - rec.date_from).days + 1

                for single_date in (rec.date_from + timedelta(days=n) for n in range(total_days)):
                    weekday = single_date.weekday()
                    # if weekday >= 5:
                    #     day_off += 1
                    # else:
                    weekday_str = str(weekday)
                    if weekday_str not in emp.resource_calendar_id.attendance_ids.mapped('dayofweek'):
                        day_off += 1

                    if str(weekday) in emp.resource_calendar_id.attendance_ids.mapped('dayofweek'):
                        attendance_records = self.env['hr.attendance'].search([
                            ('employee_id', '=', emp.id),
                            ('checkin_date', '=', single_date)
                        ])
                        if not attendance_records:
                            leave_record = self.env['hr.leave'].search([
                                ('employee_id', '=', emp.id),
                                ('request_date_from', '<=', single_date),
                                ('request_date_to', '>=', single_date),
                                ('state', '=', 'validate')
                            ], limit=1)

                            if not leave_record:
                                absent += 1

                public_holidays = sum(self.env['hr.leave'].search([
                    ('employee_id', '=', emp.id),
                    ('request_date_from', '>=', rec.date_from),
                    ('request_date_to', '<=', rec.date_to),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.name', '=', 'Public Holiday')
                ]).mapped('number_of_days'))

                paid_leaves = sum(self.env['hr.leave'].search([
                    ('employee_id', '=', emp.id),
                    ('request_date_from', '>=', rec.date_from),
                    ('request_date_to', '<=', rec.date_to),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.name', 'not in', ['Unpaid'])
                ]).mapped('number_of_days'))

                sundays = sum(1 for n in range(total_days)
                              if (rec.date_from + timedelta(days=n)).weekday() == 6)

                leaves = self.env['hr.leave'].search([
                    ('employee_id', '=', emp.id),
                    ('request_date_from', '<=', rec.date_to),
                    ('request_date_to', '>=', rec.date_from),
                    ('state', '=', 'validate'),
                    ('holiday_status_id.name', 'not in', ['Short Leave'])
                ])

                leave_days = sum(leave.number_of_days for leave in leaves)



                # worked_days += present_days + day_off + public_holidays + paid_leaves
                worked_days += present_days + sundays + leave_days

                actual_salary = rec.contract_id.wage
                total_actual_salary += actual_salary
                gross_salary += (actual_salary / ((rec.date_to - rec.date_from).days + 1)) * worked_days
                total_gross_salary += gross_salary

            employee_data = {
                'emp_id': str(emp.barcode),
                'name': emp.name,
                'department': emp.department_id.name,
                'designation': emp.job_id.name,
                'actual_salary': actual_salary,
                'gross_salary': gross_salary,
                'worked_days': worked_days,
                'earnings': earnings,
                'deductions': deductions,
                'net_payable': net_payable,
            }
            employee_data.update(allowance_totals)
            employee_data.update(deduction_totals)
            employee_list.append(employee_data)

        data = {
            'form_data': self.read()[0],
            'employee_list': employee_list,
            'allowance_headers': allowance_headers,
            'deduction_headers': deduction_headers,
            'month': month,
            'total_actual_salary': total_actual_salary,
            'total_gross_salary': total_gross_salary,
            'total_net_payable': total_net_payable,

        }

        return self.env.ref('salary_sheet_report.salary_sheet_excel').report_action(self, data=data)
