from odoo import models, fields, api
from datetime import date



class ProjectTypeDetails(models.Model):
    _name = 'type.project'
    _rec_name = 'project_type_name'

    project_type_name = fields.Char(string='Type')
    project_type_desc = fields.Char(string='Description')


class ProjectPositionDetails(models.Model):
    _name = 'position.project'
    _rec_name = 'project_position_name'

    project_position_name = fields.Char(string='Position')
    project_position_desc = fields.Char(string='Description')

class ProjectStatusDetails(models.Model):
    _name = 'status.project'
    _rec_name = 'project_status_name'

    project_status_name = fields.Char(string='Position')
    project_status_desc = fields.Char(string='Description')


class TrainingCoursesTypeDetails(models.Model):
    _name = 'type.training.courses'
    _rec_name = 'tc_type_name'

    tc_type_name = fields.Char(string='Type')
    tc_type_desc = fields.Char(string='Description')


class SkillsTypeDetails(models.Model):
    _name = 'type.skills'
    _rec_name = 'skills_type_name'

    skills_type_name = fields.Char(string='Type')
    skills_type_desc = fields.Char(string='Description')

