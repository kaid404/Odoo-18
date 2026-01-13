# -*- coding: utf-8 -*-
{
    'name': "Skans Exams Report",

    'summary': """Skans Exams Report""",

    'description': """Skans Exams Report""",

    'author': "Khalid",
    'version': '18.0',

    'depends': ['base','gxs_exam','gxs_attendance'],

    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

