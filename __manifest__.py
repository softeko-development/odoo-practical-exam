
{
    'name': 'Stock Reorder Alert Wizard',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Show popup when stock goes below minimum reordering rule',
    'author': 'ChatGPT',
    'depends': ['stock', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_alert_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
