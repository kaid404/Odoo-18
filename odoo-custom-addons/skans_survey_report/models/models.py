# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SkansSurveyReport(models.Model):
    _name = 'survey.report'

    survey_id = fields.Many2one('survey.survey', string='Survey', required=True)

    def print_report(self):
        survey_id = self.survey_id.id

        attempts = self.env['survey.user_input'].search([('survey_id', '=', survey_id),('state', '=', 'done')])

        report_data = []

        for att in attempts:
            student = att.student_id
            student_dict = {
                'student_name': student.name,
                'answers': []
            }

            answer_lines = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', att.id)
            ])
            for line in answer_lines:
                answer_display = line.display_name if line.answer_type != 'text' else line.value_text
                student_dict['answers'].append({
                    'name': student.name,
                    'session': att.batch_id.session_id.name,
                    'Pap': att.component_class_id.course_id.name,
                    'eval_date': att.create_date,
                    'description': line.question_id.title,
                    'result': answer_display,
                    'Batch': att.section_id.name,
                })
            report_data.append(student_dict)


        return self.env.ref('skans_survey_report.action_report_skans_surveys').report_action(self, data={'report_data': report_data})

