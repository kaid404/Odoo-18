# -*- coding: utf-8 -*-

{
    'name': "Employee Professional Details",

    'summary': "Employee Professional Details",

    'description': """Employee Professional Details""",

    'author': "Khalid",
    'version': '18.0',
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/professional_info_views.xml',
    ]
}
