{
    'name': 'Mass Leave Allocator',
    'version': '1.0',
    'summary': 'Allocate leave to multiple employees at once',
    'description': 'Custom Odoo module to allocate same leave type to multiple employees with preview and logging',
    'author': 'Lamia Custom',
    'depends': ['base', 'hr', 'hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
         'views/menu_action.xml', 
        'views/mass_leave_allocation_views.xml'
    ],
    'installable': True,
    'application': True,
}
