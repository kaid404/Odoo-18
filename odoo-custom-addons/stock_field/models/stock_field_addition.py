from odoo import models, fields, api


class StockField(models.Model):
    _inherit = 'stock.move'

    total_stock = fields.Float(string="On Hand", compute="get_total_stock")

    @api.onchange('product_id', 'location_id')
    def get_total_stock(self):
        for rec in self:
            if rec.location_id and rec.product_id:
                stock = self.env['stock.quant'].search([('location_id', '=', rec.location_id.id), ('product_id', '=', rec.product_id.id)])
                rec.total_stock = stock.inventory_quantity_auto_apply

