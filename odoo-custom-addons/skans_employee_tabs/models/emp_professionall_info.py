from odoo import models, fields, api
from datetime import date


class ProfessionalDetailsManagement(models.Model):
    _name = 'professional.info'

    emp_is_military_course = fields.Boolean(string='Is Military Course')
    emp_name_in_personal_qualification = fields.Char(string='Name')
    emp_certification_status = fields.Selection([('completed', 'Completed'), ('in_progress', 'InProgress')], string='Status')
    emp_institute_name = fields.Char(string='Institute Name')
    emp_country_name = fields.Many2one('res.country', string='Country')
    emp_from_date = fields.Date(string="Duration From")
    emp_to_date = fields.Date(string="Duration To")
    emp_remarks_field = fields.Char(string='Remarks/ Marks / Results')

    employee_id = fields.Many2one('hr.employee', string='Employee')


class BodyVerificationDetailsManagement(models.Model):
    _name = 'body.verification.details'

    emp_body_verification_status = fields.Selection([('verified', 'Verified'), ('not_verified', 'Not Verified'), ('applied', 'Applied')], string='Verification Status')
    emp_body_verification_date = fields.Date(string='Verification Date')
    emp_body_verification_remarks = fields.Char(string='Remarks')

    emp_id = fields.Many2one('hr.employee', string='Employee')





class EmployeModule(models.Model):
    _inherit = 'hr.employee'

    professional_details_ids = fields.One2many('professional.info', 'employee_id', string=' ')
    verification_details_ids = fields.One2many('body.verification.details', 'emp_id', string=' ')
