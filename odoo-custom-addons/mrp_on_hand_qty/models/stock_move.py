from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    on_hand_qty = fields.Float(string="On Hand", compute='_compute_on_hand_qty', store=False)

    @api.depends('product_id', 'location_id')
    def _compute_on_hand_qty(self):
        for move in self:
            quant = self.env['stock.quant'].search([
                ('product_id', '=', move.product_id.id),
                ('location_id', '=', move.location_id.id)
            ], limit=1)
            move.on_hand_qty = quant.quantity if quant else 0.0

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    total_on_hand_qty = fields.Float(string="Total On Hand", compute='_compute_total_on_hand_qty', store=False)

    def _compute_total_on_hand_qty(self):
        for picking in self:
            picking.total_on_hand_qty = sum(picking.move_ids.mapped('on_hand_qty'))


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    on_hand_qty = fields.Float(string="On Hand", compute='_compute_on_hand_qty', store=False)

    @api.depends('product_id', 'order_id.picking_type_id')
    def _compute_on_hand_qty(self):
        for rec in self:
            qty = 0.0
            product = rec.product_id
            picking_type = rec.order_id.picking_type_id

            if product and picking_type and picking_type.default_location_dest_id:
                location = picking_type.default_location_dest_id
                qty = product.with_context({'location': location.id}).qty_available

            rec.on_hand_qty = qty
