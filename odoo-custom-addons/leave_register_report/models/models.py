from odoo import models, fields, api
from datetime import date,datetime
import calendar
from odoo.tools import html2plaintext
import re



class LeaveRegisterReport(models.TransientModel):
    _name = 'leave.register.report'

    month = fields.Selection(
        [(str(i), calendar.month_name[i]) for i in range(1, 13)],
        string="Month",
        required=True
    )
    year = fields.Integer(string="Year", required=True, default=lambda self: date.today().year)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, readonly=True)
    employee_id = fields.Many2many('hr.employee', string='Employees')
    department_id = fields.Many2many('hr.department', string='Departments')
    filter_by = fields.Selection([
        ('company', 'Company '),
        ('employees', 'Employees'),
        ('departments', 'Departments'),
    ], string='Filter By', default=False)

    def print_report(self):
        month_int = int(self.month)
        date_from = date(self.year, month_int, 1)
        last_day = calendar.monthrange(self.year, month_int)[1]
        date_to = date(self.year, month_int, last_day)

        domain = [
            ('request_date_from', '>=', date_from),
            ('request_date_to', '<=', date_to),
            ('leave_encashed_check', '!=', True),
            ('state', 'in', ['validate','validate1'])
        ]

        if self.filter_by == 'company' and self.company:
            domain.append(('company_id', '=', self.company.id))

        elif self.filter_by == 'employees' and self.employee_id:
            domain.append(('employee_id', 'in', self.employee_id.ids))

        elif self.filter_by == 'departments' and self.department_id:
            domain.append(('employee_id.department_id', 'in', self.department_id.ids))


        leaves = self.env['hr.leave'].search(domain, order='request_date_from asc')


        results = []

        for leave in leaves:
            emp = leave.employee_id

            req_date_from = leave.original_date_from.date().strftime('%d-%b-%Y')
            req_days = leave.original_days
            req_date_to = leave.original_date_to.date().strftime('%d-%b-%Y')

            approve_date_from = leave.request_date_from.strftime('%d-%b-%Y')
            approve_days = leave.number_of_days
            approve_date_to = leave.request_date_to.strftime('%d-%b-%Y')


            data = {
                'code': emp.barcode,
                'name': emp.name,
                'father_name': emp.x_studio_father_name,
                'cnic': emp.identification_id,
                'dob': emp.birthday,
                'department': emp.department_id.name,
                'job': emp.job_id.name,
                'req_date_from': req_date_from,
                'req_days': req_days,
                'req_date_to': req_date_to,
                'approve_date_from': approve_date_from,
                'approve_days': approve_days,
                'approve_date_to': approve_date_to,
            }

            results.append(data)

        print(results)

        final_data = {'leaves': results,'date': datetime.now().strftime('%d-%b-%Y %I:%M %p'),'company_name':self.env.company.name,
                        'req_date_from_display': date_from.strftime('%d-%b-%Y'),
                        'req_date_to_display': date_to.strftime('%d-%b-%Y'),
                        'app_date_from_display': date_from.strftime('%d-%b-%Y'),
                        'app_date_to_display': date_to.strftime('%d-%b-%Y'),}

        return self.env.ref('leave_register_report.action_leave_register_report').report_action(self, final_data)


