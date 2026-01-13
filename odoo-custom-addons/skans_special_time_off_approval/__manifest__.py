# -*- coding: utf-8 -*-

{
    'name': "Special Approval Time-Off",

    'summary': "Module for special approval when taking more than 2 leaves",

    'description': """Module for special approval when taking more than 2 leaves""",

    'author': "Khalid",
    'version': '18.0',
    'depends': ['base','hr', 'hr_holidays'],

    # always loaded
    'data': [
        'security/special_approval_group.xml',
        'views/views.xml',
    ]
}
