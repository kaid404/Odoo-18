# -*- coding: utf-8 -*-
{
    'name': "Skans Survey Report",

    'summary': """Skans Survey Report""",

    'description': """Skans Survey Report""",

    'author': "Khalid",
    'version': '18.0',

    'depends': ['base','survey','survey_custom_report'],

    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

