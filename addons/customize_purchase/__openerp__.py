# -*- encoding: utf-8 -*-

{
    'name': 'HM Purchase Fix Module',
    'version': '1.0',
    "category" : "Generic Modules/Sales & Purchases",
    'description': """ 
      黑麦 采购
    """,
    'author': 'OSCG',
    'depends': ['base','account','stock','purchase','sale','procurement','crm','mrp', 'hr','hr_contract','oscg_approve',],
    'init_xml': [],
    'update_xml': [
        'customize_purchase.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
