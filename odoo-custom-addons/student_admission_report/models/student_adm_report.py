# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo import models, fields, api


class StudentAdmissionReport(models.TransientModel):
    _name = 'student.admission.report'
    _description = 'Student Admission Report'

    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

    def action_print_student_report(self):
        domain = []
        date_from = self.date_from
        date_to = self.date_to

        if date_from > date_to:
            raise UserError("Invalid Values")
        else:
            if date_from:
                domain += [('application_date', '>=', date_from)]
            if date_to:
                domain += [('application_date', '<=', date_to)]

            students = self.env['hospital.appointment'].search_read(domain)

