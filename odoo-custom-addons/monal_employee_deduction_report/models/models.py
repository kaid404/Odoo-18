from odoo import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class MonalDeductionReportEmp(models.TransientModel):
	_name = 'monal.deduction.report.employee'
	_description = "Deduction Report Wizard"
	
	mode_type = fields.Selection([
		('employee', 'Employee Wise'),
		('department', 'Department Wise'),
		('company', 'Company Wise'),
	], string="Mode Type", default='company', required=True)
	
	from_date = fields.Date(
		'From Date',
		default=lambda self: fields.Date.to_string(date.today().replace(day=1)),
		required=True
	)
	to_date = fields.Date(
		"To Date",
		default=lambda self: fields.Date.to_string(
			(datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()
		),
		required=True
	)
	company_id = fields.Many2one(
		'res.company',
		string="Company",
		default=lambda self: self.env.company,
		domain=lambda self: [('id', '=', self.env.company.id)],
	)
	department_ids = fields.Many2many('hr.department', string="Department")
	employee_ids = fields.Many2many('hr.employee', string="Employee")
	
	
	
	deduction_rule_ids = fields.Many2many(
		'hr.salary.rule',
		string="Deduction Type",
		domain="[('id', 'in', rule_domain_ids)]",relation="wiz_deduction_rule_rel",
	)
	rule_domain_ids = fields.Many2many(
		'hr.salary.rule',
		string="Rule Domain Helper", relation="wiz_deduction_rule_domain_rel",
	)
	
	section_ids = fields.Many2many(
		'department.section',
		string="Section",
	)
	
	salary_structure_id = fields.Many2one(
		'hr.payroll.structure',
		string="Salary Structure",
		help="Filter deduction rules by selected salary structure"
	)
	
	@api.onchange('salary_structure_id')
	def _onchange_salary_structure_id(self):
		self.rule_domain_ids = False
		
		domain = [('category_id.code', '=', 'DED')]
		if self.salary_structure_id:
			domain.append(('struct_id', '=', self.salary_structure_id.id))
		
		rules = self.env['hr.salary.rule'].search(domain)
		self.rule_domain_ids = rules.ids
		
		
		
		
	@api.onchange('mode_type')
	def _onchange_mode_type(self):
		if self.mode_type == 'employee':
			self.department_ids = False
			self.company_id = self.env.company
		elif self.mode_type == 'department':
			self.employee_ids = False
			self.company_id = self.env.company
		elif self.mode_type == 'company':
			self.employee_ids = False
			self.department_ids = False
	
	
	def print_report_imp(self):
		domain = [
			('date_from', '>=', self.from_date),
			('date_to', '<=', self.to_date),
			('state', 'in', ['done', 'paid', 'verify']),
		]
		
		if self.mode_type == 'company' and self.company_id:
			domain += [('company_id', '=', self.company_id.id)]
		
		if self.mode_type == 'department' and self.department_ids:
			domain += [('employee_id.department_id', 'in', self.department_ids.ids)]
		
		if self.mode_type == 'employee' and self.employee_ids:
			domain += [('employee_id', 'in', self.employee_ids.ids)]
		
		if self.section_ids:
			domain += [('employee_id.department_id.section_id', 'in', self.section_ids.ids)]
		
		if self.salary_structure_id:
			domain.append(('struct_id', '=', self.salary_structure_id.id))
		
		payslips = self.env['hr.payslip'].search(domain)
		
		# Sort Payslips:
		# 1. By Department name (A → Z)
		# 2. By Wage highest → lowest
		sorted_slips = sorted(payslips, key=lambda s: (
			s.employee_id.department_id.name or '',
			-(s.contract_id.wage if s.contract_id and s.contract_id.wage else 0)
		))
		
		total_deductions = 0
		all_datas = []
		today_date = date.today()  # current date
		for slip in sorted_slips:
			deduction_lines = slip.line_ids.filtered(
				lambda l: l.category_id.code == 'DED' or l.total < 0
			)
			if self.deduction_rule_ids:
				deduction_lines = deduction_lines.filtered(
					lambda l: l.salary_rule_id.id in self.deduction_rule_ids.ids
				)
			for line in deduction_lines:
				all_datas.append({
					'emp_code': slip.employee_id.barcode or '',
					'emp_name': slip.employee_id.name,
					'father_name': 'slip.employee_id.x_studio_father_name',
					'cnic': slip.employee_id.identification_id or '',
					'dob': slip.employee_id.birthday,
					'department': slip.employee_id.department_id.name or '',
					'designation': slip.employee_id.job_id.name or '',
					'joining_date': slip.contract_id.date_start if slip.contract_id else '',
					'doc_no': slip.number or slip.name,
					'doc_date': today_date.strftime('%Y-%m-%d'),
					'sr_no': line.id,
					'line_type': line.name,
					'deduction_amount': line.total,
					'remarks': '---',
				})
				total_deductions += line.total
		data = {'all_datas': all_datas,
		        'total_deductions': total_deductions,
		        }
		return self.env.ref('monal_employee_deduction_report.report_hr_deduction_employee').report_action([], data=data)
