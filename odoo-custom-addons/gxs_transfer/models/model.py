from odoo import models, fields, api

class GxsStockTransfer(models.Model):
    _inherit = 'stock.picking'

    remarks = fields.Char(string='Remarks')
    transfer_date = fields.Date(string='Transfer Date')
    transfer_datetime = fields.Datetime(string='Transfer DateTime')
    delivered_by = fields.Many2one('hr.employee', string='Delivered By')
    received_by = fields.Many2one('hr.employee', string='Received By')
    packed_count_by = fields.Many2one('hr.employee', string='Packed & Count By')
    checked_count_by = fields.Many2one('hr.employee', string='Checked By')
    bilty_no = fields.Integer(string='Bilty Number')
    number_of_carton = fields.Integer(string='No. of Carton')
    number_of_bundles = fields.Integer(string='No. of Bundles')
    bilty_attachment = fields.Binary(string='Bilty Attachment')
    carton_bundle_attachment = fields.Binary(string='Carton/Bundle Picture')