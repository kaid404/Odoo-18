{
    # App information
    'name': 'Fincera Quotation Sales Report New',
    'category': 'studio',
    'summary': 'Fincera Quotation Sales Report New',
    'description': 'Fincera Quotation Sales Report New',
    'version': "18.0.1.0.0",
    'author': 'Abdul Rehman Ghani(GXS)',
    'license': 'LGPL-3',
    'company': 'GlobalXs & Solution',
    'website': 'https://www.globalxs.com',

    # Dependencies
    'depends': ['sale', 'web', 'account'],

    # Data
    'data': [
        'views/views.xml',
        'reports/report_action.xml',
        'reports/sale_order_quotation_report.xml',
        'reports/account_payment_receipet_report.xml',
    
    ],

    # Images
    'images': [
    ],

    # Technical
    'installable': True,
    'auto_install': False,
    'application': False,
}
