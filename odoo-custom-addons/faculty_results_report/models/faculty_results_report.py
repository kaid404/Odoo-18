from odoo import models, fields, api

class FacultyResultsReport(models.TransientModel):
    _name = 'faculty.results.report'
    _description = 'Faculty Results Report'

    faculty_id = fields.Many2one('op.faculty', string='Faculty')
    year_id = fields.Many2one('op.academic.term', string='Academic Year')
    exam_type_id = fields.Many2one('op.exam.type', string='Exam Type')

    def print_faculty_report(self):
        year = self.year_id
        faculty  = self.faculty_id
        exam_id  = self.exam_type_id

        sections = self.env['class.section'].search([
            ('year_id', '=', year.id)
        ])
        subject_lines = self.env['class.section.subject.line'].search([
            ('class_section_id', 'in', sections.ids),
            ('op_faculty', '=', faculty.id)
        ])

        subjects = subject_lines.mapped('op_subject')

        faculty_year_title = f"{faculty.name} | {year.name}"
        grouped_data = {faculty_year_title: []}

        for subject in subjects:
            performance_records = self.env['gxs.std.performance'].search([
                ('section_id', 'in', sections.ids),
                ('subject_ids.subject_id', '=', subject.id),
            ])
            marks = 0
            section_name = ''
            for perf in performance_records:
                section_name = perf.section_id.display_name

                for sub in perf.subject_ids:
                    if sub.subject_id.id == subject.id:
                        if exam_id.name == 'Mid Term Examination':
                            marks += sub.mid_result
                        if exam_id.name == 'End of Year Examination':
                            marks += sub.final_result
                        if exam_id.name == 'Sendup Exam':
                            marks += sub.sendup_result
                        if exam_id.name == 'Pre Board':
                            marks += sub.pre_board_result
                        if exam_id.name == 'First Term':
                            marks += sub.first_term_result
                        else:
                            marks = 0

            print(marks)
            status = "Marked" if marks > 0 else "Unmarked"
            grouped_data[faculty_year_title].append({
                'section': section_name,
                'subject': subject.name,
                'exam_type': exam_id.name,
                'status': status,
            })

        data = {
            'results': grouped_data
        }

        return self.env.ref('faculty_results_report.action_faculty_subjects_results_report').report_action(self, data=data)
