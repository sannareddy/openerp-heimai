# -*- encoding: utf-8 -*-
from osv import osv, fields
from lxml import etree
import openerp
from openerp import SUPERUSER_ID
import logging
from openerp.tools import ustr
from openerp import tools
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import netsvc
from tools.translate import _
_logger = logging.getLogger(__name__)

class purchase_order(osv.osv):
    #_inherit = ['purchase.order','workflow.base']
    _inherit = 'purchase.order'
    _columns = {
        'invoice_requirement':fields.selection([
            ('added_value',u'增值税票'),
            
            ('common',u'普通税票'),
            ('others',u'其它')
            ],u'发票要求'),
        'transport_type':fields.selection([
            ('supply',u'供方送货'),
            
            ('self_sufficiency',u'需方自提'),
            ('express',u'快递'),
            ('ship',u'托运'),
            ('others',u'其它')
            ],u'运输方式'),
            
        'applied_range':fields.selection([
            ('production',u'生产'),
            
            ('storage',u'库存'),
            ('enquiry',u'询价'),
            ('reverse',u'备用'),
            ],u'应用范围'),
        
        'production_code': fields.char(u'生产令',size=32,help=u"图纸编号"),
        'street': fields.char(u'送货地址',size=128,help=u"送货地址"),
    }
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = {'street':'',}
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res = {'street': company.street or '',}
        return {'value': res}
    
    
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line'
    _columns = {
        'description': fields.char(u'说明',size=128,help=u"说明"),
        'graph_code':fields.char(u'图纸编号',size=128,help=u"图纸编号"),
        }
purchase_order_line()
