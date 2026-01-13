from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class EmployeeBonus(models.Model):
    _name = 'employee.bonus'
    _description = 'Employee Bonus'
    _inherit = ['mail.thread']

    name = fields.Char(string="Sequence", readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('employee.bonus'))
    date = fields.Date(string="Date", default=False, required=True)
    fiscal_year = fields.Char(string="Fiscal Year"
                              , compute='_compute_fiscal_year'
                              , store=True)
    state = fields.Selection([('draft', 'Draft'), ('fina_approval', 'Final Approval'), ('done', 'Done')],
                             default='draft', string="State", tracking=True)
    bonus_type = fields.Selection([('half', 'Half'), ('full', 'Full')], default=False, string="Bonus Type",
                                  tracking=True)
    employee_lines = fields.One2many('employee.bonus.line', 'bonus_id', string="Employee Lines", readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)

    total_employees = fields.Integer(string="Total Employees", compute="_compute_totals", store=True)
    gross_total = fields.Float(string="Gross Total", compute="_compute_totals", store=True)
    bonus_total = fields.Float(string="Bonus Total", compute="_compute_totals", store=True)

    @api.depends('employee_lines')
    def _compute_totals(self):
        for record in self:
            record.total_employees = len(record.employee_lines)
            record.gross_total = sum(line.wage for line in record.employee_lines)
            record.bonus_total = sum(line.bonus for line in record.employee_lines)

    @api.depends('date')
    def _compute_fiscal_year(self):
        for r in self:
            if r.date:
                current_date = r.date
                fiscal_year = current_date.year if current_date.month >= 7 else current_date.year - 1
                r.fiscal_year = fiscal_year

    @api.onchange('date')
    def _onchange_date(self):
        if self.date:
            running_contracts = self.env['hr.contract'].search([('state', '=', 'open')])
            running_employee_ids = running_contracts.mapped('employee_id.id')
            active_employees = self.env['hr.employee'].search(
                [('id', 'in', running_employee_ids), ('active', '=', True)]
            )

            # Check existing employees
            existing_employee_ids = set(self.employee_lines.mapped('employee_id.id'))

            # Create new lines only for employees not already present
            new_employee_lines = []
            for employee in active_employees:
                if employee.id not in existing_employee_ids:
                    new_employee_lines.append((0, 0, {
                        'employee_id': employee.id,
                        'bonus': 0.0,
                    }))

            # Only append new lines, keep existing lines
            self.employee_lines = [(5, 0, 0)] + [(4, line.id) for line in self.employee_lines] + new_employee_lines

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('employee.bonus')
        return super(EmployeeBonus, self).create(vals)

    def action_half_bonus(self):
        self._check_bonus_availability('half')
        for line in self.employee_lines:
            line.bonus = line.wage / 2
            self.state = 'fina_approval'
            self.bonus_type = 'half'

    def action_full_bonus(self):
        self._check_bonus_availability('full')
        for line in self.employee_lines:
            line.bonus = line.wage
            self.state = 'fina_approval'
            self.bonus_type = 'full'

    def action_coo_approval(self):
        self.state = 'done'

    def action_reset_to_draft(self):
        self.state = 'draft'
        self.bonus_type = False

    def _check_bonus_availability(self, bonus_type):
        """Check if the employee can avail the selected bonus type within the year."""
        for line in self.employee_lines:
            employee_id = line.employee_id.id
            bonuses = self.env['employee.bonus.line'].search([
                ('bonus_id', '!=', self.id),
                ('bonus_id.state', '=', 'done'),
                ('employee_id', '=', employee_id),
                ('bonus_id.fiscal_year', '=', self.fiscal_year),
            ])
            _logger.info('start')
            _logger.info('bonuses')
            _logger.info(bonuses)
            _logger.info('employee_id')
            _logger.info(employee_id)
            full_bonus_count = sum(1 for bonus in bonuses if bonus.bonus_id.bonus_type == 'full')
            half_bonus_count = sum(1 for bonus in bonuses if bonus.bonus_id.bonus_type == 'half')

            if full_bonus_count > 0:
                raise ValidationError(_(
                    f"Employees has already availed a full bonus this year and cannot avail another bonus."
                ))

            if bonus_type == 'full' and (half_bonus_count > 0):
                raise ValidationError(_(
                    f"Employees has availed a half bonus this year and cannot avail a full bonus."
                ))

            if bonus_type == 'half' and half_bonus_count >= 2:
                raise ValidationError(_(
                    f"Employees has already availed two half bonuses this year and cannot avail another half bonus."
                ))


class EmployeeBonusLine(models.Model):
    _name = 'employee.bonus.line'
    _description = 'Employee Bonus Line'

    bonus_id = fields.Many2one('employee.bonus', string="Bonus", required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    work_location = fields.Many2one(related='employee_id.work_location_id', string="Work Location", required=True)
    name = fields.Char(string="Employee Name", related='employee_id.name', readonly=True)
    badge_id = fields.Char(string="Badge ID", related='employee_id.barcode', readonly=True)
    wage = fields.Monetary(string="Wage", related='employee_id.contract_id.wage', readonly=True)
    bonus = fields.Float(string="Bonus", readonly=False)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    contract_start_date = fields.Date(string="Contract Start Date", related='employee_id.contract_id.date_start',
                                      tracking=True)
    employee_status = fields.Selection(related='employee_id.employee_type', string="Employee Status")
    # total_employees_1 = fields.Integer(related='bonus_id.total_employees', string="Total Employees", readonly=True)
    # total_gross_1 = fields.Float(///related='bonus_id.total_gross', string="Total Gross", readonly=True)
    # total_bonus_1 = fields.Float(related='bonus_id.total_bonus', string="Total Bonus", readonly=True)