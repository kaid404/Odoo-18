from odoo import models, fields, api
from datetime import datetime, time, timedelta


class CheckFieldAccount(models.Model):
    _inherit = 'account.account'

    show_in_report = fields.Boolean(string='Show in Report', store=True)

class SozoReceiptsAndPaymentsReport(models.Model):
    _name = 'receipts.payments.report'

    rp_date = fields.Date(string='Report Date', required=True)

    def generate_receipts_and_payments_report(self):

        date_selected = self.rp_date
        date_from = datetime.combine(date_selected, time(00, 0, 0))
        date_to = datetime.combine(date_selected, time(23, 59, 59))


        domain = [('date_order', '>=', date_from), ('date_order', '<=', date_to)]

        receipts_data = {}
        payments_data = {}

        receipts = self.env['pos.order'].search(domain)

        for order in receipts:
            for line in order.lines:
                receipt_account = line.product_id.property_account_income_id
                if receipt_account:
                    key = (receipt_account.code, receipt_account.name)
                    amount = line.qty * line.price_unit

                    if key not in receipts_data:
                        receipts_data[key] = 0.0

                    receipts_data[key] += amount

        expense_accounts = self.env['account.account'].search([
            ('account_type', '=', 'expense')
        ])
        expense_account_ids = expense_accounts.ids

        payment_domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('account_id', 'in', expense_account_ids)
        ]

        payments = self.env['account.move.line'].search(payment_domain)

        for line in payments:
            pm_account = line.account_id
            key = (pm_account.code, pm_account.name)
            amount = line.debit

            if key not in payments_data:
                payments_data[key] = 0.0

            payments_data[key] += amount

        cash_bank_accounts = self.env['account.account'].search([
            ('account_type', '=', 'asset_cash'),('show_in_report', '=', True)
        ])
        cash_bank_account_ids = cash_bank_accounts.ids

        opening_date = date_from - timedelta(minutes=1)
        print(opening_date)

        opening_lines = self.env['account.move.line'].search([
            ('date', '<=', opening_date),
            ('account_id', 'in', cash_bank_account_ids)
        ])

        opening_balances = {}
        for line in opening_lines:
            key = (line.account_id.code, line.account_id.name)
            amount = line.balance
            opening_balances[key] = opening_balances.get(key, 0.0) + amount

        # ➕ Receipts (debits)
        cash_receipts_lines = self.env['account.move.line'].search([
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('account_id', 'in', cash_bank_account_ids)
        ])

        receipts_summary = {}
        payments_summary = {}
        for line in cash_receipts_lines:
            key = (line.account_id.code, line.account_id.name)
            receipts_summary[key] = receipts_summary.get(key, 0.0) + line.debit
            payments_summary[key] = payments_summary.get(key, 0.0) + line.credit

        # RECEIPTS DATA

        receipt_report = []
        for (code, name), total in receipts_data.items():
            receipt_report.append({
                'receipt_code': code,
                'receipt_name': name,
                'receipt_total': round(total, 2)
            })

            # PAYMENTS DATA
        payment_report = []
        for (code, name), total in payments_data.items():
            payment_report.append({
                'payment_code': code,
                'payment_name': name,
                'payment_total': round(total, 2)
            })

            # CASH AND BANKS DATA

        cash_bank_report = []
        for account in cash_bank_accounts:
            key = (account.code, account.name)
            opening = opening_balances.get(key, 0.0)
            receipts = receipts_summary.get(key, 0.0)
            payments = payments_summary.get(key, 0.0)
            closing = receipts - payments + opening

            cash_bank_report.append({
                'account_code': account.code,
                'account_name': account.name,
                'opening_balance': round(opening, 2),
                'total_receipts': round(receipts, 2),
                'total_payments': round(payments, 2),
                'closing_balance': round(closing, 2)
            })

        final_report_data = {
            'company_logo': f"data:image/png;base64,{self.env.company.logo.decode('utf-8')}" if self.env.company.logo else None,
            'receipt_data': receipt_report,
            'payment_data': payment_report,
            'cash_bank_data': cash_bank_report,
            'date_from': date_from.strftime('%-m/%-d/%Y %-H:%M:%S'),
            'date_to': date_to.strftime('%-m/%-d/%Y %-H:%M:%S'),
        }

        return self.env.ref('sozo_receipts_and_payments_report.action_report_receipts_payments_report').report_action(self, data=final_report_data)

