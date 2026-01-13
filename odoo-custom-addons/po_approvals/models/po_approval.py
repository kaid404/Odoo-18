from odoo import models, fields, api


class PoApprovals(models.Model):
    _inherit = 'purchase.order'

    show_finance_btn = fields.Boolean(compute='compute_approvals', default=True, store=True)
    show_executive_director_btn = fields.Boolean(compute='compute_approvals', default=True, store=True)
    show_ceo_btn = fields.Boolean(compute='compute_approvals', default=True, store=True)
    show_confirm_btn = fields.Boolean(compute='show_confirm_button', default=True, store=True)


    state = fields.Selection([
        ('draft', 'RFQ'),
        ('finance', 'Finance Approval'),
        ('executive', 'Executive Approval'),
        ('ceo', 'CEO Approval'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], default='draft', string="Status")

    @api.depends('tax_totals', 'state')
    def compute_approvals(self):
        for rec in self:
            total_amount = rec.tax_totals.get('total_amount', 0)

            if total_amount <= 100000:
                rec.show_finance_btn = False
                rec.show_executive_director_btn = True
                rec.show_ceo_btn = True

            elif (total_amount > 100000) and (total_amount <= 200000):
                rec.show_finance_btn = False
                rec.show_executive_director_btn = False
                rec.show_ceo_btn = True

            elif total_amount > 200000:
                rec.show_finance_btn = False
                rec.show_executive_director_btn = False
                rec.show_ceo_btn = False
            else:
                rec.show_finance_btn = True
                rec.show_executive_director_btn = True
                rec.show_ceo_btn = True

    @api.depends('tax_totals', 'state')
    def show_confirm_button(self):
        for rec in self:
            total_amount = rec.tax_totals.get('total_amount', 0)

            if total_amount <= 100000 and rec.state != 'finance':
                rec.show_confirm_btn = False

            elif (total_amount > 100000) and (total_amount <= 200000) and rec.state != 'executive':
                rec.show_confirm_btn = False

            elif total_amount > 200000 and rec.state != 'ceo':
                rec.show_confirm_btn = False

            else:
                rec.show_confirm_btn = True




    def confirm_finance_button(self):
        for rec in self:
            rec.state = 'finance'


    def confirm_executive_button(self):
        for rec in self:
            rec.state = 'executive'


    def confirm_ceo_button(self):
        for rec in self:
            rec.state = 'ceo'


    def button_confirm(self):
        for rec in self:
            rec.state = 'purchase'
