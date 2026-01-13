from odoo import models, fields, api


class DisciplinaryRecords(models.Model):
    _inherit = 'hr.employee'

    disc_description = fields.Char(string='Description of Misconduct')
    disc_date = fields.Date(string='Misconduct Date')
    disc_place = fields.Char(string='Place of Misconduct')
    disc_inquiry_headed_by = fields.Many2one('hr.employee', string='Inquiry Headed by')
    disc_punishment_type = fields.Selection([('minor', 'Minor'),('major', 'Major')], string='Type of Punishment')
    disc_remarks = fields.Char(string='Remarks')
    disc_documents = fields.Binary(string='Documents Attached')
    disc_action_type = fields.Many2one('disciplinary.action', string='Disciplinary Action Type')

class DisciplinaryActionType(models.Model):
    _name = 'disciplinary.action'
    _rec_name = 'disc_action_type_name'

    disc_action_type_name = fields.Char(string='Type')

