{
    'name': 'Faculty Results Report',
    'version': '18.0',
    'summary': 'Module for generating faculty results summary report',
    'description': 'Module for generating faculty results summary report',
    'author': 'Khalid',
    'depends': ['base','senior_result_report'],
    'data': [
        'security/ir.model.access.csv',
        'views/faculty_results_report_views.xml',
        'views/template.xml',
    ],
    'installable': True,
    'application': False,
}
