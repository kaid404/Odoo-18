from datetime import timedelta

from odoo import models, fields, api

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    original_date_from = fields.Datetime(string="Original From Date", readonly=True)
    original_date_to = fields.Datetime(string="Original To Date", readonly=True)
    original_days = fields.Integer(string="Original Days", readonly=True)
    leave_encashed_check = fields.Boolean(string='Leave Encashed', default=False)

    @api.model
    def create(self, vals):
        records = super(HrLeave, self).create(vals if isinstance(vals, list) else [vals])

        for rec in records:
            # Only set once
            if rec.request_date_from:
                rec.original_date_from = rec.request_date_from
            if rec.request_date_to:
                rec.original_date_to = rec.request_date_to
            if rec.number_of_days:
                rec.original_days = rec.number_of_days

        return records