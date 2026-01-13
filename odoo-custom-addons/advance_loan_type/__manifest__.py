# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Employee Advance Loan Field Type',
    'version': '18.0',
    'summary': 'Employee Advance Loan Field Type',

    'category': 'Studio',
    'author': 'Abdul Rehman Ghani (GXS)',
    'website': 'https://abdul.rehman@globalxs.co',

    'depends': [
        'sync_employee_advance_salary',
        'hr'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/loan_view.xml',

    ],
    'demo': [

    ],

}
