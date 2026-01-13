{
    'name': 'Jr Result Report',
    'version': '18.0',
    'category': 'Productivity',
    'Summary': 'Additional Fields Buttons Status added',
    'depends': ['base', 'gxs_core', 'gxs_student_performance', 'gxs_milestone_results'],
    'description': """jr Result Report""",

    'data': [
        'security/ir.model.access.csv',
        'views/result_report_view.xml',
        'views/templates.xml',

    ],

    'installable': True,
    'auto install': False,
}
