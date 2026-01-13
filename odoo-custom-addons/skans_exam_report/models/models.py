from odoo import models, fields, api
from datetime import datetime
from collections import defaultdict

from odoo.exceptions import ValidationError


class SkansExamReport(models.Model):
    _name = 'skans.exam.report'

    wizard_session = fields.Many2one('op.exam.session', string="Exam Session", required=True)
    # wizard_subject = fields.Many2one('op.exam', string="Subjects", domain="[('session_id', '=', wizard_session)]")
    wizard_class = fields.Many2one('op.course', string="Class", required=True)
    wizard_start_date = fields.Date(string='Start Date')
    wizard_end_date = fields.Date(string='End Date')

    def _calculate_grade(self, marks, total):
        if not total:
            return ''
        percent = (marks / total) * 100
        if percent >= 90:
            return 'A+'
        elif percent >= 80:
            return 'A'
        elif percent >= 70:
            return 'B'
        elif percent >= 60:
            return 'C'
        elif percent >= 50:
            return 'D'
        else:
            return 'F'

    def generate_exam_results_report(self):
        course = self.wizard_class
        start_date = self.wizard_start_date
        end_date = self.wizard_end_date

        session = self.env['op.exam.session'].search([
            ('course_id', '=', course.id),
            ('start_date', '>=', start_date),
            ('end_date', '<=', end_date)
        ], limit=1)

        if not session:
            raise ValidationError("No exam session found for this class and date range 😢")

        # results_dict = {}

        exams = self.env['op.exam'].search([
            ('session_id', '=', session.id),
        ])

        if not exams:
            raise ValidationError("No exams found for this  session")


        # for exam in exams:
        #     print(exam.name)

        result_lines = self.env['op.result.line'].search([
            ('exam_id', 'in', exams.ids)
        ])

        student_result_map = defaultdict(list)
        for line in result_lines:
            if line.student_id:
                student_result_map[line.student_id.id].append(line)

        subjects = course.subject_ids

        results_dict = {}

        for student_id, lines in student_result_map.items():
            student = self.env['op.student'].browse(student_id)
            marksheet_line = next((
                line for line in self.env['op.marksheet.line'].search([('student_id', '=', student.id)])
                if line.result_line and line.result_line.exam_id.session_id.id == session.id
            ), None)

            remarks = marksheet_line.remarks if marksheet_line else 'N/A'


            attendance_register = self.env['op.attendance.register'].search([('course_id', '=', session.course_id.id), ('section_id', '=', session.section_name.id)])

            attendance_sheets = self.env['op.attendance.sheet'].search([
                ('register_id', '=', attendance_register.id)
            ])

            present_count = 0

            for sheet in attendance_sheets:
                for line in sheet.attendance_line:
                    if line.student_id.id == student.id and line.present:
                        present_count += 1

            total_working_days = len(attendance_sheets)
            attendance_days = present_count

            att_key = ''
            attendance_percentage = attendance_days / total_working_days * 100

            if attendance_percentage >= 90:
                att_key += 'E'

            elif attendance_percentage >= 70:
                att_key += 'G'

            elif attendance_percentage >= 50:
                att_key += 'S'

            else:
                att_key += 'NI'




            results_dict[student.id] = {
                'user_id': student.name,
                'campus': student.x_camp_id.campus_name,
                'session_year': f'{session.name} {student.class_id.name}',
                'class': session.class_name.name if session.class_name else '',
                'section': session.section_name.name if session.section_name else '',
                'age': int((datetime.today().date() - student.birth_date).days / 365.25) if student.birth_date else '',
                'teacher_remarks': remarks,
                'working_days': total_working_days,
                'attendance_days': attendance_days,
                'attendance_key': att_key,
                'results': []
            }

            for subject in subjects:
                matching_line = next((l for l in lines if l.exam_id.subject_id.id == subject.id), None)
                total = matching_line.exam_id.total_marks if matching_line else 0
                obtained = matching_line.marks if matching_line else 0
                avg = (obtained / total) * 100 if total else 0
                grade = self._calculate_grade(obtained, total)

                results_dict[student.id]['results'].append({
                    'subject': subject.name,
                    'total_marks': total,
                    'obtained_marks': obtained,
                    'average': round(avg, 2),
                    'grade': grade
                })

        return self.env.ref('skans_exam_report.action_skans_exam_report').report_action(self, data={'data': results_dict})


        # for exam in exams:
        #     result_lines = self.env['op.result.line'].search([
        #         ('exam_id', '=', exam.id)
        #     ])
        #
        #     student_result_map = {}
        #     for line in result_lines:
        #         student = line.student_id
        #         if not student:
        #             continue
        #         student_result_map.setdefault(student.id, []).append(line)
        #
        #     for student_id, lines in student_result_map.items():
        #         student = self.env['op.student'].browse(student_id)
        #
        #         marksheet_line = self.env['op.marksheet.line'].search([
        #             ('student_id', '=', student.id)
        #         ], limit=1)
        #
        #         remarks = marksheet_line.remarks if marksheet_line else ''
        #
        #         if student.id not in results_dict:
        #             results_dict[student.id] = {
        #                 'user_id': student.name,
        #                 'class': exam.class_name.name if exam.class_name else '',
        #                 'section': exam.section_name.name if exam.section_name else '',
        #                 'age': int((datetime.today().date() - student.birth_date).days / 365.25)
        #                 if student.birth_date else '',
        #                 'teacher_remarks': remarks,
        #                 'results': []
        #             }
        #
        #         # Go through each subject in the class
        #         for subject in subjects:
        #             # Try to find matching result line
        #             matching_line = next((l for l in lines if l.exam_id.subject_id.id == subject.id), None)
        #
        #             total = matching_line.exam_id.total_marks if matching_line else 100
        #             obtained = matching_line.marks if matching_line else 0
        #             avg = (obtained / total) * 100 if total else 0
        #             grade = 'A+'  # You can calculate based on avg if needed
        #
        #             results_dict[student.id]['results'].append({
        #                 'subject': subject.name,
        #                 'total_marks': total,
        #                 'obtained_marks': obtained,
        #                 'average': round(avg, 2),
        #                 'grade': grade
        #             })


        # for student in students:
        #
        #     marksheet_line = self.env['op.marksheet.line'].search([('student_id', '=', student.id),], limit=1)
        #     print(marksheet_line)
        #     remarks = marksheet_line.remarks if marksheet_line else ''
        #
        #     student_data = {
        #         'user_id': student.name,
        #         'class': self.wizard_class.name,
        #         'age': int((datetime.today().date() - student.birth_date).days / 365.25) if student.birth_date else '',
        #         'teacher_remarks':remarks,
        #         'results': []
        #     }
        #
        #     for subject in subjects:
        #         domain = [
        #             ('student_id', '=', student.id),
        #             ('exam_id.session_id', '=', self.wizard_session.id),
        #             ('exam_id.class_name', '=', self.wizard_class.id),
        #             ('exam_id.subject_id', '=', subject.id),
        #         ]
        #
        #         if self.wizard_start_date:
        #             domain.append(('exam_id.exam_date', '>=', self.wizard_start_date))
        #         if self.wizard_end_date:
        #             domain.append(('exam_id.exam_date', '<=', self.wizard_end_date))
        #
        #         result_line = self.env['op.result.line'].search(domain, limit=1)
        #
        #         total = result_line.exam_id.total_marks if result_line and result_line.exam_id.total_marks else 100
        #         obtained = result_line.marks if result_line else 0
        #         avg = (obtained / total) * 100 if total else 0
        #         grade = 'A+'
        #
        #         student_data['results'].append({
        #             'subject': subject.name,
        #             'total_marks': total,
        #             'obtained_marks': obtained,
        #             'average': round(avg, 2),
        #             'grade': grade,
        #         })
        #     results_dict[student.id] = student_data
        #
        # print(results_dict)

        #
        # exams = []
        #
        # if self.wizard_subject:
        #     exams = [self.wizard_subject]
        # else:
        #     exams = self.env['op.exam'].search([
        #         ('session_id', '=', self.wizard_session.id)
        #     ])
        #
        # for exam in exams:
        #     result_lines = self.env['op.result.line'].search([
        #         ('exam_id', '=', exam.id)
        #     ])
        #
        #
        #
        #     for line in result_lines:
        #         student = line.student_id
        #         if not student:
        #             continue
        #
        #         if student.id not in results_dict:
        #
        #             marksheet_line = self.env['op.marksheet.line'].search([
        #                 ('student_id', '=', student.id),
        #             ], limit=1)
        #
        #             print(marksheet_line)
        #
        #             remarks = marksheet_line.remarks if marksheet_line else ''
        #
        #             results_dict[student.id] = {
        #                 'user_id': student.name,
        #                 'class': exam.class_name.name if exam.class_name.name else '',
        #                 'section': exam.section_name.name if exam.section_name.name else '',
        #                 'age': int(
        #                     (datetime.today().date() - student.birth_date).days / 365.25) if student.birth_date else '',
        #                 'teacher_remarks': remarks if remarks else 'N/A',
        #                 'results': [],
        #             }
        #             print(remarks)
        #
        #
        #         total = exam.total_marks or 100
        #         obtained = line.marks or 0
        #         grade = 'A+'
        #         avg = (obtained / total) * 100 if total else 0
        #
        #         results_dict[student.id]['results'].append({
        #             'subject': exam.subject_id.name,
        #             'total_marks': total,
        #             'obtained_marks': obtained,
        #             'average': round(avg, 2),
        #             'grade': grade
        #         })
        #
        #     print(results_dict)
        #
