from odoo import models, fields


import logging


_logger = logging.getLogger(__name__)


class TimeTableReport(models.TransientModel):
    _inherit = 'time.table.report'

    faculty_ids = fields.Many2many('op.faculty', string='Faculties')
    class_id = fields.Many2one('op.academic.year', string='Academic Class', required=True)
    gxs_campus_id = fields.Many2one('gxs.campus', string='Campus',  required=True)



    def generate_pdf_report(self):
        return self.env.ref('timetable_reports.action_faculty_timetable_pdf_report').report_action(self)

    def generate_pdf_class_report(self):
        return self.env.ref('timetable_reports.action_faculty_class_timetable_pdf_report').report_action(self)

    def get_sessions(self, faculty=False):
        domain = [
            ('class_section.class_id', '=', self.class_id.id),
            ('class_section.school_campus_id', '=', self.gxs_campus_id.id),
            ('start_datetime', '>=', self.start_date),
            ('end_datetime', '<=', self.end_date),
        ]

        if faculty:
            domain.append(('faculty_id', '=', faculty.id))

        sessions = self.env['op.session'].search(domain, order='start_datetime')

        return sessions


        
        # tt = self.env['op.session'].search([
        #     ('faculty_id', '=', faculty.id),
        #     ('class_section.class_id', '=', self.class_id.id),
        #     ('class_section.school_campus_id', '=', self.gxs_campus_id.id),
        #     ('start_datetime', '>=', self.start_date),
        #     ('end_datetime', '<=', self.end_date),
        # ], order='start_datetime')
        # _logger.info(tt)
        # _logger.info(faculty)
        # return tt

class OpSession(models.Model):
    _inherit = 'op.session'

    section_id = fields.Many2one('class.section', string='Section')
    class_name = fields.Many2one(related='section_id.class_id', string='Class')
    # manin_class = fields.many2one(related='faculty_ids.class_id')

