# -*- coding: utf-8 -*-
{
    'name': "PO Approvals",

    'summary': "Adding 2 buttons for RFQ Approvals",

    'description': """Adding 2 buttons for RFQ Approvals""",

    'author': "Khalid",
    'version': '18.0',
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        'security/po_approval_groups.xml',
        'views/po_views.xml'
    ]
}

