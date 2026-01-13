from odoo import models, fields, api


class FacultyResultSummaryWizard(models.TransientModel):
    _name = 'faculty.result.summary.wizard'
    _description = 'Faculty Result Summary Wizard'

    academic_term_ids = fields.Many2one(
        'op.academic.term',
        string="Academic Year",
        required=True
    )

    campus_name = fields.Many2one(
        'gxs.campus',
        string="Campus",
    )

    def action_print_report(self):
        domain = []

        # Academic year filter
        if 'academic_year_id' in self.env['milestone.std.performance']._fields:
            domain.append(('academic_year_id', '=', self.academic_term_ids.id))

        # Campus filter from wizard
        if self.campus_name and 'campus_id' in self.env['milestone.std.performance']._fields:
            domain.append(('campus_id', '=', self.campus_name.id))

        # Filter performances first
        performances_all = self.env['milestone.std.performance'].search(domain)

        # Faculties that have matching performances
        faculty_ids = performances_all.mapped('faculty_id').ids
        faculties = self.env['op.faculty'].browse(faculty_ids)

        data_records = []
        for faculty in faculties:
            faculty_perfs = performances_all.filtered(lambda r: r.faculty_id.id == faculty.id)

            # ✅ Unique student IDs
            student_ids = faculty_perfs.mapped('student_id').ids
            total = len(set(student_ids))

            count_A = len(faculty_perfs.filtered(lambda r: getattr(r, 'grade', '') in ['A+', 'A']))
            count_BC = len(faculty_perfs.filtered(lambda r: getattr(r, 'grade', '') in ['B', 'C']))
            count_D = len(faculty_perfs.filtered(lambda r: getattr(r, 'grade', '') in ['D', 'NYS']))

            campus_list = list(set(faculty_perfs.mapped('campus_id.campus_name')))
            campus_display = ', '.join(campus_list) if campus_list else ''

            data_records.append({
                'faculty_name': faculty.name,
                'campus_name': campus_display,
                'A_percent': round((count_A / total) * 100, 2) if total else 0,
                'BC_percent': round((count_BC / total) * 100, 2) if total else 0,
                'D_percent': round((count_D / total) * 100, 2) if total else 0,
                'total_students': total
            })

        # If no matching records
        if not data_records:
            data_records.append({
                'faculty_name': '',
                'campus_name': '',
                'A_percent': 0,
                'BC_percent': 0,
                'D_percent': 0,
                'total_students': 0
            })

        return self.env.ref(
            'faculty_result_summary.faculty_result_summary_pdf_report_action'
        ).report_action(
            [],
            data={
                'records': data_records,
                'academic_year': self.academic_term_ids.name,
                'campus': self.campus_name.campus_name if self.campus_name else False
            }
        )


class FacultyResultSummaryReport(models.AbstractModel):
    _name = 'report.faculty_result_summary.report_faculty_result_summary_pdf'
    _description = 'Faculty Result Summary Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        # Ensure data is at least an empty dict
        data = data or {}

        # Pass docids as empty set if wizard didn't bind to a model
        docs = self.env['op.faculty'].browse(docids) if docids else self.env['op.faculty']

        return {
            'doc_ids': docids,
            'doc_model': 'op.faculty',
            'docs': docs,
            'data': data,
            'company': self.env.company,
        }

