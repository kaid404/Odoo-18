# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
from odoo import models, api, fields, _
import time
from dateutil.relativedelta import relativedelta

from odoo.tools.safe_eval import safe_eval
import logging

_logger = logging.getLogger(__name__)
class HrPayslip(models.Model):
    _inherit = 'hr.payslip'



    def _generate_pdf(self):
        filtered_payslips = self.filtered(lambda a: a.state == 'paid')
        mapped_reports = filtered_payslips._get_pdf_reports()
        generic_name = _("Payslip")
        template = self.env.ref('hr_payroll.mail_template_new_payslip', raise_if_not_found=False)
        for report, payslips in mapped_reports.items():
            for payslip in payslips:
                pdf_content, dummy = self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, payslip.id)
                if report.print_report_name:
                    pdf_name = safe_eval(report.print_report_name, {'object': payslip})
                else:
                    pdf_name = generic_name
                attachments_vals_list = {
                    'name': f"{pdf_name}.pdf",
                    'type': 'binary',
                    'raw': pdf_content,
                    'res_model': payslip._name,
                    'res_id': payslip.id
                }
                
                # Send email to employees
                attachment_id = self.env['ir.attachment'].sudo().create(attachments_vals_list)
                if template:
                    email_send = template.send_mail(payslip.id, email_layout_xmlid='mail.mail_notification_light')
                    send_email = self.env['mail.mail'].search([('id','=',email_send)])
                    send_email.write({'unrestricted_attachment_ids':attachment_id.ids})
                    send_email.send()
                    
        

    def action_payslip_done(self):
        print('action_payslip_done')
        res = super(HrPayslip, self.with_context(payslip_generate_pdf_direct=False)).action_payslip_done()
        payslip_line_obj = self.env['payslip.line']
        slip_line_obj = self.env['hr.payslip.line']
        skip_installment_obj = self.env['hr.skip.installment']
        for payslip in self:
            advance_salary_ids = self.env['hr.advance.salary'].search(
                ['|', '&', ('payment_start_date', '>=', payslip.date_from),
                 ('payment_start_date', '<=', payslip.date_to),
                 ('payment_start_date', '<=', payslip.date_from),
                 ('employee_id', '=', payslip.employee_id.id),
                 ('state', '=', 'paid')])

            _logger.info(advance_salary_ids)
            _logger.info('advance_salary_ids')
            for rec in advance_salary_ids:
                skip_installment_ids = skip_installment_obj.search(
                    [('advance_salary_id', '=', rec.id), ('state', '=', 'approve'), ('date', '>=', payslip.date_from),
                     ('date', '<=', payslip.date_to)])
                if skip_installment_ids:
                    due_date = rec.payment_end_date + relativedelta(months=1)
                    rec.write({'payment_end_date': due_date})
                else:
                    if rec.payment == 'fully':
                        slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id),
                                                          ('code', '=', 'ADV/SAL' + str(rec.id))])
                    else:
                        
                        slip_line_ids = slip_line_obj.search([('slip_id', '=', payslip.id),
                                                              ('code', '=', 'LOAN/SAL/' + str(rec.id))])

                    # duplicate_remove = payslip_line_obj.search([('payslip_id', '=', payslip.id)])
                    if slip_line_ids:
                        _logger.info(slip_line_ids)
                        amount = slip_line_ids.read(['total'])[0]['total']
                        payslip_line_data = {
                            'advance_salary_id': rec.id,
                            'payslip_id': payslip.id,
                            'employee_id': payslip.employee_id.id,
                            'amount': amount if payslip.credit_note else abs(amount),
                            'date': time.strftime('%Y-%m-%d')
                        }
                        payslip_line_obj.create(payslip_line_data)
                        rec.amount_paid += abs(amount)
                        if rec.amount_paid == rec.request_amount:
                            rec.write({'state': 'done'})
                        # rec.action_mail_send(self)
            # if payslip.env.context.get('payslip_generate_pdf'):
            #     _logger.info('dddddddddddddddddddddddddddddddddddddddd')
            #     _logger.info('dddddddddddddddddddddddddddddddddddddddd')
            #     _logger.info('dddddddddddddddddddddddddddddddddddddddd')
            #     _logger.info('dddddddddddddddddddddddddddddddddddddddd')
            #     if payslip.env.context.get('payslip_generate_pdf_direct'):
            #         _logger.info('gggggggggggggggggggggggggggggggggggggg')
            #         _logger.info('gggggggggggggggggggggggggggggggggggggg')
            #         _logger.info('gggggggggggggggggggggggggggggggggggggg')
            #         _logger.info('gggggggggggggggggggggggggggggggggggggg')
            #         payslip._generate_pdf()
            #     else:
            #         _logger.info('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            #         _logger.info('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            #         _logger.info('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            #         _logger.info('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
            #         payslip.write({'queued_for_pdf': True})
            #         payslip_cron = payslip.env.ref('hr_payroll.ir_cron_generate_payslip_pdfs', raise_if_not_found=False)
            #         if payslip_cron:
            #             _logger.info('cccccccccccccccccccccccccccccccccccccccccccccccc')
            #             _logger.info('cccccccccccccccccccccccccccccccccccccccccccccccc')
            #             _logger.info('cccccccccccccccccccccccccccccccccccccccccccccccc')
            #             _logger.info('cccccccccccccccccccccccccccccccccccccccccccccccc')
            #             payslip_cron._trigger()
            #

        return res
    
    @api.model
    def _cron_generate_pdf(self, batch_size=False):
        payslips = self.search([
            ('state', 'in', ['paid']),
            ('queued_for_pdf', '=', True),
        ])
        _logger.info(payslips)
        if payslips:
            return super(HrPayslip,payslips)._cron_generate_pdf(batch_size)
        return False
        
        
    def advance_salary_deduction(self):
        slip_line_obj = self.env['hr.payslip.line']
        skip_installment_obj = self.env['hr.skip.installment']
        for payslip in self:
            duplicate_remove = self.env['payslip.line'].search([('payslip_id', '=', payslip.id),('advance_salary_id','!=',False)])
            print(duplicate_remove)
            for f in duplicate_remove:
                f.advance_salary_id.amount_to_pay += f.amount
                f.advance_salary_id.amount_paid -= f.amount
                f.advance_salary_id.deduction_amount = f.amount
                f.advance_salary_id.state = 'paid'
                f.sudo().unlink()

            
            advance_salary_ids2 = self.env['hr.advance.salary'].search(
                ['&', ('payment_start_date', '>=', payslip.date_from),
                 ('payment_start_date', '<=', payslip.date_to),
                 ('employee_id', '=', payslip.employee_id.id),
                 ('state', '=', 'paid'),('payment','=','fully')])

            advance_salary_ids = self.env['hr.advance.salary'].search(
                ['&', ('payment_start_date', '>=', payslip.date_from),
                 ('employee_id', '=', payslip.employee_id.id),
                 ('state', '=', 'paid'),('payment','=','partially'),('payment_end_date', '<=', payslip.date_to)])
            
            advance_salary_ids = self.env['hr.advance.salary'].search(
                ['|', '&', ('payment_start_date', '>=', payslip.date_from),
                 ('payment_start_date', '<=', payslip.date_to),
                 ('payment_start_date', '<=', payslip.date_from),
                 ('employee_id', '=', payslip.employee_id.id),
                 ('state', '=', 'paid')])
            #advance_salary_ids = advance_salary_ids.ids + advance_salary_ids2.ids
            #advance_salary_ids = self.env['hr.advance.salary'].search([('id', 'in', list(set(advance_salary_ids)))])



            print('/???',advance_salary_ids,payslip.employee_id.name)
            rule_ids = self.env['hr.salary.rule'].search(
                [('code', '=', 'ADV/SAL'), ('struct_id', '=', self.struct_id.id)])
            rule_ids2 = self.env['hr.salary.rule'].search(
                [('code', '=', 'LOAN/SAL'), ('struct_id', '=', self.struct_id.id)])
            # rule_ids3 = self.env['hr.salary.rule'].search(
            #     [('code', '=', 'COMPANY/LOAN'), ('struct_id', '=', self.struct_id.id)])
            # rule_ids4 = self.env['hr.salary.rule'].search(
            #     [('code', '=', 'VEH/LOAN'), ('struct_id', '=', self.struct_id.id)])
            print(rule_ids)
            if rule_ids or rule_ids2:
                if rule_ids:
                    rule = rule_ids[0]
                oids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'ADV/SAL')])
                oids2 = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'LOAN/SAL')])
                # oids3 = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'COMPANY/LOAN')])
                # oids4 = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'VEH/LOAN')])
                if oids or oids2:
                    oids.unlink()
                    oids2.unlink()
                    # oids3.unlink()
                    # oids4.unlink()

                _logger.info('ddddddddddddddddddddd')
                _logger.info(advance_salary_ids)
                for rec in advance_salary_ids:
                    rule = 0
                    if rec.payment == 'partially' and rule_ids2:
                        rule = rule_ids2[0]
                        code_12 = 'LOAN/SAL/' + str(rec.id)
                    # elif rec.payment == 'partially' and rec.loan_type.name in 'Comp Loan' and rule_ids3:
                    #     rule = rule_ids3[0]
                    #     code_12 = 'COMP/SAL/' + str(rec.id)
                    # elif rec.payment == 'partially' and rec.loan_type.name in 'Vehicle Loan' and rule_ids4:
                    #     rule = rule_ids4[0]
                    #     code_12 = 'VEH/LOAN/' + str(rec.id)
                    else:
                        if rule_ids:
                            rule = rule_ids[0]
                            code_12 = 'ADV/SAL' + str(rec.id)


                    skip_installment_ids = skip_installment_obj.search([('advance_salary_id', '=', rec.id),
                                                                        ('state', '=', 'approve'),
                                                                        ('date', '>=', payslip.date_from),

                                                                    ('date', '<=', payslip.date_to)])
                    print(rec,'ddddddddddddddddddd333333333',skip_installment_ids)
                    _logger.info('ppppppppppppppooooooooooooo')
                    _logger.info(skip_installment_ids)
                    if not skip_installment_ids and rule != 0:
                        if rec.payment == 'partially':
                            amount = rec.advance_salary_line_ids.filtered(lambda a: payslip.date_from <= a.date <= payslip.date_to).amount
                        else:
                            amount = rec.amount_to_pay
                        slip_line_data = {
                            'slip_id': payslip.id,
                            'salary_rule_id': rule.id,
                            'contract_id': payslip.contract_id.id,
                            'name': rec.name,
                            'code': code_12,
                            'category_id': rule.category_id.id,
                            'sequence': rule.sequence,
                            'appears_on_payslip': rule.appears_on_payslip,
                            # # 'condition_select': rule.condition_select,
                            # 'condition_python': rule.condition_python,
                            # 'condition_range': rule.condition_range,
                            # 'condition_range_min': rule.condition_range_min,
                            # 'condition_range_max': rule.condition_range_max,
                            # 'amount_select': rule.amount_select,
                            # 'amount_fix': rule.amount_fix,
                            # 'amount_python_compute': rule.amount_python_compute,
                            # 'amount_percentage': rule.amount_percentage,
                            # 'amount_percentage_base': rule.amount_percentage_base,
                            # 'register_id': rule.register_id.id,
                            'amount': amount,
                            'total':amount,
                            'employee_id': payslip.employee_id.id,
                        }
                        print('llllll',amount)
                        if abs(slip_line_data['amount']) > rec.amount_to_pay:
                            slip_line_data.update({'amount': rec.amount_to_pay})
                        slip_line_obj.create(slip_line_data)
                        net_ids = slip_line_obj.search([('slip_id', '=', payslip.id), ('code', '=', 'NET')])
                        if net_ids:
                            net_record = net_ids[0]
                            net_ids.write({'amount': net_record.amount - slip_line_data['amount'],'total':net_record.amount - slip_line_data['amount']})


    def compute_sheet(self):
        _logger.info('lllllkkkkkk')
        """
            Override method for calculate advance salary on payslip calculation time
        """
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            # _logger.info('lllh')
            # payslip.tax_deduction()
            payslip.advance_salary_deduction()
        return res
