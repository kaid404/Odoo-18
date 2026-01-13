{
    'name': 'Senior Students Result Reports',
    'version': "18.0",
    'category': 'Studio',
    'summary': 'Module for Senior Students Result Reports',
    'sequence': '-10001',
    'license': 'AGPL-3',
    'author': '(GXS)',
    'Maintainer': 'Global Xs Tehnology Solutions',
    'website': 'http://globalxs.co',
    'depends': [
        'base', 'gxs_core', 'gxs_student_performance','gxs_exam_assessment','odoocms_student_exam_performance'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/wizard_views.xml',
        'views/templates.xml',
    ],

    'installable': True,
    'application': True,
    'auto install': False,
}
