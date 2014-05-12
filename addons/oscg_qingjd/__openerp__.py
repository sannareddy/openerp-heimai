# -*- encoding: utf-8 -*-

{
    'name': 'OSCG 请假单',
    'version': '1.0',
    "category" : "Generic Modules/Report",
    'description': """
     """,
    'author': '杨锋',
    'depends': ['base','account'],
    'init_xml': [ ],
    'update_xml': [
        'qingjd_view.xml',
        'qingjd_workflow.xml',
        'report/qingjd_report.xml',
        ],
    'demo_xml': [],
    'installable': True,
    'active': False
}
