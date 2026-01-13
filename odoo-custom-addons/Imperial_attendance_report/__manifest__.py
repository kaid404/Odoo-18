{
    'name': 'Imperial Daily Attendance Report',
    'version': '18.0',
    'category': 'Extra Tools',
    'summary': 'Module for Managing Attendance Reports for Imperial ',
    'license': 'AGPL-3',
    'author': 'Hammad Asghar/Khalid',
    'Maintainer': 'Odoo',
    'depends': [
        'base',
        'hr',
        'hr_attendance',
    ],
    'demo': [],
    'data': [

        'security/ir.model.access.csv',
        'data/paper_format.xml',
        'views/daily_report_template.xml',
        'views/view.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}