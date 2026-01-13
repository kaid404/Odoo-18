from odoo import models, api, fields


class ChildrenInformation(models.Model):
    _name = 'hr.child.info'
    _description = "'Details of employee's children"

    child_name = fields.Char(string='Children Name' )
    child_gender = fields.Selection([('male','Male'),('female', 'Female'),('other','Other')], string='Gender')
    child_bod = fields.Date(string="Child Birth Date")
    birth_place = fields.Char(string="Birth Place")

    employee_id = fields.Many2one('hr.employee', string='Employee')



class SpouseInformation(models.Model):
    _inherit = 'hr.employee'
    _description = "Details of employee's spouse"

    sp_name = fields.Char(string="Spouse Name")
    sp_dob = fields.Date(string="Date of Birth")
    sp_cnic = fields.Char(string="CNIC No.")
    sp_dom = fields.Date(string="Date of Marriage")
    sp_mp = fields.Char(string="Marriage place")
    sp_profession = fields.Char(string="Profession")
    sp_status = fields.Selection([('serving','Serving'),('retired','Retired'),('others','others')],string="Status")
    sp_designation = fields.Char(string="Designation")
    sp_employer = fields.Char(string="Employer", placeholder='Name or Description')

    child_details_ids = fields.One2many('hr.child.info', 'employee_id', string=' ')





