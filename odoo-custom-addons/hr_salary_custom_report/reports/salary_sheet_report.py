from odoo import models


class SalarySheetXlsx(models.AbstractModel):
    _name = 'report.hr_salary_custom_report.salary_sheet_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        report_data = self.env[
            'report.hr_salary_custom_report.salary_sheet_report_template'
        ]._get_report_data(wizard)

        sheet = workbook.add_worksheet('Salary Sheet')

        title = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'
        })
        subtitle = workbook.add_format({
            'bold': True, 'font_size': 11, 'align': 'center'
        })
        header = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        cell = workbook.add_format({
            'border': 1
        })
        left = workbook.add_format({
            'border': 1, 'align': 'left'
        })
        center = workbook.add_format({
            'border': 1, 'align': 'center'
        })
        right = workbook.add_format({
            'border': 1, 'align': 'right'
        })
        total = workbook.add_format({
            'bold': True, 'border': 1
        })

        widths = [
            14, 28, 22,  # A-C Code, Name, Designation
            12, 12, 12, 13, 14,  # D-H Attendance (FIXED)
            18, 18, 18,  # I-K Salary figures
            14, 14, 14,  # L-N Salary/day, work, encash (M fixed)
            15, 16, 18,  # O-Q Salary days, allowance, gross
            18, 22,  # R-S Umrah, Bank (R fixed)
            14, 16, 12,  # T-V Food, Absentee, EOBI (T,U fixed)
            16, 16,  # W-X Loan, Fine
            18, 18,  # Y-Z Advance, Crockery
            20,
            18
        ]

        for i, w in enumerate(widths):
            sheet.set_column(i, i, w)

        row = 0

        sheet.merge_range(row, 0, row, 27, report_data['company_name'], title)
        row += 1

        sheet.merge_range(
            row, 0, row, 27,
            f"Salary Sheet - {report_data['period_name']}",
            subtitle
        )
        row += 2

        for dept in report_data.get('departments', []):

            sheet.merge_range(
                row, 0, row, 27,
                f"Department: {dept['department_name']} "
                f"(Employees: {dept['dept_totals']['employee_count']})",
                total
            )
            row += 1

            sheet.merge_range(
                row, 0, row, 27,
                f"Total Employees: {dept['dept_statistics']['total_employees']} | "
                f"New Joining: {dept['dept_statistics']['new_joinings']} | "
                f"Resigned: {dept['dept_statistics']['resigned_employees']}",
                left
            )
            row += 1

            headers = [
                'Employee Code',
                'Employee Name',
                'Designation',
                'Present Days',
                'Absent Days',
                'Leave Days',
                'Paid Leaves',
                'Unpaid Leaves',
                'Basic Salary',
                'Earned Salary',
                'Outstanding Amount',
                'Salary Per Day',
                'Working Days',
                'Encashment',
                'Salary Days',
                'Allowance',
                'Gross Salary',
                'Umrah Deduction',
                'Bank Account',
                'Food Overage',
                'Absentee Deduction',
                'EOBI',
                'Loan Deduction',
                'Fine / Debt',
                'Current Advance',
                'Crockery Damage',
                'Pro Outstanding',
                'Net Salary'
            ]

            for col, h in enumerate(headers):
                sheet.write(row, col, h, header)

            row += 1

            for emp in dept['employees']:
                values = [
                    emp.get('emp_code'),
                    emp.get('emp_name'),
                    emp.get('designation'),
                    emp.get('present_days'),
                    emp.get('absent_days'),
                    emp.get('leave_days'),
                    emp.get('pl'),
                    emp.get('unpaid_leaves'),
                    emp.get('wage'),
                    emp.get('basic_salary'),
                    emp.get('out_standing'),
                    emp.get('salary_day'),
                    emp.get('work_days'),
                    emp.get('encashment_days'),
                    emp.get('salary_days'),
                    emp.get('allowance'),
                    emp.get('gross_salary'),
                    emp.get('umra_dept'),
                    emp.get('bank_ac'),
                    emp.get('food_over'),
                    emp.get('absnty'),
                    emp.get('eobi'),
                    emp.get('loan_deduct'),
                    emp.get('fine_debt'),
                    emp.get('current_accm'),
                    emp.get('crockery_deduction'),
                    emp.get('pro_out_standing'),
                    emp.get('net_salary'),
                ]

                for col, val in enumerate(values):
                    fmt = right if isinstance(val, (int, float)) else cell
                    sheet.write(row, col, val, fmt)

                row += 1

            sheet.merge_range(row, 0, row, 2, 'Department Total', total)

            dept_total_map = [
                None, None, None,
                'present_days',
                'absent_days',
                'leave_days',
                'paid_leaves',
                'unpaid_leaves',
                'wage',
                'basic_salary',
                'out_standing',
                'salary_day',
                'work_days',
                'encashment_days',
                'salary_days',
                'allowance',
                'gross_salary',
                'umra_dept',
                'bank_ac',
                'food_over',
                'absnty',
                'eobi',
                'loan_deduct',
                'fine_debt',
                'current_accm',
                'crockery_deduction',
                'pro_out_standing',
                'net_salary',
            ]

            for col, key in enumerate(dept_total_map):
                if key:
                    sheet.write(
                        row,
                        col,
                        dept['dept_totals'].get(key, 0),
                        total
                    )

            # sheet.write(row, 3, dept['dept_totals']['present_days'], total)
            # sheet.write(row, 4, dept['dept_totals']['absent_days'], total)
            # sheet.write(row, 26, dept['dept_totals']['net_salary'], total)

            row += 2

        sheet.merge_range(row, 0, row, 27, 'GRAND TOTAL', title)
