# -*- coding: utf-8 -*-
{
    'name': "Teacher Unique Code",

    'summary': """The system should have Provision for assigning unique teacher code names,using the first two letters of the first name
     and the first letter of the last name (e.g.,SAR for Sadia Rehman,IMA for lmran Awan).""",

    'description': """The system should have Provision for assigning unique teacher code names,using the first two letters of the first name
     and the first letter of the last name (e.g.,SAR for Sadia Rehman,IMA for lmran Awan).""",

    'author': "Khalid",
    'version': '18.0',

    'depends': ['base','gxs_core'],

    'data': [
        'views/views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

