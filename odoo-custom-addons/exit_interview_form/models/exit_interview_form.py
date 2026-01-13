from odoo import models, fields, api


class ExitInterviewForm(models.Model):
    _name = 'exit.interview.form'
    _rec_name = 'interview_emp'

    interview_emp = fields.Many2one('hr.employee', string="Employee Name")
    interview_emp_number = fields.Integer(compute='get_fields_data',string="Employee Number")
    interview_emp_designation = fields.Char(compute='get_fields_data',string="Designation")
    interview_emp_resign_date = fields.Date(string="Date Of Resigning")
    interview_emp_school_head = fields.Char(compute='get_fields_data',string="Head Of School")
    interview_emp_school_name = fields.Char(compute='get_fields_data',string="Name Of School")

    interview_salary_package = fields.Boolean(string="Salary Package")
    interview_benefit_plan = fields.Boolean(string="Benefit Plan")
    interview_work_load = fields.Boolean(string="Work Load")
    interview_further_studies = fields.Boolean(string="Further Studies")
    interview_better_opportunity = fields.Boolean(string="Better Opportunity")
    interview_lack_fairness_promotion = fields.Boolean(string="Lack of Fairness in Promotion")
    interview_org_culture = fields.Boolean(string="Culture of the Organization")
    interview_lack_growth = fields.Boolean(string="Lack of Growth")
    interview_training_development = fields.Boolean(string="Training & Development")
    interview_conflict_manager_employee = fields.Boolean(string="Conflict with Manager/Employee")
    interview_redundant_termination = fields.Boolean(string="Redundant/Termination")
    interview_other_reason = fields.Boolean(string="Other")
    interview_other_reason_text = fields.Char(string="Other Reason (Explain)")

    interview_main_reason_text = fields.Char(string="What is your main reason of leaving this company?")
    interview_suggestion_text = fields.Char(string="Suggestion For Improvement")



    @api.onchange('interview_emp')
    def get_fields_data(self):
        if self.interview_emp:
            self.interview_emp_number = self.interview_emp.barcode
            self.interview_emp_designation = self.interview_emp.job_id.name
            self.interview_emp_school_head = self.interview_emp.parent_id.name
            self.interview_emp_school_name = self.interview_emp.address_id.name