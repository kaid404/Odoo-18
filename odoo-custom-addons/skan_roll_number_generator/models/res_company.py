from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    campus_code = fields.Char(string="Campus Code")