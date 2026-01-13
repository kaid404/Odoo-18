# -*- coding: utf-8 -*-
{
    'name': "Salary Sheet Report",
    'summary': """Salary Sheet Report""",
    'description': """Salary Sheet Report""",
    'author': "HASNAIN JUTT(GXS)",
    'website': "http://www.globalxs.co",
    'category': 'Studio',
    'version': '18.0',
    'depends': [
        'hr', 'hr_payroll', 'hr_contract',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'wizard/salary_sheet.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
