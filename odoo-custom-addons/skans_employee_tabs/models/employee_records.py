from odoo import models, fields, api


class ActionType(models.Model):
    _name = 'action.type'
    _rec_name = 'action_type_name'

    action_type_name = fields.Char(string='Type')
    action_type_status = fields.Selection([('active','Active'),('inactive','InActive')],string='Status')


class EmployeeRecords(models.Model):
    _name = 'emp.records'

    record_action_name = fields.Many2one('action.type', string="Action Type")
    record_action_status = fields.Selection([('active','Active'),('inactive','InActive')],compute='compute_details', string="Action Status")
    record_effective_from = fields.Date(string="Effective From")
    record_effective_to = fields.Date(string="Effective To")
    record_placed_at_sch = fields.Many2one('gxs.campus', string="Placed at SCH")
    record_placed_at_clg = fields.Many2one('odoocms.campus', string="Placed at CLG")
    record_oo_date = fields.Date(string="OO Date")
    record_oo_num = fields.Char(string="OO Number", readonly=True, copy=False, default='OO')
    record_salary_amount = fields.Integer(string="Salary on this Action")

    records_emp_id = fields.Many2one('hr.employee')

    @api.model
    def create(self, vals):
        if vals.get('record_oo_num', 'OO') == 'OO':
            seq = self.env['ir.sequence'].next_by_code('emp.oo.number') or '/'
            vals['record_oo_num'] = seq
        return super(EmployeeRecords, self).create(vals)

    @api.onchange('record_placed_at')
    def compute_salary(self):
        for rec in self:
            if rec.records_emp_id:
                rec.record_salary_amount = rec.records_emp_id.contract_id.wage

    @api.onchange('record_action_name')
    def compute_details(self):
        for rec in self:
            rec.record_action_status = rec.record_action_name.action_type_status if rec.record_action_name else False


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_records_ids = fields.One2many('emp.records', 'records_emp_id', string=' ')
