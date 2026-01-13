from odoo import models, fields, api


class GradeSummaryReport(models.TransientModel):
    _name = 'grade.summary.report'

    class_id = fields.Many2one('op.academic.year', string="class")
    campus_id = fields.Many2one('res.company', string="campus")

    def print_grade_summary_report(self):

        courses = self.env['op.course'].search([('class_id', '=', self.class_id.id)])
        students = self.env['op.student'].search([('year_id', '=', self.class_id.id)])

        grade_levels = []
        grade_obj = self.env['op.grade.configuration'].search([])
        for grade in grade_obj:
            grade_levels.append(grade.result)


        subjects = []
        subject_names = []

        for cs in courses:
            for line in cs.subject_ids:
                if line.name not in subjects:
                    subjects.append(line.name)
                    subject_names.append(line.name)

        raw_counts = {grade: {sub: 0 for sub in subjects} for grade in grade_levels}
        total_students = len(students)

        for student in students:
            for sub in subjects:
                result_lines = self.env['gxs.std.performance.line'].search([
                    ('profoma_id.student_id', '=', student.id),
                    ('subject_id.name', '=', sub)
                ])
                for res_line in result_lines:
                    if res_line.grade_final.result in grade_levels:
                        raw_counts[res_line.grade_final.result][sub] += 1

        grade_data = {
            grade: {
                sub: round((raw_counts[grade][sub] / total_students) * 100, 2) if total_students > 0 else 0
                for sub in subjects
            } for grade in grade_levels
        }

        report_data = {
            'subject_names': subject_names,
            'grade_levels': grade_levels,
            'grade_data': grade_data,
        }

        return self.env.ref('grade_summary_report.action_grade_summary_report').report_action(self, data=report_data)




