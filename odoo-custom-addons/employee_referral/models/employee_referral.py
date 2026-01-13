from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HRDepartment(models.Model):
    _inherit = 'hr.employee'

    referral_1 = fields.Many2one('hr.employee', string="First Referral", store=True, tracking=True)
    referral_2 = fields.Many2one('hr.employee', string="Second Referral", store=True, tracking=True)
    external_ref = fields.Char(string='External Referral', tracking=True)
