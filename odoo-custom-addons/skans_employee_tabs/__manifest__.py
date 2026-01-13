# -*- coding: utf-8 -*-
{
    'name': "Employee Additional Tabs",

    'summary': "Module for adding Tabs in Employee Form",

    'description': """Module for adding Tabs in Employee Form""",

    'author': "Khalid",
    'version': '18.0',
    'depends': ['base', 'hr', 'skans_empl_incriment', 'skan_employee_bonus'],

    # always loaded
    'data': [
        'data/rec_sequence.xml',
        'security/ir.model.access.csv',
        'views/academic_info.xml',
        'views/additional_duties.xml',
        'views/disciplinary_views.xml',
        'views/employee_records.xml',
        'views/personal_info_views.xml',
        'views/project_lists_info_views.xml',
        'views/training_courses_info_views.xml',
        'views/training_courses_taught_views.xml',
        'views/professional_info_views.xml',
        'views/project_info_views.xml',
        'views/prof_reg_info_view.xml',
        'views/family_info.xml',
        'views/employee_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'skans_employee_tabs/static/src/css/custom_style.css',
        ],
    },

}
