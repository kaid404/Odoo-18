# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR attendance',
    'version': '1.0',
    'category': 'costing',
    'author': 'Mr Hamza',
    'sequence': -150,
    'summary': 'vendor wise costing system',
    'description': """vendor wise costing system""",
    'depends': ['hr_attendance'],
    'data': [
        'views/hr_attendance_view.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
