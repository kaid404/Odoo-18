from odoo import models, fields, api
from odoo.exceptions import UserError

from odoo.odoo.api import ondelete


class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('department', 'Department Approved'),
        ('audit', 'Audit Approved'),
        ('finance', 'Finance Approved'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], default='draft', string="Status")

    @api.depends('state', 'move_type')
    def _compute_show_buttons(self):
        for rec in self:
            rec.show_department_button = rec.state == 'draft' and rec.move_type == 'in_invoice'
            rec.show_audit_button = rec.state == 'department' and rec.move_type == 'in_invoice'
            # rec.show_finance_button = rec.state == 'audit' and rec.move_type == 'in_invoice'


    show_department_button = fields.Boolean(compute='_compute_show_buttons')
    show_audit_button = fields.Boolean(compute='_compute_show_buttons')
    # show_finance_button = fields.Boolean(compute='_compute_show_buttons')


    def button_department_approve(self):
        self.write({'state': 'department'})

    def button_audit_approve(self):
        self.write({'state': 'audit'})

    def button_finance_approve(self):
        self.write({'state': 'finance'})


    def action_post(self):
        # if any(move.state != 'finance' for move in self):
        #     raise UserError("Only Finance Approved bills can be confirmed.")
        return super().action_post()
