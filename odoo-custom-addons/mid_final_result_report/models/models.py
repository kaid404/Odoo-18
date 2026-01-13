from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError

class SeniorResultReport(models.TransientModel):
    _name = 'mid.final.result.wizard'

    # student_id = fields.Many2one('op.student', string="Student")
    class_id = fields.Many2one('op.academic.year', string="Class")
    campus_id = fields.Many2one('gxs.campus', string="Campus")
    year_id = fields.Many2one('op.academic.term', string="Year")
    section_id = fields.Many2one('class.section', string="Section")
    exam_type = fields.Many2one('op.exam.type', string="Exam Type")
    sec_ids = fields.Many2many('class.section', compute='get_class_sections', store=True)

    @api.onchange('class_id')
    def get_class_sections(self):
        for rec in self:
            if rec.class_id:
                sections = self.env['class.section'].search([('class_id', '=', rec.class_id.id)])
                rec.sec_ids = sections.ids
                print('done')


    def print_result_report(self):

        domain = [
            ('year_id', '=', self.year_id.id),
            ('class_id', '=', self.class_id.id),
            ('section_id', '=', self.section_id.id),
        ]

        if self.campus_id:
            domain.append(('campus_id', '=', self.campus_id.id))

        result_record = self.env['gxs.std.performance'].search(domain)

        if not result_record:
            raise ValidationError('No record found with these details.')

        exam_field_map = {
            'Mid Year Examination': 'mid',
            'End of Year Examination': 'final',
        }

        selected_field = exam_field_map.get(self.exam_type.name)
        if not selected_field:
            raise ValidationError(f"Invalid exam type: {self.exam_type.name}")

        valid_records = result_record.filtered(lambda r: getattr(r, selected_field))
        if not valid_records:
            raise ValidationError(
                f"No record found with '{self.exam_type.name}' enabled. Please check the selected exam type."
            )

        student_data = []

        for record in valid_records:
            subject_list = []
            for subject in record.subject_ids:

                if subject.subject_id.g_subject_id and subject.subject_id.g_subject_id.bypass:
                    print(subject.subject_id.name)
                    continue

                if self.exam_type.code == 'MYE':
                    if subject.mid_result > 0:
                        mid_marks = round(subject.mid_result, 2)
                    else:
                        mid_marks = 'Absent'
                    final_marks = '-'
                    grade = subject.grade.result if subject.grade else 'N/A'
                elif self.exam_type.code == 'EOY':
                    if subject.mid_result > 0:
                        mid_marks = round(subject.mid_result, 2)
                    else:
                        mid_marks = 'Absent'
                    if subject.final_result > 0:
                        final_marks = round(subject.final_result, 2)
                    else:
                        final_marks = 'Absent'
                    grade = subject.grade_final.result if subject.grade_final else 'N/A'
                else:
                    mid_marks = '-'
                    final_marks = '-'
                    grade = '-'

                # mid_marks = str(mid_marks) if isinstance(mid_marks, (int, float)) else mid_marks
                # final_marks = str(final_marks) if isinstance(final_marks, (int, float)) else final_marks

                subject_list.append({
                    'subject': subject.subject_id.name,
                    'mid_marks': mid_marks,
                    'final_marks': final_marks,
                    'grade': grade,
                })


            student_data.append({
                'name': record.student_id.name,
                'exam_type': self.exam_type.name,
                'class_name': record.class_id.name,
                'section': record.section_id.name,
                'year': record.year_id.name,
                'campus': record.campus_id.campus_name,
                'age': (date.today() - record.student_id.birth_date).days // 365 if record.student_id.birth_date else 0,
                'subjects': subject_list,
            })

        data = {
            'student_data': student_data,
            'campus': self.campus_id.campus_name if self.campus_id else False,
            'class': f"{self.class_id.name} - {self.section_id.name}",
            # 'section': self.section_id.name,
            'year': self.year_id.name,
            'exam_type': self.exam_type.name,

        }

        return self.env.ref('mid_final_result_report.action_mid_final_results_report').report_action(self, data=data)
