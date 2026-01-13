# -*- coding: utf-8 -*-
{
    'name': "SOZO Receipts & Payments Report",

    'summary': """SOZO Receipts & Payments Report""",

    'description': """SOZO Receipts & Payments Report""",

    'author': "Khalid",
    'version': '18.0',

    'depends': ['base','point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

