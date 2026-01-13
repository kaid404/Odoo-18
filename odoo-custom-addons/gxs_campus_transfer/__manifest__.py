{
    'name': 'Student Campus Transfer',
    'version': '18.0',
    'category': 'Studio',
    'module_type': 'official',
    'summary': """ 
            Custom Odoo module to send an email of lows tock to related parson.
    """,
    'author': 'HASNAIN JUTT(GXS)',
    'license': 'AGPL-3',
    'website': 'https://www.globalxs.co',
    'depends': ['base','mail', 'gxs_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/section_views.xml',
        'views/class_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
