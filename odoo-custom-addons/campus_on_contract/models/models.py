from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    school_campus = fields.Many2one(related='employee_id.school_campus_id', string='Campus',store=True)
    college_campus = fields.Many2one(related='employee_id.campus_id', string='Campus',store=True)
    show_school = fields.Boolean( compute='show_school_field',string='Show School', default=True)
    show_college = fields.Boolean( compute='show_college_field',string='Show College', default=True)

    @api.depends('employee_id.employee_type_2')
    def show_school_field(self):
        for rec in self:
            if rec.employee_id.employee_type_2 in ['school','ho']:
                rec.show_school = True
            else:
                rec.show_school = False

    @api.depends('employee_id.employee_type_2')
    def show_college_field(self):
        for rec in self:
            if rec.employee_id.employee_type_2 == 'college':
                rec.show_college = True
            else:
                rec.show_college = False
