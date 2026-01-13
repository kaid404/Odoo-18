from odoo import models, fields, api


class TeacherUniqueCode(models.Model):
    _inherit = 'op.faculty'

    teacher_unique_code = fields.Char(compute='get_teacher_unique_code',string='Unique Code')

    def get_teacher_unique_code(self):
        for rec in self:
            first_part = rec.first_name[:2] if rec.first_name else ''
            last_part = rec.last_name[:1] if rec.last_name else ''

            rec.teacher_unique_code = first_part + last_part
