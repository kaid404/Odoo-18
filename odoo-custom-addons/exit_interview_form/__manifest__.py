# -*- coding: utf-8 -*-
{
    'name': "Exit Interview Form",

    'summary': """Creating a Menu and form in Hr Employee of Exit Interview""",

    'description': """Creating a Menu and form in Hr Employee of Exit Interview""",

    'author': "GXS",
    'version': '18.0',

    'depends': ['base','hr'],

    'data': [
        'security/ir.model.access.csv',
        'views/exit_interview_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

