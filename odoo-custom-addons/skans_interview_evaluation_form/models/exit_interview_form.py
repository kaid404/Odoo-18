from odoo import models, fields, api


class ExitInterviewForm(models.Model):
    _name = 'exit.interview.form'
    _rec_name = 'interview_emp'
    description = 'Interview Exit Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    interview_emp = fields.Many2one('hr.employee', string="Employee Name", store=True, tracking=True)
    interview_emp_number = fields.Char(compute='get_fields_data', string="Employee Number", tracking=True)
    interview_emp_designation = fields.Char(compute='get_fields_data', string="Designation", tracking=True)
    interview_emp_resign_date = fields.Date(string="Date Of Resigning", store=True, tracking=True)
    interview_emp_school_head = fields.Char(compute='get_fields_data', string="Head Of School", tracking=True)
    interview_emp_school_name = fields.Char(compute='get_fields_data', string="Name Of School",tracking=True)

    interview_salary_package = fields.Boolean(string="Salary Package", store=True, tracking=True)
    interview_benefit_plan = fields.Boolean(string="Benefit Plan", store=True, tracking=True)
    interview_work_load = fields.Boolean(string="Work Load", store=True, tracking=True)
    interview_further_studies = fields.Boolean(string="Further Studies", store=True, tracking=True)
    interview_better_opportunity = fields.Boolean(string="Better Opportunity", store=True, tracking=True)
    interview_lack_fairness_promotion = fields.Boolean(string="Lack of Fairness in Promotion", store=True,
                                                       tracking=True)
    interview_org_culture = fields.Boolean(string="Culture of the Organization", store=True, tracking=True)
    interview_lack_growth = fields.Boolean(string="Lack of Growth", store=True, tracking=True)
    interview_training_development = fields.Boolean(string="Training & Development", store=True, tracking=True)
    interview_conflict_manager_employee = fields.Boolean(string="Conflict with Manager/Employee", store=True,
                                                         tracking=True)
    interview_redundant_termination = fields.Boolean(string="Redundant / Termination", store=True, tracking=True)
    interview_other_reason = fields.Boolean(string="Other", store=True, tracking=True)
    interview_other_reason_text = fields.Char(string="Other Reason (Explain)", store=True, tracking=True)
    template_id = fields.Many2one('interview.form.template', string="Template", required=True, store=True,
                                  tracking=True)
    line_ids = fields.One2many('exit.interview.form.line', 'exit_id', string="Rating Criteria", store=True,
                               tracking=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id, store=True,
                                 tracking=True)

    interview_main_reason_text = fields.Html(string="What is your main reason of leaving this company?", store=True,)
    interview_suggestion_text = fields.Html(string="Suggestion For Improvement", store=True)
    interview_return_yes = fields.Boolean(string="Yes", store=True, tracking=True)
    interview_return_no = fields.Boolean(string="No", store=True, tracking=True)
    interview_return_maybe = fields.Boolean(string="Maybe", store=True, tracking=True)

    @api.onchange('interview_return_yes')
    def _onchange_return_yes(self):
        if self.interview_return_yes:
            self.interview_return_no = False
            self.interview_return_maybe = False

    @api.onchange('interview_return_no')
    def _onchange_return_no(self):
        if self.interview_return_no:
            self.interview_return_yes = False
            self.interview_return_maybe = False

    @api.onchange('interview_return_maybe')
    def _onchange_return_maybe(self):
        if self.interview_return_maybe:
            self.interview_return_yes = False
            self.interview_return_no = False

    @api.depends('interview_emp')
    def get_fields_data(self):
        for record in self:
            if record.interview_emp:
                record.interview_emp_number = record.interview_emp.barcode
                record.interview_emp_designation = record.interview_emp.job_id.name
                record.interview_emp_school_head = record.interview_emp.parent_id.name
                record.interview_emp_school_name = record.interview_emp.address_id.name
            else:
                record.interview_emp_number = False
                record.interview_emp_designation = False
                record.interview_emp_school_head = False
                record.interview_emp_school_name = False

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.line_ids = [(5, 0, 0)]  # clear existing lines
            self.line_ids = [
                (0, 0, {
                    'criteria': line.criteria,
                    'rating_1': line.rating_1,
                    'rating_2': line.rating_2,
                    'rating_3': line.rating_3,
                    'rating_4': line.rating_4,
                    'rating_5': line.rating_5,
                }) for line in self.template_id.line_ids
            ]


class ExitInterviewFormLine(models.Model):
    _name = 'exit.interview.form.line'
    _description = 'Exit Interview Form Line'

    exit_id = fields.Many2one('exit.interview.form', string="Evaluation Form", ondelete="cascade")
    criteria = fields.Char(string="Criteria")
    # rating = fields.Selection([('5', '5'), ('4', '4'), ('3', '3'), ('2', '2'), ('1', '1')], string="Rating")
    rating_1 = fields.Boolean(string="Very Dissatisfied")
    rating_2 = fields.Boolean(string="Slightly Dissatisfied")
    rating_3 = fields.Boolean(string="Neutral")
    rating_4 = fields.Boolean(string="Slightly Satisfied")
    rating_5 = fields.Boolean(string="Very Satisfied")

    @api.onchange('rating_1')
    def _onchange_rating1_checkboxes(self):
        for rec in self:
            if rec.rating_1:
                rec.rating_2 = rec.rating_3 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_2')
    def _onchange_rating2_checkboxes(self):
        for rec in self:
            if rec.rating_2:
                rec.rating_1 = rec.rating_3 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_3')
    def _onchange_rating3_checkboxes(self):
        for rec in self:
            if rec.rating_3:
                rec.rating_2 = rec.rating_1 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_4')
    def _onchange_rating4_checkboxes(self):
        for rec in self:
            if rec.rating_4:
                rec.rating_2 = rec.rating_3 = rec.rating_1 = rec.rating_5 = False

    @api.onchange('rating_5')
    def _onchange_rating5_checkboxes(self):
        for rec in self:
            if rec.rating_5:
                rec.rating_2 = rec.rating_3 = rec.rating_4 = rec.rating_1 = False
