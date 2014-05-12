# -*- encoding: utf-8 -*-
import time
import datetime
import pooler
import logging
import netsvc
import tools
from dateutil.relativedelta import relativedelta
logger = netsvc.Logger()
from datetime import timedelta, date
from osv import fields,osv
import logging
_logger = logging.getLogger(__name__)


class oscg_qingjd(osv.osv):
    _name = 'oscg_qingjd'
    _description = u'请假单'
    def _get_wage(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            start = datetime.datetime.strptime(emp.kaisrq, '%Y-%m-%d')
            stop = datetime.datetime.strptime(emp.jiesrq, '%Y-%m-%d')
            res[emp.id] = (stop - start).days
            _logger.debug("SUN  jiesrq = %s  kaisrq= %s" % (emp.jiesrq,emp.kaisrq))
        return res

    _columns = {
            'shenqr':fields.many2one('res.users',u'申请人',required=True),
            #'tians':fields.float(u'天数',size=64,required=True),
            'tians': fields.function(_get_wage, string = u'天数', type= 'float', help="Basic Salary of the employee"),
            'kaisrq':fields.date(u'开始日期',required=True),
            'jiesrq':fields.date(u'结束日期',required=True),
            'period_id': fields.many2one('account.period', u'月份',required=True,),
            'shiyou':fields.text(u'事由'),
            'state':fields.selection([('draft',u'草稿'),('wait_prove',u'待批'),('proved',u'已批'),('rejected',u'被拒')],u'状态',readonly=True)
          }
          
    _defaults = { 'state': 'draft',}
    
oscg_qingjd()