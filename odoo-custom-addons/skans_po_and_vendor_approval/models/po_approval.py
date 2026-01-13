from odoo import models, fields, api


class PoApprovals(models.Model):
    _inherit = 'purchase.order'

    show_finance_btn = fields.Boolean(compute='compute_finance_btn', default=True, store=True)
    show_executive_director_btn = fields.Boolean(compute='compute_director_btn', default=True, store=True)
    show_ceo_btn = fields.Boolean(compute='compute_ceo_btn', default=True, store=True)

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('finance', 'Finance Director'),
        ('executive', 'Executive Director'),
        ('ceo', 'CEO Approval'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], default='draft', string="Status")

    @api.depends('tax_totals', 'state')
    def compute_finance_btn(self):
        for rec in self:
            total_amount = rec.tax_totals.get('total_amount', 0)

            if total_amount <= 100000 and rec.state == 'draft':
                rec.show_finance_btn = False

            else:
                rec.show_finance_btn = True

    @api.depends('tax_totals', 'state')
    def compute_director_btn(self):
        for rec in self:
            total_amount = rec.tax_totals.get('total_amount', 0)

            if (total_amount > 100000) and (total_amount <= 200000) and rec.state == 'draft':
                rec.show_executive_director_btn = False

            else:
                rec.show_executive_director_btn = True

    @api.depends('tax_totals', 'state')
    def compute_ceo_btn(self):
        for rec in self:
            total_amount = rec.tax_totals.get('total_amount', 0)

            if total_amount > 200000 and rec.state == 'draft':
                rec.show_ceo_btn = False

            else:
                rec.show_ceo_btn = True


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
        for order in self:
            if order.state not in ['draft', 'sent', 'finance', 'executive', 'ceo']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True





