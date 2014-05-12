# -*- encoding: utf-8 -*-

{
    'name': '表单审批流程配置',
    'version': '1.0',
    "category" : "Hidden",
    'description': """ 
    业务背景
           对大公司，ERP系统中很多表单都需要多部门审批，如新增供应商，新增产品资料，SO单的审批等。目前OpenERP中缺乏简单易用的审批流功能。
           简单易用的审批流功能要求：a) 容易为各种表单添加审批流程；b) 审批权限配置和修改简单明了。
    模块功能说明
    
    
    模块使用方法说明
    
    """,
    'author': 'OSCG',
    'website': 'http://www.oscg.cn',
    'depends': ['base','mail'],
    'init_xml': [],
    'update_xml': ['security/approve_security.xml', 'approve_view.xml'  ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
