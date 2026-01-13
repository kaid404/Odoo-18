from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError


class ExitInterviewForm(models.Model):
    _name = 'op.result.student'

    # student_name = fields.Many2one('op.student', string="Student")
    class_id = fields.Many2one('op.academic.year', string="Class", required=True)
    campus_id = fields.Many2one('gxs.campus', string="Campus")
    year_id = fields.Many2one('op.academic.term', string="Year", required=True)
    section_id = fields.Many2one('class.section', string="Section", required=True)
    exam_type = fields.Many2one('op.exam.type', string="Exam Type", required=True)

    @api.onchange('class_id')
    def _onchange_class_id(self):
        for rec in self:
            rec.section_id = False
            return {'domain': {'section_id': [('class_id', '=', rec.class_id.id)]}}

    def print_result_report(self):
        # performance_record = self.env['milestone.std.performance'].search([
        #     ('year_id', '=', self.year_id.id),
        #     ('class_id', '=', self.class_id.id),
        #     ('section_id', '=', self.section_id.id),
        #     ('campus_id', '=', self.campus_id.id)
        # ])
        domain = [
            ('year_id', '=', self.year_id.id),
            ('class_id', '=', self.class_id.id),
            ('section_id', '=', self.section_id.id),
        ]

        if self.campus_id:
            domain.append(('campus_id', '=', self.campus_id.id))

        performance_record = self.env['milestone.std.performance'].search(domain)

        if not performance_record:
            raise ValidationError('No Record with these details..')

        student_data = []

        for rec in performance_record:
            subject_data = []

            remarks_line = rec.remarks_ids.filtered(
                lambda l: l.exam_type.id == self.exam_type.id
            )
            student_remarks = remarks_line.remarks if remarks_line else ''

            for subject in rec.subject_ids:
                result = self.env['milestone.std.result'].search([
                    ('std_performance_line_id', '=', subject.id)
                ], limit=1)

                result_line = result.std_result_lines_id.filtered(
                    lambda line: line.exam_type.id == self.exam_type.id
                )

                rating_field_info = self.env['milestone.std.result.line.details'].fields_get(['milestone_rating'])
                rating_selection_dict = dict(rating_field_info['milestone_rating']['selection'])

                result_det = []
                result_details = result_line.result_line_details_id
                for detail in result_details:
                    rating_value = detail.milestone_rating
                    rating_label = rating_selection_dict.get(rating_value, 'N/A')

                    result_det.append({
                        'criteria': detail.subline_marks_id.assessment_name,
                        'rating': rating_label
                    })

                subject_data.append({
                    'subject_name': subject.subject_id.name,
                    'result_details': result_det,
                })

                all_attendance = self.env['op.attendance.line'].sudo().search(
                    [('student_id', '=', rec.student_id.id), ('attendance_id.section_name', '=', self.section_id.id)])
                presents = self.env['op.attendance.line'].sudo().search(
                    [('student_id', '=', rec.student_id.id), ('attendance_id.section_name', '=', self.section_id.id),
                     ('present', '=', True)])
                total_days = len(all_attendance)
                present_days = len(presents)

            student_data.append({
                'student_name': rec.student_id.name,
                'campus': rec.campus_id.campus_name,
                'year': self.year_id.name,
                'class': self.class_id.name,
                'section': self.section_id.name,
                'age': (date.today() - rec.student_id.birth_date).days // 365 if rec.student_id.birth_date else 0,
                'subjects': subject_data,
                'att_days': total_days,
                'presents': present_days,
                'remarks': student_remarks,
            })

        final_report = {
            'student_data': student_data
        }

        return self.env.ref('jr_result_report.action_milestone_results_report').report_action(self, data=final_report)

    # def print_result_report(self):
    #     performance_record = self.env['milestone.std.performance'].search([
    #         ('year_id', '=', self.year_id.id),
    #         ('class_id', '=', self.class_id.id),
    #         ('section_id', '=', self.section_id.id)
    #     ])
    #
    #     if not performance_record:
    #         raise ValidationError('No Record with these details..')
    #
    #     student_data = []
    #     subject_data = []
    #
    #     for rec in performance_record:
    #
    #         student_data.append({
    #             'student_name': rec.student_id.name,
    #             'campus': rec.campus_id.campus_name,
    #             'year': self.year_id.name,
    #             'class': self.class_id.name,
    #             'section': self.section_id.name,
    #             'age': (date.today() - rec.student_id.birth_date).days // 365
    #         })
    #
    #         for subject in rec.subject_ids:
    #             result = self.env['milestone.std.result'].search([
    #                 ('std_performance_line_id', '=', subject.id)
    #             ], limit=1)
    #
    #             result_line = result.std_result_lines_id.filtered(
    #                 lambda line: line.exam_type.id == self.exam_type.id
    #             )
    #
    #             rating_field_info = self.env['milestone.std.result.line.details'].fields_get(['milestone_rating'])
    #             rating_selection_dict = dict(rating_field_info['milestone_rating']['selection'])
    #
    #             result_det = []
    #
    #             result_details = result_line.result_line_details_id
    #             for detail in result_details:
    #                 rating_value = detail.milestone_rating
    #                 rating_label = rating_selection_dict.get(rating_value, 'N/A')
    #
    #                 result_det.append({
    #                     'criteria': detail.subline_marks_id.assessment_name,
    #                     'rating': rating_label
    #                 })
    #
    #             subject_data.append({
    #                 'subject_name': subject.subject_id.name,
    #                 'result_details': result_det,
    #             })
    #
    #     final_report = {
    #         'student_data': student_data,
    #         'subject_data': subject_data
    #     }
    #
    #     print(final_report)
    #
    #     return self.env.ref('jr_result_report.action_milestone_results_report').report_action(self, data=final_report)
