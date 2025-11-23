# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Custom',
    'version': '0.1',
    'author': 'My Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'application': False,
    'installable': True,
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment.xml',
        'views/account_payment_server_action.xml',
    ],
}
