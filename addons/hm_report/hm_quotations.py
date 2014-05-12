# -*- encoding: utf-8 -*-
import time
#from mx.DateTime import *
from report import report_sxw
import pooler
import logging
import netsvc
import tools
from tools import amount_to_text_en
import logging
logger = logging.getLogger(__name__)
class Parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'get_user':self.get_user,
            'get_selection_item':self._get_selection_item('item'),
        })
    def get_user(self,obj):
        res=''
        user_ids=obj.partner_id and obj.partner_id.child_ids or []
        for user in user_ids:
            if user.type not in ['contact','delivery']:continue
            if user.type=='delivery':
                return user.name
            if user.type=='contact'and (not res):
                res=user.name
        return res
        
    def get_selection_item(obj, field, value=None):
        try:
            if isinstance(obj, report_sxw.browse_record_list):
                obj = obj[0]
            if isinstance(obj, (str,unicode)):
                model = obj
                field_val = value
            else:
                model = obj._table_name
                field_val = getattr(obj, field)
            if kind=='item':
                if field_val:
                    return dict(self.pool.get(model) \
                    .fields_get(self.cr, self.uid, allfields=[field], context=self.context)\
                    [field]['selection'])[field_val]
            elif kind=='items':
                return self.pool.get(model) \
                .fields_get(self.cr, self.uid, allfields=[field], context=self.context)\
                [field]['selection']
            return ''
        except Exception:
            return ''
