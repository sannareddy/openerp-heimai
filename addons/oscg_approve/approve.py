# -*- encoding: utf-8 -*-

import time
from osv import osv, fields
import openerp
from openerp import SUPERUSER_ID
import logging
from openerp.tools import ustr

_logger = logging.getLogger(__name__)

class approve_flow(osv.osv):
    _name = "approve.flow"
    _description = u"表单审批流程配置"
    _columns = {
        'name': fields.char(u'审批流程', size=64, required=True),
        'res_model':fields.many2one('ir.model', u'表单对象', required=True),
        'step_ids': fields.one2many('approve.step', 'flow_id', u'审批步骤'),
    }

class approve_step(osv.osv):
    _name = "approve.step"

    _columns = {
        'sequence':fields.integer(u'序号', required=True),
        'role_id':fields.many2one('res.groups', u'审批角色', required=True),
        'user_id':fields.many2one('res.users', u'默认审批人'),
        'stage': fields.char(u'内部状态', size=16, required=True),
        'stage_name': fields.char(u'显示状态', size=16, required=True),
        'domain':fields.char(u'条件', size=256),
        'countersign':fields.boolean(u'会签'),
        'notify':fields.boolean(u'邮件'),
        'flow_id': fields.many2one('approve.flow', '审批流程', required=True, ondelete='cascade', select=True),
    }
    _order = 'sequence asc'

    _defaults = {
        'sequence':1,
    }

class approve_log(osv.osv):
    _name = "approve.log"
    _columns = {
        'step_id':fields.many2one('approve.step', u'审批步骤'),
        'sequence': fields.related('step_id', 'sequence', type='integer', string=u'序号', store=True, readonly=True),
        'role_id': fields.related('step_id', 'role_id', type='many2one', relation='res.groups', string=u'审批角色', store=True, readonly=True),
        'user_id':fields.many2one('res.users', u'审批人', required=True),
        'approve_desc':fields.char(u'审批意见', size=16, readonly=True),
        'approve_date':fields.datetime(u'审批时间' , readonly=True),
        'countersign':fields.boolean(u'会签'),
        'notify':fields.boolean(u'邮件通知'),
        'id':fields.integer('ID'),
        'res_id':fields.integer('Res ID'),
        'res_model':fields.many2one('ir.model', u'表单对象', required=True),
    }
    _order = 'res_model, res_id, sequence'
    def _default_role(self, cr, uid, context=None):
        sql1 = "select min(id) from res_users"
        cr.execute(sql1)
        min_role_id = cr.fetchone()
        return min_role_id and min_role_id[0] or False
    _defaults = {
        'sequence':1,
        'approve_date':False,
        'role_id':_default_role,
    }

class approve_base(osv.AbstractModel):
    _name = "approve.base"
    
    def _read_approve_log(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for id in ids:
            model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
            sql = "select id,sequence,res_id,res_model,role_id,user_id,approve_date,approve_desc,countersign,notify from approve_log where res_id=%s and res_model=%s order by sequence asc;"%(id,model_id[0])
            cr.execute(sql)
            res[id] = cr.dictfetchall()
            for x in res[id]:
                if x['approve_date'] == None: x['approve_date'] = False
                if x['user_id'] == None: x['user_id'] = False
        return res

    def _write_approve_log(self, cr, uid, ids, name, value, arg, context=None):
        if not value:
            return False
        if isinstance(ids, (int, long)):
            ids = [ids]
        model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        log_obj = self.pool.get('approve.log')
        for v in value:
            if not v[2]: continue
            log = v[2]
            log.update({'res_model':model_id[0],'res_id':ids[0]})
            log_id = log.get('id',False)
            if log.has_key('id'): log.pop('id')
            if log_id:
                log_obj.write(cr, uid, log_id, log, context=context)
            else:
                log_obj.create(cr, uid, log, context=context)
        return True

    _columns = {
        'approve_stage': fields.selection([('draft', u'未提交'), ('approving', u'审批中'), ('approved', u'审批通过'), ('cancel', u'已取消')], u'审批状态', readonly=True), 
        #approve_users格式形如： ,1,2,3,  以逗号隔开的user_id列表，开头和结尾也含有逗号。 
        'approve_users': fields.char(u'当前审批人', size=32, invisible=True),
        'approve_logs': fields.function(_read_approve_log, fnct_inv=_write_approve_log, type='one2many', relation='approve.log', string=u'审批流',ondelete="cascade"),
    }

    def _default_approve_logs(self, cr, uid, context=None):
        if context is None:
            context = {}
        model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        approve_obj = self.pool.get('approve.flow')
        approve_id = approve_obj.search(cr,uid,[('res_model','=',model_id[0])])
        res = []
        if approve_id:
            for flow in approve_obj.browse(cr,uid,approve_id[0]).step_ids:
                res.append({'step_id':flow.id,'sequence':flow.sequence,'user_id':flow.user_id.id,
                                     'role_id':flow.role_id and flow.role_id.id or False,
                                     'countersign':flow.countersign, 'notify':flow.notify})
        return res

    _defaults = {
        'approve_stage': 'draft',
        'approve_logs':_default_approve_logs,
    }

    def next_approve_logs(self, cr, uid, id, context=None):
        '''返回下一条待审的approve.log
        '''
        log_obj = self.pool.get('approve.log')
        model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        res = []
        log_ids = log_obj.search(cr,uid,[('res_model', '=', model_id[0]), ('res_id', '=', id), ('approve_date', '=', False)], context=context)
        if log_ids:
            countersign = False
            for log in log_obj.browse(cr, uid, log_ids, context=context):
                if not log.countersign: #如果下一条不是会签，直接取该条作为结果
                    if not countersign: 
                        res.append(log)
                    break
                if log.countersign: #如果下一条是会签，需要将连续的会签取出来作为下一个审批项
                    countersign = True
                    res.append(log)
        return res
        
    def approve_submit(self, cr, uid, ids, context=None):
        if context is None:context={}
        user_obj = self.pool.get('res.users')
        log_obj = self.pool.get('approve.log')
        model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        user = user_obj.browse(cr, uid, uid, context=context)
        for form in self.browse(cr, uid, ids, context=context):
            localdict = context and context.copy() or {}
            localdict.update({'o': form, 'user': user})
            localdict.update({'time': time})
            log_ids = log_obj.search(cr, uid, [('res_model', '=', model_id[0]), ('res_id', '=', form.id), ('approve_date', '=', False)], context=context)
            for log in log_obj.browse(cr, uid, log_ids, context=context):
                try:
                    condition = log.step_id.domain
                    if condition:
                        res = eval(condition, localdict)
                        if not res:
                            log_obj.unlink(cr, uid, [log.id])
                except Exception, e:
                    _logger.warning(u'审批步骤[Form: %s,%s  Sequence: %s  Condition: %s]条件计算异常[%s]' % (self._name, form.id, log.sequence, log.step_id.domain, e,))
                    continue
                
            next_logs = self.next_approve_logs(cr, uid, form.id, context=context)
            next_user_ids = ','.join(['%s' % x.user_id.id for x in next_logs])
            if next_user_ids: 
                next_user_ids = ',%s,' % next_user_ids
            else:
                next_user_ids = False
            self.write(cr,uid,ids,{'approve_stage':'approving', 'approve_users': next_user_ids}, context=context)
            body = u"%s 提交了表单 <em>%s</em> 。" % ( user.name, form.name)
            self.message_post(cr, uid, [form.id], body=body, context=context)
        return True
        
    def approve_cancel(self, cr, uid, ids, context=None):
        if context is None:context={}
        user_obj = self.pool.get('res.users')
        self.write(cr,uid,ids,{'approve_stage':'cancel', 'approve_users':False},context=context)
        
        user = user_obj.browse(cr, uid, uid)
        for form in self.browse(cr, uid, ids, context=context):
            body = u"%s 取消了表单 <em>%s</em> 。" % ( user.name, form.name)
            self.message_post(cr, uid, [form.id], body=body, context=context)
        return True

    def approve_done(self, cr, uid, id, context=None):
        pass
    
    def approve_agree(self, cr, uid, ids, context=None):
        if context is None:context={}
        t = time.strftime('%Y-%m-%d %H:%M:%S')
        user_obj = self.pool.get('res.users')
        log_obj = self.pool.get('approve.log')
        model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        user = user_obj.browse(cr, uid, uid)
        for id in ids:
            next_logs = self.next_approve_logs(cr, uid, id, context=context)
            approved = False
            for log in next_logs:
                if log.user_id.id == uid:
                    log_obj.write(cr, uid, log.id, {'approve_desc':u'同意', 'approve_date': t}, context=context)
                    approved = True
            if not approved:
                raise osv.except_osv(u'错误', u'您不是当前审批人，不可以审批!')
            
            next_logs = self.next_approve_logs(cr, uid, id, context=context)
            next_user_ids = ','.join(['%s' % x.user_id.id for x in next_logs])
            if next_user_ids: 
                next_user_ids = ',%s,' % next_user_ids
            else:
                next_user_ids = False
            
            self.write(cr, uid, id, {'approve_stage':'approving', 'approve_users': next_user_ids}, context=context)
            form = self.browse(cr, uid, id, context=context)
            body = u"%s 审批了表单 <em>%s</em> 。" % ( user.name, form.name)
            self.message_post(cr, uid, [form.id], body=body, context=context)
            if not next_user_ids: #最后一个审批者
                self.approve_done(cr, uid, id, context)
        return True

    def approve_refuse(self, cr, uid, ids, context=None):
        if context is None:context={}
        user_obj = self.pool.get('res.users')
        model_id = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        
        user = user_obj.browse(cr, uid, uid)
        for form in self.browse(cr, uid, ids, context=context):
            cr.execute("update approve_log set approve_desc='', approve_date=NULL where res_id=%s and res_model=%s"%(form.id, model_id[0]))
            self.write(cr, uid, form.id, {'approve_stage':'draft', 'approve_users': False}, context=context)
            body = u"%s 拒绝了表单 <em>%s</em> 。" % ( user.name, form.name)
            self.message_post(cr, uid, [form.id], body=body, context=context)
        return True
        