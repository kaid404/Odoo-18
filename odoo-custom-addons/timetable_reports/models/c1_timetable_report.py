from odoo import fields, models, api
from datetime import datetime


class C1TimetableReport(models.AbstractModel):
    _name = "report.timetable_reports.c1_timetable_xlsx"
    _inherit = 'report.report_xlsx.abstract'

    def get_period_number(self, start_time):
        """Map start time to period number"""
        time_table = [
            ('10:00', 1),
            ('10:30', 2),
            ('11:00', 3),
            ('11:30', 4),
            ('12:00', 5),
            ('12:30', 6),
            ('13:00', 7),
            ('13:30', 8),
        ]
        time_str = start_time.strftime('%H:%M')
        for t, p in time_table:
            if time_str <= t:
                return p
        return 8

    def generate_xlsx_report(self, workbook, data, objs):
        sheet = workbook.add_worksheet('C2 Timetable Report')

        # Formats
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center', 'bg_color': '#F4B084'})
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
        border_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        vertical_day_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})

        # Fetch sessions and faculties
        data = self.env['time.table.report'].search([],limit=1, order='id desc')
        sessions = self.env['op.session'].search([], order='start_datetime')
        faculties = sessions.mapped('faculty_id')
        faculty_col_map = {faculty.id: idx * 6 + 2 for idx, faculty in enumerate(faculties)}  # Each faculty gets 6 columns

        # Headers
        last_col = len(faculties) * 6 + 1
        sheet.merge_range(0, 0, 0, last_col, 'C2 Timetable Report', title_format)
        sheet.merge_range(1, 0, 2, 1, 'Format C-II', header_format)
        sheet.merge_range(1, 2, 2, last_col, 'Teacher Timetable', header_format)
        sheet.merge_range(3, 0, 4, 0, 'Class\nTeacher', header_format)
        sheet.merge_range(3, 1, 4, 1, 'Period', header_format)

        # Faculty sub-headers
        session_fields = ['Subject', 'Classroom', 'Course', 'Year', 'Type', 'Time']
        for faculty in faculties:
            base_col = faculty_col_map[faculty.id]
            sheet.merge_range(3, base_col, 3, base_col + 5, faculty.name, header_format)
            for i, field in enumerate(session_fields):
                sheet.write(4, base_col + i, field, header_format)

        # Layout: reserve max 8 rows per day for periods
        start_row = 5
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        day_row_map = {}
        for day in days:
            vertical_text = '\n'.join(day.upper())
            row_start = start_row
            row_end = start_row + 7
            sheet.merge_range(row_start, 0, row_end, 0, vertical_text, vertical_day_format)
            day_row_map[day] = row_start
            for i in range(8):
                sheet.write(row_start + i, 1, str(i + 1), border_format)
                for col in range(2, last_col + 1):
                    sheet.write(row_start + i, col, '', border_format)
                sheet.set_row(row_start + i, 20)
            start_row += 8

        # Column widths
        for col in range(0, last_col + 1):
            sheet.set_column(col, col, 18)

        # Fill sessions: grouped by day and period
        for day in days:
            day_sessions = sessions.filtered(lambda s: s.start_datetime.strftime('%A') == day)

            # Group sessions by period
            period_sessions = {}
            for session in day_sessions:
                period = self.get_period_number(session.start_datetime)
                if period not in period_sessions:
                    period_sessions[period] = []
                period_sessions[period].append(session)

            for period, sess_list in period_sessions.items():
                row = day_row_map[day] + (period - 1)
                for session in sess_list:
                    base_col = faculty_col_map.get(session.faculty_id.id)
                    if base_col is None:
                        continue
                    values = [
                        session.subject_id.name or '',
                        session.classroom_id.name or '',
                        session.course_id.name or '',
                        session.year_id.name or '',
                        session.type or '',
                        f"{session.start_datetime.strftime('%I:%M %p')} - {session.end_datetime.strftime('%I:%M %p')}"
                        if session.end_datetime else '',
                    ]
                    for i, val in enumerate(values):
                        sheet.write(row, base_col + i, val, border_format)
