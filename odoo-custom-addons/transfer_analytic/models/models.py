from odoo import models, fields
from odoo.exceptions import ValidationError


class TransferConsumptionLine(models.Model):
    _inherit = "transfer.consumption.line"

    analytic_distribution = fields.Json()
    analytic_precision = fields.Integer(default=2)
    remarks = fields.Char(string='Remarks')

    product_uom_id = fields.Many2one(
        related='product_id.uom_id',
        string="Unit of Measure",
        readonly=True,
        store=True,
    )


class TransferConsumption(models.Model):
    _inherit = "transfer.consumption"

    analytic_distribution = fields.Json(
        inverse="_inverse_analytic_distribution",
    )

    def _inverse_analytic_distribution(self):
        for rec in self:
            rec.line_ids.write({
                'analytic_distribution': rec.analytic_distribution
            })

    def action_approve_by_admin(self):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']

        for rec in self:
            # if not rec.line_ids:
            #     raise ValidationError("No transfer lines found to approve.")
            # if not rec.quantity_check:
            #     raise ValidationError("⚠️ Please click the 'Check Qty' button before approving this request.")

            rec.product_check = True

            # Filter valid lines (quantity > 0 and avb_quantity > 0)
            valid_lines = [line for line in rec.line_ids if line.quantity > 0 and line.avb_quantity > 0]

            if not valid_lines:
                # No valid lines to transfer, just approve
                rec.approval_stage = 'done'
                continue

            # Group valid lines by destination location
            transfer_map = {}
            for line in valid_lines:
                key = line.dest_location_id.id
                transfer_map.setdefault(key, []).append(line)

            for dest_loc_id, lines in transfer_map.items():
                picking_type = self.env['stock.picking.type'].search([
                    ('sequence_code', 'ilike', 'CONS'),
                    ('code', '=', 'internal'),
                    ('warehouse_id', '=', rec.warehouse_id.id)
                ], limit=1)

                if not picking_type:
                    raise ValidationError("No suitable picking type found for internal transfer.")

                picking = StockPicking.create({
                    'picking_type_id': picking_type.id,
                    'location_id': rec.source_location_id.id,
                    'location_dest_id': dest_loc_id,
                    'origin': rec.name,
                })

                for line in lines:
                    StockMove.create({
                        'name': line.product_id.display_name,
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.quantity,
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': rec.source_location_id.id,
                        'location_dest_id': line.dest_location_id.id,
                        'picking_id': picking.id,
                        'analytic_distribution': line.analytic_distribution,
                    })

                picking.action_confirm()
                picking.action_assign()
                picking.button_validate()

            rec.approval_stage = 'done'
