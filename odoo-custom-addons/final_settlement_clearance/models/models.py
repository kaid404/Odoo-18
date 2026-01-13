from odoo import models, fields, api


class EmployeeFinalSettlement(models.Model):
    _inherit = 'employee.final.settlement'

    librarian_report = fields.Selection([('clear','Clear'),('not_clear','Not Clear')], string='Librarian Report')
    it_report_ids = fields.Many2many('it.report', string='IT Report')
    canteen_report = fields.Selection([('clear','Clear'),('not_clear','Not Clear')], string='Canteen Report')
    comments = fields.Html(string='Comments')



class ITReport(models.Model):
    _name = 'it.report'

    sequence = fields.Integer('Sequence')
    name = fields.Char(string='Description')