from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    po_origin = fields.Boolean(compute='check_po_origin')

    @api.depends('invoice_origin')
    def check_po_origin(self):
        for move in self:
            move.po_origin = bool(move.invoice_origin)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_quantity_editable = fields.Boolean(compute='_compute_is_quantity_editable', string="Is Quantity Editable")

    @api.depends('move_id.po_origin')
    def _compute_is_quantity_editable(self):
        for line in self:
            line.is_quantity_editable = line.move_id.po_origin

