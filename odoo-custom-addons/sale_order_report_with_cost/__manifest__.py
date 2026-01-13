{
    'name': 'Sale Order Reports',
    'version': "18.0.1.0.0",
    'category': 'Studio',
    'summary': 'Module for manging Sale Order Reports',
    'sequence': '-10001',
    'license': 'AGPL-3',
    'author': 'HASNAIN JUTT(GXS)',
    'Maintainer': 'Global Xs Tehnology Solutions',
    'website': 'http://globalxs.co',
    'depends': [
        'base', 'stock', 'sale',
    ],
    'demo': [],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'views/nomi_report_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
