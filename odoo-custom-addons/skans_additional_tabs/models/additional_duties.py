from odoo import models, fields, api


class AdditionalDuties(models.Model):
    _name = 'additional.duties'

    duties_job = fields.Many2one('hr.job', string='Job Position')
    duties_department = fields.Many2one('hr.department', string='Department')
    duties_additional = fields.Text(string="Additional Duties")


    additional_duties_emp_id = fields.Many2one('hr.employee')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    additional_duties_emp_ids = fields.One2many('additional.duties', 'additional_duties_emp_id')

