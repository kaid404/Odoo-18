from odoo import models, fields, api


class GlobalCompanyField(models.AbstractModel):
    _inherit = 'base'

    company_id = fields.Many2one('res.company', string='Company ID')