from odoo import models, fields, api


class EmpMandatoryFields(models.Model):
    _inherit = 'hr.employee'