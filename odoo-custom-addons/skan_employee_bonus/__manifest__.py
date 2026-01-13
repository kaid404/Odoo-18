{
    'name': 'Opus Employee Bonus',
    'version': '18.0',
    'category': 'Extra Tools',
    'summary': 'Module for manging Employee Bonus',
    'sequence': '-10008',
    'license': 'AGPL-3',
    'author': 'Hammad Asghar' 'Asad',
    'Maintainer': 'Odoo Mates',
    'website': '',
    'depends': [
        'hr',
        'hr_payroll',
    ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/groups.xml',
        'views/hr_employee_bonus_view.xml',

    ],
    'installable': True,
    'application': True,
    'auto install': False,
}
