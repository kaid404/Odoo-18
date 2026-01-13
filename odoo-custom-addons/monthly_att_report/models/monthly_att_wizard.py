from odoo import models, fields
from datetime import timedelta


class MonthlyAttendanceWizard(models.TransientModel):
    _name = 'monthly.report.wizard'
    _description = 'Monthly Attendance Report Wizard'

    class_id = fields.Many2one('odoocms.class', string='Class', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)

    def print_report(self):

        date_list = []
        date_map = {}

        current_date = self.date_from
        while current_date <= self.date_to:
            date_str = current_date.strftime('%Y-%m-%d')
            date_list.append(date_str)
            date_map[date_str] = (current_date.weekday() == 6)
            current_date += timedelta(days=1)

        attendance_recs = self.env['odoocms.class.attendance'].search([
            ('class_id', '=', self.class_id.id),
            ('date_att', '>=', self.date_from),
            ('date_att', '<=', self.date_to),
        ])

        attendance_data = {}

        for att in attendance_recs:
            date_key = att.date_att.strftime('%Y-%m-%d')

            for line in att.attendance_lines:
                student = line.student_id.name
                attendance_data.setdefault(student, {})

                if date_map.get(date_key):
                    attendance_data[student][date_key] = 'SUN'
                else:
                    attendance_data[student][date_key] = (
                        'P' if line.present else 'A'
                    )

        for student, records in attendance_data.items():
            for dt in date_list:
                if dt not in records:
                    records[dt] = 'SUN' if date_map.get(dt) else 'A'

        data = {
            'class_name': self.class_id.name,
            'date_list': date_list,
            'attendance_data': attendance_data,
        }
        return self.env.ref('monthly_att_report.monthly_att_report_action').report_action(self, data=data)
