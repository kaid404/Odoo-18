from odoo import models
from calendar import monthrange
from datetime import date
from odoo.exceptions import ValidationError


class ReportXlsxConsumption(models.AbstractModel):
    _name = 'report.salary_sheet_report.salary_sheet_documents_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, res):
        sheet = workbook.add_worksheet('Salary Sheet')
        bold = workbook.add_format({'bold': True})
        bold_font_header_date = workbook.add_format(
            {'align': 'left', 'bold': True, 'bg_color': '#8f8e8c', 'font_color': 'black', 'font_size': '18'})
        bold_font_header_date.set_text_wrap()
        bold_font_header_date.set_border()
        bold_font_header = workbook.add_format(
            {'align': 'center', 'bold': True, 'bg_color': '#8f8e8c', 'font_color': 'black'})
        bold_font_header.set_text_wrap()
        bold_font_header.set_border()
        data_font = workbook.add_format(
            {'align': 'center', 'font_color': 'black'})
        data_font.set_text_wrap()
        data_font.set_border()
        location_font = workbook.add_format(
            {'align': 'left', 'bold': True, 'bg_color': '#b8b7b6', 'font_color': 'black', 'font_size': '12'})
        location_font.set_text_wrap()
        location_font.set_border()
        bold_font_total = workbook.add_format(
            {'align': 'center', 'bold': True, 'bg_color': '#e6e4e1', 'font_color': 'black'})
        bold_font_total.set_text_wrap()
        bold_font_total.set_border()
        bold_font_total_grand = workbook.add_format(
            {'align': 'center', 'bold': True, 'bg_color': '#8f8e8c', 'font_color': 'black'})
        bold_font_total_grand.set_text_wrap()
        bold_font_total_grand.set_border()

        sheet.set_column('A:AZ', 20)

        wizard = self.env['salary.sheet'].search([], order='id desc', limit=1, )
        row = 0
        month = f"{data['month']}"
        sheet.merge_range(row, 0, 1, 3, month, bold_font_header_date)

        headers = ['Sr.No', 'Code.', 'Name', 'Department', 'Designation', 'Actual Salary', 'Worked Days',
                   'Gross Salary']
        col = 0
        for header in headers:
            sheet.write(3, col, header, bold_font_header)
            col += 1

        for allowance in data['allowance_headers']:
            sheet.write(3, col, allowance, bold_font_header)
            col += 1
        for deduction in data['deduction_headers']:
            sheet.write(3, col, deduction, bold_font_header)
            col += 1
        sheet.write(3, col, 'Total Earnings', bold_font_header)
        sheet.write(3, col + 1, 'Total Deductions', bold_font_header)
        sheet.write(3, col + 2, 'Net Pay', bold_font_header)

        allowance_totals = {allowance: 0 for allowance in data['allowance_headers']}
        deduction_totals = {deduction: 0 for deduction in data['deduction_headers']}

        total_deductions_sum = 0
        total_earnings_sum = 0
        total_net_payable_sum = 0
        sr_no = 0
        row = 4
        for emp in data.get('employee_list'):
            sr_no += 1
            col = 0
            sheet.write(row, col, sr_no, data_font)
            sheet.write(row, col + 1, emp['emp_id'], data_font)
            sheet.write(row, col + 2, emp['name'], data_font)
            sheet.write(row, col + 3, emp['department'], data_font)
            sheet.write(row, col + 4, emp['designation'], data_font)
            actual_salary = emp['actual_salary']
            sheet.write(row, col + 5, '{:,}'.format(round(actual_salary)), data_font)
            sheet.write(row, col + 6, emp['worked_days'], data_font)
            gross_salary = emp['gross_salary']
            sheet.write(row, col + 7, '{:,}'.format(round(gross_salary)), data_font)

            total_deductions = sum(emp.get(deduction, 0) for deduction in data['deduction_headers'])
            total_earnings = sum(emp.get(allowance, 0) for allowance in data['allowance_headers'])
            gross_salary = emp['gross_salary']
            net_payable = gross_salary + total_earnings - total_deductions

            total_earnings_sum += total_earnings
            total_deductions_sum += total_deductions
            total_net_payable_sum += net_payable

            col = 8
            for allowance in data['allowance_headers']:
                allowance_value = emp.get(allowance, 0)
                sheet.write(row, col, '{:,}'.format(round(allowance_value)), data_font)
                allowance_totals[allowance] += allowance_value
                col += 1
            for deduction in data['deduction_headers']:
                deduction_value = emp.get(deduction, 0)
                sheet.write(row, col, '{:,}'.format(round(deduction_value)), data_font)
                deduction_totals[deduction] += deduction_value
                col += 1

            sheet.write(row, col, '{:,}'.format(round(total_earnings)), data_font)
            sheet.write(row, col + 1, '{:,}'.format(round(total_deductions)), data_font)
            sheet.write(row, col + 2, '{:,}'.format(round(net_payable)), data_font)
            row += 1

        col = 0
        sheet.merge_range(row, col, row, col + 4, 'Total', bold_font_total)
        sheet.write(row, col + 5, '{:,}'.format(round(data['total_actual_salary'])), bold_font_total)
        sheet.write(row, col + 6, '', bold_font_total)
        sheet.write(row, col + 7, '{:,}'.format(round(data['total_gross_salary'])), bold_font_total)

        col = 8
        for allowance in data['allowance_headers']:
            sheet.write(row, col, '{:,}'.format(round(allowance_totals[allowance])), bold_font_total)
            col += 1

        for deduction in data['deduction_headers']:
            sheet.write(row, col, '{:,}'.format(round(deduction_totals[deduction])), bold_font_total)
            col += 1

        sheet.write(row, col, '{:,}'.format(round(total_earnings_sum)), bold_font_total)
        sheet.write(row, col + 1, '{:,}'.format(round(total_deductions_sum)), bold_font_total)
        sheet.write(row, col + 2, '{:,}'.format(round(total_net_payable_sum)), bold_font_total)
