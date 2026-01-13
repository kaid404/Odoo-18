{
    'name': 'Grade Summary Report',
    'version': '18.0',
    'depends': ["gxs_exam"],
    'description': """Grade Summary Report""",

    'data': [
        'security/ir.model.access.csv',
        'views/grade_summary_report.xml',
        'views/templates.xml',

    ],

    'installable': True,
    'auto install': False,
}
