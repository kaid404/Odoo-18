# -*- coding: utf-8 -*-
{
    'name': "Reports With Images",

    'summary': "Added the image column in default odoo reports",

    'description': """Added the image column in default odoo reports""",

    'author': "Khalid(Gxs)",

    'category': 'Reporting',
    'version': '18.0',

    'depends': ['base', 'sale', 'purchase'],

    'data': [
        'views/sale_order_template.xml',
        'views/purchase_order_template.xml',
        'views/bills_template.xml',
    ],
}



