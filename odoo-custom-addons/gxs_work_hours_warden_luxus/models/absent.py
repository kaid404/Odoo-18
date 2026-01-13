from odoo import fields, models,api
from datetime import datetime ,date
import calendar




class EmployeeGatePass(models.Model):
    _name = 'employee.attendance.absent'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee GatePass"

    badge_id = fields.Char(string='ID #', related='name.barcode')
    amount_deduc = fields.Float(string='Amount Deduct', compute="compute_amount_deduc", store=True)
    date = fields.Date(string='Date')
    time_out = fields.Datetime(string='Time Out')
    time_in = fields.Datetime(string='Time In')
    total_time = fields.Float(string='Total Time', compute='_compute_total_time', store=True)
    name = fields.Many2one('hr.employee', string='Name')
    department = fields.Many2one('hr.department',related='name.department_id', string='Department')
    absent_line_ids = fields.One2many('absent.lines', 'absent_id', string="Absent Days")
    month = fields.Char(string="Month")

    @api.depends('absent_line_ids.deduction_amount')
    def compute_amount_deduc(self):
        for rec in self:
            rec.amount_deduc = sum(line.deduction_amount for line in rec.absent_line_ids)


    def make_absent(self):
        today = date.today()

        # today = date.today()
        month_str = today.strftime('%Y-%m')  # "2025-07"
        year = today.year
        month = today.month
        total_days_in_month = calendar.monthrange(year, month)[1]

        plan = self.env['planning.slot'].search([('new_date', '=', today)]).mapped('employee_id.id')
        attendance = self.env['hr.attendance'].search([('checkin_date', '=', today)]).mapped('employee_id.id')

        absent = list(set(plan) - set(attendance))

        unpaid = self.env["hr.leave"].search([
            ('employee_id', 'in', absent),
            ('request_date_from', '<=', today),
            ('request_date_to', '>=', today),
            ('holiday_status_id.name', '!=', 'Unpaid')
        ]).mapped('employee_id.id')

        absent = list(set(absent) - set(unpaid))

        contracts = self.env['hr.contract'].search([('employee_id', 'in', absent), ('state', '=', 'open')])
        wage_dict = {cn.employee_id.id: cn.wage / total_days_in_month for cn in contracts}

        for emp_id in absent:
            # Check if a record exists for this month
            existing = self.env['employee.attendance.absent'].search([
                ('name', '=', emp_id),
                ('month', '=', month_str)
            ], limit=1)

            if not existing:
                existing = self.env['employee.attendance.absent'].create({
                    'name': emp_id,
                    'month': month_str,
                })

            # Check if today is already in line_ids
            already_logged = existing.absent_line_ids.filtered(lambda l: l.date == today)
            if not already_logged:
                existing.write({
                    'absent_line_ids': [(0, 0, {
                        'date': today,
                        'deduction_amount': wage_dict.get(emp_id, 0.0),
                    })]
                })


        # year = date.today().year
        # month = date.today().month
        # total_days_in_month = calendar.monthrange(year, month)[1]
        #
        #
        #
        # plan = self.env['planning.slot'].search([('new_date', '=', date.today())]).mapped('employee_id.id')
        # attendance = self.env['hr.attendance'].search([('checkin_date', '=', date.today())]).mapped('employee_id.id')
        #
        # absent  = list(set(plan) - set(attendance))
        #
        # unpaid = self.env["hr.leave"].search(
        #     [('employee_id', 'in', absent), ('request_date_from', '>=', date.today()),
        #      ('request_date_to', '<=', date.today()), ('holiday_status_id.name', '!=', 'Unpaid')]).mapped('employee_id.id')
        #
        # absent = list(set(absent) - set(unpaid))
        #
        #
        #
        # # plan = self.env['planning.slot'].search(
        # #     [('employee_id', 'in', absent), ('new_date', '=', date.today())])
        # # allocated_hours = {}
        # # for pl in plan:
        # #     allocated_hours.update({pl.employee_id.id:pl.allocated_hours})
        #
        #
        #
        # wage = {}
        # contract = self.env['hr.contract'].search([('employee_id','in',absent),('state','=','open')])
        # for cn in contract:
        #     # allocated_hours_per_employee = allocated_hours.get(cn.employee_id.id)
        #     # per_hours = cn.wage/total_days_in_month
        #     # per_hours = per_hours/allocated_hours_per_employee
        #     wage.update({cn.employee_id.id:cn.wage/total_days_in_month})
        #
        #
        # for rec in absent:
        #     self.env['employee.attendance.absent'].create({'name':rec,'date':date.today(),'amount_deduc':wage.get(rec)})


class EmployeeAbsentLine(models.Model):
    _name = 'absent.lines'
    _description = "Absent Line"

    absent_id = fields.Many2one('employee.attendance.absent', string="Absent Ref", ondelete="cascade")
    date = fields.Date(string="Date")
    deduction_amount = fields.Float(string="Amount Deduct")


