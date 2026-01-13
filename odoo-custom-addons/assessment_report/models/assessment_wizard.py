from odoo import models, fields, api
from datetime import datetime


class AssessmentReport(models.Model):
    _name = 'assessment.report'

    wizard_term = fields.Many2one('odoocms.academic.term', string='Term', required=True)
    wizard_class = fields.Many2one('odoocms.class', string='Class', required=True)
    wizard_assignment = fields.Many2one('odoocms.assessment.component', string='Assignment')

    def check_st_status(self, percentage):
        if percentage > 50:
            return 'PASS'
        else:
            return 'FAIL'


    def generate_report(self):
        wiz_term = self.wizard_term
        wiz_class = self.wizard_class
        wiz_assignment = self.wizard_assignment

        domain = [('term_id', '=', wiz_term.id), ('class_id', '=', wiz_class.id)]

        if wiz_assignment:
            domain += [('assessment_component_id', '=', wiz_assignment.id)]

        assessments = self.env['odoocms.assessment'].search(domain)

        students_data = []
        total_students = 0
        passed = 0
        failed = 0

        for ass in assessments:
            for line in ass.assessment_lines:
                status = self.check_st_status(line.percentage)

                students_data.append({
                    'name': line.student_id.name,
                    'total_marks': line.max_marks,
                    'obt_marks': line.obtained_marks,
                    'percentage': line.percentage,
                    'grade': self.check_st_status(line.percentage),
                })
                total_students += 1
                if status == 'PASS':
                    passed += 1
                else:
                    failed += 1


        report_data = {
            'term': wiz_term.name,
            'class': wiz_class.name,
            'assignment': wiz_assignment.assessment_type_name if wiz_assignment else 'All Assignments',
            'printed_by': self.env.user.name,
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'students': students_data,
            'total_st': total_students,
            'passed_st': passed,
            'failed_st': failed,
        }

        return self.env.ref('assessment_report.action_report_assessments').report_action(self, data=report_data)
