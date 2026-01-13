from odoo import models, api, fields


class ProfessionalRegistration(models.Model):
    _name = 'employee.registration.info'
    _description = "Professional Registration Information"

    reg_body = fields.Char(string='Registration Body' )
    reg_no = fields.Char(string="Reg.No")
    reg_date = fields.Date(string="Date of Reg.")
    valid_upto = fields.Date(string="Valid Upto")
    emp_id = fields.Many2one('hr.employee', string="Employee")

class CollaborationDetails(models.Model):
    _name = 'employee.collaboration'

    emp_id = fields.Many2one('hr.employee', string="Employee")
    details = fields.Char(string="Type/Details")
    from_date = fields.Date(string="Date From")
    to_date = fields.Date(string="Date To")
    organization = fields.Char(string="Organization")
    country = fields.Many2one('res.country',string="Country")
    status = fields.Many2one('status.collaboration',string="Status")


class EmployeeCollaboration(models.Model):
    _inherit = 'hr.employee'

    collab_id = fields.One2many('employee.collaboration','emp_id', string=" ")
    reg_id = fields.One2many('employee.registration.info','emp_id', string=" ")



class StatusCollaboration(models.Model):
    _name = 'status.collaboration'
    _rec_name = 'status'

    collab_id = fields.One2many('employee.collaboration','status', string="Collaboration")
    status = fields.Char(string="Status Name")
    description = fields.Char(string="Description")
