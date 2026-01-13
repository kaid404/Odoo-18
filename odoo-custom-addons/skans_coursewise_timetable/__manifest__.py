# -*- coding: utf-8 -*-
{
    'name': "Class Wise TimeTable",

    'summary': """The system should be able to generate a timetable for each course with a "From" and "To" feature allowing users to create the timetable
     either on a yearly or monthly basis.It should also include weekday wise details, where users can define the subject plan for each day of the week.""",

    'description': """The system should be able to generate a timetable for each course with a "From" and "To" feature allowing users to create the timetable
     either on a yearly or monthly basis.It should also include weekday wise details, where users can define the subject plan for each day of the week.""",

    'author': "Khalid",
    'version': '18.0',

    'depends': ['base','gxs_core', 'gxs_timetable'],

    'data': [
        'security/ir.model.access.csv',
        'wizard/wizard_timetable_gen_views.xml',
        'views/timetable_slot_views.xml',
        'views/inherit_slot_views.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,

}

