from odoo import models, api, fields


class QualificationEmployee(models.Model):
    _name = 'hr.qualification'
    _rec_name = 'degree_name'

    degree_name = fields.Char(string="Degree Name")
    degree_duration = fields.Char(string="Duration")


class EducationsInformation(models.Model):
    _name = 'employee.educations'
    _description = "Details of employee's Qualification"

    employee_id = fields.Many2one('hr.employee', string="Employee")
    emp_edu = fields.Many2one('hr.qualification', string="Qualification")
    dgr_name = fields.Char(string="Degree Name")
    dgr_from = fields.Date(string="Duration From")
    dgr_to = fields.Date(string="Duration To")
    specialization = fields.Char(string="Specialization")
    university = fields.Char(string="University")
    edu_country = fields.Many2one('res.country', string="Country")
    t_marks = fields.Float(string="Total Marks / CGPA")
    ob_marks = fields.Float(string="Obtain Marks / CGPA")
    dgr_status = fields.Selection([('completed', 'Completed'), ('inprogress', 'Inprogress')], string="Degree Status")
    dg_duration = fields.Char(string="Duration")
    dgr_verify = fields.Selection([('verified', 'Verified'), ('not_verify', 'Not Varify'), ('applied', 'Applied')],
                                  string="Degree Verification Status")


class ChildrenInformation(models.Model):
    _inherit = 'hr.employee'

    education_id = fields.One2many('employee.educations', 'employee_id', ondelete='cascade', string=' ')
    verify_body_id = fields.One2many('hr.verify.body', 'emp_id', ondelete='cascade', string=' ')


class VerifyBodyModel(models.Model):
    _name = 'hr.verify.body'

    emp_id = fields.Many2one('hr.employee', string="Employee")
    verify_by = fields.Many2one('hr.employee', string="Verified By")
    verify_authority = fields.Selection([('hec', 'HEC'),
                                         ('ibcc', 'IBCC'), ], string="Verification Authority")
    v_date = fields.Date(string="Verification Date")
    remarks = fields.Char(string="Remarks")
    dgr_cate = fields.Selection([('14yr', '14 yr.'),
                                ('16yr', '16 yr.'),
                                ('phd', 'PHD'),
                                ('post_doc', 'Post Doc'), ], string="Degree Category")

    eq_degree = fields.Char(string="Equitant Qualification")
    j_type = fields.Selection([('part_time', 'Part-Time'),
                               ('full_time', 'Full-time'), ], string="Type")
