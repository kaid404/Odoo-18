# -*- coding: utf-8 -*-
{
    'name': "Approval For PO and Vendor Bill",

    'summary': "",

    'description': """""",

    'author': "Hamza",
    'version': '18.0',

    'depends': ['base','account','purchase'],

    'data': [
        # 'security/ir.model.access.csv',
        'security/vendor_groups.xml',
        'security/po_approval_groups.xml',
        'views/view.xml',
        'views/po_views.xml',
        # 'views/templates.xml',
    ],
}

