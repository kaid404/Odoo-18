{
    'name': "CMS Student Performance",
    'author': "ABDUL REHMAN GHANI (GXS)",
	'website': "http://www.globalxs.co/abdul.rehman@globalxs.co",
	'Maintainer': 'Global XS Technology Solutions',
	'category': 'Studio',
    'license': 'AGPL-3',
    'description': """CMS Student Performance""",
    'version': '18.0',
    'depends': ['gxs_core', 'odoocms_academic', 'mail', 'gxs_student_performance'],
    'data': [
        'security/ir.model.access.csv',
        'views/op_subject.xml',
        'views/perfromance_template.xml',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
