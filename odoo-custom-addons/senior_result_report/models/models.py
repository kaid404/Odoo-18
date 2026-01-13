from odoo import models, fields, api
from datetime import date
 
from odoo.exceptions import ValidationError

class SeniorResultReport(models.TransientModel):
    _name = 'senior.result.wizard'

    # student_id = fields.Many2one('op.student', string="Student")
    class_id = fields.Many2one('op.academic.year', string="Class")
    campus_id = fields.Many2one('gxs.campus', string="Campus")
    year_id = fields.Many2one('op.academic.term', string="Year")
    section_id = fields.Many2one('class.section', string="Section",domain="[('class_id', '=',class_id)]")
    exam_type = fields.Many2one('op.exam.type', string="Exam Type")

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
            'Sendup Exam': 'sendup',
            'Pre Board': 'pre_board',
            'First Term': 'first_term',
        }

        selected_field = exam_field_map.get(self.exam_type.name)
        if not selected_field:
            raise ValidationError(f"Invalid exam type: {self.exam_type.name}")

        valid_records = result_record.filtered(lambda r: getattr(r, selected_field))
        if not valid_records:
            raise ValidationError(
                f"No record found with '{self.exam_type.name}' enabled. Please check the selected exam type."
            )
        print('somethingggggggggggggggggggggggggg')

        course = self.env['op.course'].search([('class_id', '=', self.class_id.id)], limit=1)

        template = self.env['gxs.odoocms.assessment.template'].search([
            ('course_ids', 'in', course.id)
        ], limit=1)

        grade_lines = []
        if template and template.grade_ids:
            for grade in template.grade_ids:
                grade_lines.append({
                    'result': grade.result,
                    'min_per': grade.min_per,
                    'max_per': grade.max_per,
                })


        student_data = []

        for record in valid_records:
            avg_grad = ''
            avg_pr = []
            subject_list = []
            for subject in record.subject_ids:
                if subject.subject_id.g_subject_id.bypass == False:
                    if self.exam_type.name == 'Mid Year Examination':
                        obtained = subject.mid_result
                        grade = subject.grade.result
                        avg_grad = record.grade.result

                    elif self.exam_type.name == 'End of Year Examination':
                        obtained = subject.final_result
                        grade = subject.grade_final.result
                        avg_grad = record.grade.result
                    elif self.exam_type.name == 'Sendup Exam':
                        obtained = subject.sendup_result
                        grade = subject.sendup_grade.result
                        avg_grad = record.sendup_grade.result
                    elif self.exam_type.name == 'Pre Board':
                        obtained = subject.pre_board_result
                        grade = subject.pre_board_grade.result
                        avg_grad = record.pre_board_grade.result
                    elif self.exam_type.name == 'First Term':
                        obtained = subject.first_term_result
                        grade = subject.first_term_grade.result
                        avg_grad = record.first_term_grade.result
                    else:
                        obtained = 0
                        grade = ''
                    if obtained > 0:
                        obtained = round(obtained, 2)
                    else:
                        obtained = 'Absent'
                    avg_pr.append(obtained)

                    std_sect = self.env['gxs.std.result'].sudo().search(
                        [('std_performance_id', '!=', False), ('subject_id', '=', subject.subject_id.id),
                         ('section_id', '=', self.section_id.id), ('year_id', '=', self.year_id.id),
                         ('student_id', '=', record.student_id.id),

                         ], limit=1, order='id desc')
                    total_marks_xyz = 0
                    for std in std_sect.std_result_lines_id:
                        if std.exam_type.id == self.exam_type.id:
                            total_marks_xyz = 0
                            len_xyz = 0
                            for iiii in std.result_line_details_id:
                                if iiii.obtained_marks > 0:
                                    len_xyz += 1
                                    total_marks_xyz += (iiii.total_marks)

                    if self.exam_type.name in ['End of Year Examination','Mid Year Examination']:

                        result = self.env['gxs.std.result.line'].sudo().search(
                            [('std_result_id.std_performance_line_id', '=', subject.id),
                             ('exam_type', '=', self.exam_type.id)])

                        term_pr = 0
                        exam_pr = 0
                        for i in result.result_line_details_id:
                            if i.subline_marks_id.name == 'Exam':
                                exam_pr = i.obtained_marks
                            else:
                                term_pr = term_pr + i.obtained_marks

                        if '9' in self.class_id.display_name or '10' in self.class_id.display_name:
                            obtained =  exam_pr
                                 


                        # avg = obtained / total_marks_xyz * 100
                        
                        avg = 0
                        if total_marks_xyz != 0:
                            avg = obtained / total_marks_xyz * 100
                        subject_list.append({
                            'subject': subject.subject_id.name,
                            'mid_marks': subject.mid_result,
                            'exam_pr': round(exam_pr,2),
                            'term_pr': round(term_pr,2),
                            'obtained_marks': round(obtained,2),
                            'total_marks': total_marks_xyz,
                            'average': round(avg,2),
                            'grade': grade,
                        })
                    else:
                        avg = 0
                        if total_marks_xyz != 0:
                            avg = obtained / total_marks_xyz * 100
                        subject_list.append({
                            'subject': subject.subject_id.name,
                            'mid_marks': obtained,
                            'obtained_marks': round(obtained,2),
                            'total_marks': total_marks_xyz,
                            'average': round(avg,2),
                            'grade': grade,
                        })
    
                    performance_data = {}
    
                    performance_line = record.section_performance_line_ids.filtered(
                        lambda l: l.exam_type.id == self.exam_type.id
                    )
    
                    if performance_line:
                        general_perf_lines = performance_line.performance_line
                        for line in general_perf_lines:
                            performance_data[line.name] = line.performance_type
    
                    all_attendance = self.env['op.attendance.line'].sudo().search(
                        [('student_id', '=', record.student_id.id), ('attendance_id.section_name', '=', self.section_id.id)])
                    presents = self.env['op.attendance.line'].sudo().search(
                        [('student_id', '=', record.student_id.id), ('attendance_id.section_name', '=', self.section_id.id),
                         ('present', '=', True)])
                    total_days = len(all_attendance)
                    present_days = len(presents)
    
                    # print(performance_data)

            numeric_avg = [x if isinstance(x, (int, float)) else 0 for x in avg_pr]

            student_data.append({
                'name': record.student_id.name,
                'exam_type': self.exam_type.name,
                'class_name': record.class_id.name,
                'section': record.section_id.name,
                'year': record.year_id.name,
                'campus': record.campus_id.campus_name,
                'age': (date.today() - record.student_id.birth_date).days // 365 if record.student_id.birth_date else 0,
                'subjects': subject_list,
                'avg_grad': avg_grad,
                'avg_pr': round(sum(numeric_avg)/len(avg_pr),2),
                'performance': performance_data,
                'total_att_days': total_days,
                'present_days': present_days,
                'remarks': performance_line.remarks,
            })

        # if self.exam_type.name == 'Mid Year Examination':
        #
        #     for record in result_record:
        #         subject_list = []
        #         for subject in record.subject_ids:
        #             avg = subject.mid_result / 100 * 100
        #             subject_list.append({
        #                 'subject': subject.subject_id.name,
        #                 'obtained_marks': subject.mid_result,
        #                 'total_marks': 100,
        #                 'average': avg,
        #                 'grade': subject.grade.result
        #             })
        #
        #         student_data.append({
        #             'name': record.student_id.name,
        #             'class_name': record.class_id.name,
        #             'section': record.section_id.name,
        #             'year': record.year_id.name,
        #             'campus': record.campus_id.campus_name,
        #             'age': (date.today() - record.student_id.birth_date).days // 365if record.student_id.birth_date else 0,
        #             'subjects': subject_list,
        #         })
        #
        #
        # else:
        #     for record in result_record:
        #         subject_list = []
        #         for subject in record.subject_ids:
        #             avg = subject.final_result / 100 * 100
        #             subject_list.append({
        #                 'subject': subject.subject_id.name,
        #                 'obtained_marks': subject.mid_term,
        #                 'total_marks': 100,
        #                 'average': avg,
        #                 'grade': subject.grade_final.result
        #             })
        #
        #         student_data.append({
        #             'name': record.student_id.name,
        #             'class_name': record.class_id.name,
        #             'section': record.section,
        #             'year': record.year_id.name,
        #             'campus': record.campus_id.campus_name,
        #             'age': (date.today() - record.student_id.birth_date).days // 365,
        #             'subjects': subject_list,
        #         })
            #
            # for rec in result_record:
            #
            #     student_data.append({
            #         'student_name': rec.student_id.name,
            #         'campus': rec.campus_id.campus_name,
            #         'year': year.name,
            #         'class': rec.class_id.name,
            #         'section': rec.section_id.name,
            #         'age': (date.today() - rec.student_id.birth_date).days // 365
            #     })
            #     for subject in rec.subject_ids:
            #         avg = subject.final_result / 100 * 100
            #         subject_data.append({
            #             'subject_name': subject.subject_id.name,
            #             'obt_marks': subject.final_result,
            #             'total': 100,
            #             'average': avg,
            #             'grade': subject.grade_final.result if subject.grade_final.result else ''
            #         })

        data = {
            'student_data': student_data,
            'grade_lines': grade_lines,

        }
        # print(data)

        return self.env.ref('senior_result_report.action_senior_results_report').report_action(self, data=data)
