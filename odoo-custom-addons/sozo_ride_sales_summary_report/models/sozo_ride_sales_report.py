from numpy.ma.core import product
from requests import session
from datetime import datetime
from collections import defaultdict

from odoo import models, fields, api


class SozoRideSalesSummaryReport(models.TransientModel):
    _name = 'ride.sales.summary.report'

    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    session_id = fields.Many2one('pos.session', string='Session')
    category_id = fields.Many2one('product.category', string='Category')

    def generate_ride_sales_summary_report(self):
        date_from = self.date_from
        date_to = self.date_to
        session_id = self.session_id.id
        category_id = self.category_id.id

        domain = [('date_order', '>=', date_from), ('date_order', '<=', date_to)]

        if session_id:
            domain.append(('session_id', '=', session_id))

        sales_data = self.env['pos.order'].search(domain)

        # grouped_data = defaultdict(lambda: {
        #     'ride_name': '',
        #     'category': '',
        #     'qty': 0,
        #     'refund': 0,
        #     'net_qty': 0,
        #     'price_list': [],
        #     'total_amount': 0.0,
        # })
        #
        # for sale in sales_data:
        #     for line in sale.lines:
        #         if category_id and line.product_id.categ_id.id != category_id:
        #             continue
        #
        #         key = line.product_id.id
        #         group = grouped_data[key]
        #
        #         group['ride_name'] = line.product_id.name
        #         group['category'] = line.product_id.categ_id.name or 'Uncategorized'
        #
        #         refund_qty = abs(line.qty) if line.qty < 0 else 0
        #         net_qty = line.qty if line.qty > 0 else 0
        #
        #         group['qty'] += line.qty + refund_qty
        #         group['refund'] += refund_qty
        #         group['net_qty'] += net_qty
        #         group['price_list'].append(line.price_unit)
        #         group['total_amount'] += float(line.qty) * float(line.price_unit)
        #
        # paid_rides = []
        # free_rides = []
        #
        # for group in grouped_data.values():
        #     min_price = min(group['price_list'])
        #     max_price = max(group['price_list'])
        #     price_range = f"{min_price:.2f}" if min_price == max_price else f"{min_price:.2f} - {max_price:.2f}"
        #
        #     ride_summary = {
        #         'ride_name': group['ride_name'],
        #         'category': group['category'],
        #         'qty': group['qty'],
        #         'refund': group['refund'],
        #         'net_qty': group['net_qty'],
        #         'price': price_range,
        #         'total_amount': group['total_amount'],
        #     }
        #
        #     if min_price == 0.0 or max_price == 0.0:
        #         free_rides.append(ride_summary)
        #     else:
        #         paid_rides.append(ride_summary)
        #
        # paid_rides = sorted(paid_rides, key=lambda x: x['category'])
        # free_rides = sorted(free_rides, key=lambda x: x['category'])

        grouped_data = defaultdict(lambda: {
            'ride_name': '',
            'category': '',
            'qty_paid': 0,
            'refund_paid': 0,
            'net_qty_paid': 0,
            'qty_free': 0,
            'refund_free': 0,
            'net_qty_free': 0,
            'price_list_paid': [],
            'price_list_free': [],
            'total_amount_paid': 0.0,
            'total_amount_free': 0.0,
        })

        for sale in sales_data:
            for line in sale.lines:
                if category_id and line.product_id.categ_id.id != category_id:
                    continue

                key = line.product_id.id
                group = grouped_data[key]

                group['ride_name'] = line.product_id.name
                group['category'] = line.product_id.categ_id.name or 'Uncategorized'

                refund_qty = abs(line.qty) if line.qty < 0 else 0
                net_qty = line.qty if line.qty > 0 else 0

                if line.price_unit == 0:
                    group['qty_free'] += line.qty + refund_qty
                    group['refund_free'] += refund_qty
                    group['net_qty_free'] += net_qty
                    group['price_list_free'].append(line.price_unit)
                    group['total_amount_free'] += float(line.qty) * float(line.price_unit)
                else:
                    group['qty_paid'] += line.qty + refund_qty
                    group['refund_paid'] += refund_qty
                    group['net_qty_paid'] += net_qty
                    group['price_list_paid'].append(line.price_unit)
                    group['total_amount_paid'] += float(line.qty) * float(line.price_unit)

        paid_rides = []
        free_rides = []

        for group in grouped_data.values():
            if group['price_list_paid']:
                min_price = min(group['price_list_paid'])
                max_price = max(group['price_list_paid'])
                price_range = f"{min_price:.2f}" if min_price == max_price else f"{min_price:.2f} - {max_price:.2f}"

                paid_rides.append({
                    'ride_name': group['ride_name'],
                    'category': group['category'],
                    'qty': group['qty_paid'],
                    'refund': group['refund_paid'],
                    'net_qty': group['net_qty_paid'],
                    'price': price_range,
                    'total_amount': group['total_amount_paid'],
                })

            if group['price_list_free']:
                min_price = min(group['price_list_free'])
                max_price = max(group['price_list_free'])
                price_range = f"{min_price:.2f}" if min_price == max_price else f"{min_price:.2f} - {max_price:.2f}"

                free_rides.append({
                    'ride_name': group['ride_name'],
                    'category': group['category'],
                    'qty': group['qty_free'],
                    'refund': group['refund_free'],
                    'net_qty': group['net_qty_free'],
                    'price': price_range,
                    'total_amount': group['total_amount_free'],
                })

        paid_rides = sorted(paid_rides, key=lambda x: x['category'])
        free_rides = sorted(free_rides, key=lambda x: x['category'])

        now = datetime.now()
        report_date = now.date()


        final_report_data = {
            'company_logo': f"data:image/png;base64,{self.env.company.logo.decode('utf-8')}" if self.env.company.logo else None,
            # 'report_data': report_data,
            'paid_rides_report_data': paid_rides,
            'free_rides_report_data': free_rides,
            'print_date': report_date.strftime('%d %b %Y'),
            'print_time': now.strftime('%I:%M:%S %p'),
            'date_from': date_from.strftime('%d %b %Y'),
            'date_to': date_to.strftime('%d %b %Y'),
            'category_name': self.category_id.name if self.category_id else None,
        }

        return self.env.ref('sozo_ride_sales_summary_report.action_report_ride_sales_summary').report_action(self, data=final_report_data)
