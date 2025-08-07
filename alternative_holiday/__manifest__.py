# -*- coding: utf-8 -*-
{
    'name': 'Alternative Holiday Request',
    'version': '18.0.0.0',
    'summary': 'Allows employees to request compensatory leave for holidays/weekends worked',
    'author': 'Humayra, Rifat, Lamia',
    'category': 'Human Resources',
    'depends': ['base', 'hr', 'hr_holidays', 'mail'],
    'data': [
        'security/alternative_holiday_security.xml',
        'security/ir.model.access.csv',
        'views/holiday_request_views.xml',
        'views/holiday_request_manager_views.xml',
        'views/email_template.xml',
        'views/holiday_request_menus.xml',
    ],
    'installable': True,
    'application': True,
}
