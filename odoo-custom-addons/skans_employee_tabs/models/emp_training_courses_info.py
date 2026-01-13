from odoo import models, fields, api

class TrainingCoursesDetails(models.Model):
    _name = 'training.courses'

    emp_type_list_training_courses = fields.Many2one('type.training.courses', string="Type")
    emp_tc_name = fields.Char(string='Name of Training')
    emp_tc_date_from = fields.Date(string='Duration From')
    emp_tc_date_to = fields.Date(string='Duration To')
    emp_tc_center = fields.Char(string='Center/Station')
    emp_tc_organize_by = fields.Char(string='Organized By')
    emp_tc_organizing_body = fields.Char(string='Organizing Body')
    emp_tc_sponsored_by = fields.Char(string='Sponsored By')
    emp_tc_sponsored_body = fields.Char(string='Sponsored Body')

    training_courses_emp_id = fields.Many2one('hr.employee', string='Employee')


class InheritTrainingField(models.Model):
    _inherit = 'hr.employee'

    training_courses_emp_ids = fields.One2many('training.courses', 'training_courses_emp_id', string=' ')
