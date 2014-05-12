# -*- encoding: utf-8 -*-

{
    'name': 'HM Report Module',
    'version': '1.0',
    "category" : "Generic Modules/Sales & Purchases",
    'description': """ 
      黑迈 报表
    """,
    'author': 'OSCG',
    'depends': ['customize_purchase','report_aeroo','report_aeroo_ooo',],
    'init_xml': [],
    'update_xml': [
        'hm_report.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
