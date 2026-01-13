# -*- coding: utf-8 -*-
{
    'name': "SOZO WATER PARK Ride Sales Summary Report",

    'summary': """SOZO WATER PARK Ride Sales Summary Report""",

    'description': """SOZO WATER PARK Ride Sales Summary Report""",

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

