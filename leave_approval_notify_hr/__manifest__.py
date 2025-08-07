{
    'name': 'Leave Approval Notifier',
    'version': '18.0.0.0',
    'summary': 'Multi-level leave approval with HR notification',
    'description': """
        Allows employees to apply for leave, managers to approve,
        and automatically notifies HR after approval.
    """,
    'author': 'Humayra,Rifat, Lamia',
    'depends': ['base','hr', 'mail'],
    'data': [
        'security/leave_approval_security.xml',
        'security/ir.model.access.csv',
        # 'views/all_request.xml',
        'views/leave_type_views.xml',
        'data/mail_template_data.xml',
        'views/leave_request_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}