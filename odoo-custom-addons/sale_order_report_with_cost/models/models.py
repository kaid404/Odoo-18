
from odoo import models, fields, api


class ProductCostPrice(models.Model):
    _inherit = 'sale.order.line'

    standard_cost2 = fields.Float(string='Cost',
                                  compute='_compute_cost_order_line',
                                  tracking=True, readonly=True)

    cost_order_line = fields.Float(
        string='Cost Subtotal',
        compute='_compute_total_order_line',
        currency_field='currency_id',
        store=True
    )

    @api.depends('product_id')
    def _compute_cost_order_line(self):
        for line in self:
            line.standard_cost2 = line.product_id.standard_price

    @api.depends('standard_cost2', 'product_uom_qty')
    def _compute_total_order_line(self):
        for line in self:
            line.cost_order_line = line.standard_cost2 * line.product_uom_qty


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_print_nomi_quotation(self):
        return self.env.ref('sale_order_report_with_cost.action_report_nomi_quotation').report_action(self)
