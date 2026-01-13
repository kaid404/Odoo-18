from odoo import models, fields, api

class TrainingCoursesTaught(models.Model):
    _name = 'training.courses.taught'

    emp_tct_term = fields.Char(string='Term')
    emp_tct_course_id = fields.Char(string='Course ID')
    emp_tct_subject_area = fields.Char(string='Subject Area')
    emp_tct_catalog_nbr = fields.Char(string='Catalog Nbr')
    emp_tct_course_title = fields.Char(string='Course Title')
    emp_tct_class_section = fields.Char(string='Class Section')
    emp_tct_institute = fields.Char(string='Institute')
    emp_tct_credit_hours = fields.Char(string='Credit Hours/Units')

    training_courses_taught_emp_id = fields.Many2one('hr.employee', string='Employee')


class InheritTrainingCoursesTaught(models.Model):
    _inherit = 'hr.employee'

    training_courses_taught_ids = fields.One2many('training.courses.taught', 'training_courses_taught_emp_id', string=' ')
