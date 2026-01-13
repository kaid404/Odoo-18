from odoo import models, fields, api

class ProjectDetails(models.Model):
    _name = 'projects.info'

    emp_type_project_list = fields.Many2one('type.project', string="Type")
    emp_position_list = fields.Many2one('position.project', string="Position")
    emp_status_list = fields.Many2one('status.project', string="Status")
    emp_remuneration = fields.Char(string='Remuneration')
    emp_project_funded = fields.Selection([('funded','Funded'), ('granted', 'Granted')], string='Funded/Granted')
    emp_project_total = fields.Float(string='Total Amount of Project')
    emp_funding_agency = fields.Char(string='Funding Agency')
    emp_funded_amount = fields.Float(string='Funded Amount')
    emp_project_date_from = fields.Date(string='Duration From')
    emp_project_date_to = fields.Date(string='Duration To')
    emp_project_url = fields.Char(string='Link')

    project_emp_id = fields.Many2one('hr.employee', string='Employee')


class InheritProjectDetails(models.Model):
    _inherit = 'hr.employee'

    project_employee_ids = fields.One2many('projects.info', 'project_emp_id', string=' ')
