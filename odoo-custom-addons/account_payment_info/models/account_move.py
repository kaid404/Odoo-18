from odoo import models, fields, api
import json
from datetime import datetime

class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_date = fields.Date(
        string='Payment Date', compute='_compute_payment_info', store=True
    )
    payment_journal_id = fields.Many2one(
        'account.journal', string='Payment Journal', compute='_compute_payment_info', store=True
    )

    @api.depends('invoice_payments_widget','status_in_payment')
    def _compute_payment_info(self):
        for move in self:
            move.payment_date = False
            move.payment_journal_id = False

            payment_lines = self.env['account.move.line']

            for line in move.line_ids:
                payment_lines |= (line.matched_debit_ids.mapped('debit_move_id') |
                                  line.matched_credit_ids.mapped('credit_move_id'))

            if payment_lines:
                last_payment = payment_lines.sorted(key=lambda l: l.date, reverse=True)[0]
                move.payment_date = last_payment.date
                move.payment_journal_id = last_payment.journal_id