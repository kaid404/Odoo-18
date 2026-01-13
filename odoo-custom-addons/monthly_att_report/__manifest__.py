
{
    'name': 'Monthly Attendance Report',
    'version': '18.0',
    'category': 'Reports',
    'summary': 'Module for generating attendance report for the College Classes',
    'author': 'Khalid',
    'depends': ['base', 'odoocms','odoocms_registration'],
    'data': [
        'security/ir.model.access.csv',
        'views/monthly_att_wizard_view.xml',
        'views/monthly_att_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
