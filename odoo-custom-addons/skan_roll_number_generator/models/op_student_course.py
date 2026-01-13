from odoo import models, fields, api
from datetime import datetime

class Admission(models.Model):
    _inherit = 'op.admission'

    application_number = fields.Char(string='Application Number', readonly=True)
    campus_id = fields.Many2one('odoocms.campus', string='Campus', required=True)

    _sql_constraints = [
        ('unique_application_number', 'unique(application_number)', 'Application Number must be unique.')
    ]

    @api.model
    def create(self, vals):
        if not vals.get('application_number') and vals.get('campus_id'):
            campus = self.env['odoocms.campus'].browse(vals['campus_id'])

            campus_code = campus.code.upper() if campus.code else 'XXX'
            current_year = datetime.now().year

            count = self.search_count([
                ('campus_id', '=', campus.id),
                ('create_date', '>=', f'{current_year}-01-01'),
                ('create_date', '<=', f'{current_year}-12-31')
            ])
            sequence = f"{count + 1:04d}"

            vals['application_number'] = f"{campus_code}/{current_year}/{sequence}"

        return super(Admission, self).create(vals)

    @api.onchange('campus_id')
    def _onchange_campus_id(self):
        if self.application_number:
            return {
                'warning': {
                    'title': 'Warning!',
                    'message': 'Changing the campus will not update the Application Number automatically. Create a new record if needed.',
                }
            }
