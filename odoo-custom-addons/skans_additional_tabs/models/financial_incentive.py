from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    increment_ids = fields.One2many(
        'hr.employee.increment.lines',
        'employee_id',
        string=' '
    )


    bonus_line_ids = fields.One2many(
        'employee.bonus.line',
        'employee_id',
        compute='_compute_employee_bonus_lines',
        string=' '
    )

    bonus_date = fields.Date(related='bonus_line_ids.bonus_id.date')

    def _compute_employee_bonus_lines(self):
        for employee in self:
            bonus_lines = self.env['employee.bonus.line'].search([
                ('employee_id', '=', employee.id),
                ('bonus_id.state', '=', 'done')
            ])
            employee.bonus_line_ids = bonus_lines

