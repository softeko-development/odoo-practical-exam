{
    'name': 'Mass Confirm Quotations',
    'version': '1.0.0',
    'category': 'Sales',
    'summary': 'Bulk confirm multiple sales quotations at once',
    'description': """
        This module allows sales managers to confirm multiple draft quotations 
        simultaneously through a wizard interface with filtering options.
    """,
    'author': 'Your Name',
    'depends': ['sale', 'stock'],
    'data': [
        'wizard/wizard_views.xml',
        'views/menu_views.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}