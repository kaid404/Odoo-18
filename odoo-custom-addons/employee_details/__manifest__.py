# -*- coding: utf-8 -*-
{
    'name': 'Employee Details',

    'version': '18.0',

    'summary': 'Add employee details ',

    'description': 'Add Employee details.',

    'author': 'Hamza',
    'category': 'Human Resources',

    'depends': ['base', 'hr'],

    'data': [
        # Add XML view files here if any (optional)
        'security/ir.model.access.csv',
        # 'views/professional_info_views.xml',
        'views/academic_info.xml',
        'views/family_info.xml',
        # 'views/hr_employee_views.xml',
        # 'views/hr_next_of_kin_views.xml',
        'views/collaboration_info_view.xml',
        'views/prof_reg_info_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
