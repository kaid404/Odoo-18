{
    'name': "Skans Appraisal Template Froms",
    'author': 'GXS',
    'license': 'AGPL-3',
    'website': 'http://www.globalxs.co',
    'description': """Skans Appraisal Template Froms""",
    'version': '18.0',
    'depends': ['hr_appraisal'],
    'data': [
        'security/ir.model.access.csv',
        'views/appraisal_temp_views.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
