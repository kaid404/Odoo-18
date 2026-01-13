# -*- coding: utf-8 -*-
{
    'name': 'Skans Maternity Leave Restriction',

    'version': '18.0',

    'summary': 'Restrict maternity leave based on job duration and max days',

    'description': 'Allows maternity leave allocation only if job duration is less than 1 year and days are under 45.',

    'author': 'Hamza',
    'category': 'Human Resources',

    'depends': ['hr_holidays', 'hr_contract'],

    'data': [
        'views/view.xml'

    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}


