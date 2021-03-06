# coding=utf-8
from datetime import datetime
from openerp import tools
from openerp.osv import fields
from openerp.osv.orm import Model


class ReportStructure(Model):
    _name = 'day.report.structure'
    _description = u'Ежедневные отчеты - Структура'
    _auto = False
    _order = 'paid_date'

    @staticmethod
    def calc(field, total):
        try:
            return field * 100 / total
        except ZeroDivisionError:
            return 0

    def _fact(self, cr, uid, ids, name, arg, context=None):
        res = {}
        field = "{name}_s".format(name=name,)
        for record in self.read(cr, uid, ids, ['paid_date'], context):
            start_date = datetime.strptime(record['paid_date'], "%Y-%m-%d")
            f_ids = self.search(cr, uid, [('paid_date', '<=', record['paid_date']), ('paid_date', '>=', start_date.strftime('%Y-%m-01'))])
            res[record['id']] = sum(r[field] for r in self.read(cr, uid, f_ids, [field], context))
        return res

    def _part(self, cr, uid, ids, name, arg, context=None):
        """
            Динамически определяет роли на форме
        """
        res = {}
        field = name[:-5]
        total = 'total_plan'
        if 'fact' in name:
            total = 'total_fact'
        for record in self.read(cr, uid, ids, [field, total], context):
            res[record['id']] = self.calc(record[field], record[total])
        return res

    def _per(self, cr, uid, ids, name, arg, context=None):
        """
            Динамически определяет роли на форме
        """
        res = {}
        fact = name.replace('per', 'fact')
        plan = name.replace('per', 'plan')
        for record in self.read(cr, uid, ids, [fact, plan], context):
            res[record['id']] = self.calc(record[fact], record[plan])
        return res

    _columns = {
        'date_start': fields.date('c', select=True),
        'date_end': fields.date('по', select=True),

        'paid_date': fields.date('Дата'),

        'ppc_plan': fields.float('PPC план'),
        'ppc_plan_part': fields.function(
            _part,
            type='float',
            string='PPC план доля'
        ),
        'ppc_fact_s': fields.float('PPC факт'),
        'ppc_fact': fields.function(
            _fact,
            type='float',
            string='PPC факт'
        ),
        'ppc_fact_part': fields.function(
            _part,
            type='float',
            string='PPC факт доля'
        ),
        'ppc_per': fields.function(
            _per,
            type='float',
            string='PPC процент выполнения'
        ),
        
        'smm_plan': fields.float('smm план'),
        'smm_plan_part': fields.function(
            _part,
            type='float',
            string='smm план доля'
        ),
        'smm_fact_s': fields.float('smm факт'),
        'smm_fact': fields.function(
            _fact,
            type='float',
            string='smm факт'
        ),
        'smm_fact_part': fields.function(
            _part,
            type='float',
            string='smm факт доля'
        ),
        'smm_per': fields.function(
            _per,
            type='float',
            string='smm процент выполнения'
        ),
        
        'seo_plan': fields.float('seo план'),
        'seo_plan_part': fields.function(
            _part,
            type='float',
            string='seo план доля'
        ),
        'seo_fact_s': fields.float('seo факт'),
        'seo_fact': fields.function(
            _fact,
            type='float',
            string='seo факт'
        ),
        'seo_fact_part': fields.function(
            _part,
            type='float',
            string='seo факт доля'
        ),
        'seo_per': fields.function(
            _per,
            type='float',
            string='seo процент выполнения'
        ),
        
        'call_plan': fields.float('call план'),
        'call_plan_part': fields.function(
            _part,
            type='float',
            string='call план доля'
        ),
        'call_fact_s': fields.float('call факт'),
        'call_fact': fields.function(
            _fact,
            type='float',
            string='call факт'
        ),
        'call_fact_part': fields.function(
            _part,
            type='float',
            string='call факт доля'
        ),
        'call_per': fields.function(
            _per,
            type='float',
            string='call процент выполнения'
        ),
        
        'web_plan': fields.float('web план'),
        'web_plan_part': fields.function(
            _part,
            type='float',
            string='web план доля'
        ),
        'web_fact_s': fields.float('web факт'),
        'web_fact': fields.function(
            _fact,
            type='float',
            string='web факт'
        ),
        'web_fact_part': fields.function(
            _part,
            type='float',
            string='web факт доля'
        ),
        'web_per': fields.function(
            _per,
            type='float',
            string='web процент выполнения'
        ),
        
        'video_plan': fields.float('video план'),
        'video_plan_part': fields.function(
            _part,
            type='float',
            string='video план доля'
        ),
        'video_fact_s': fields.float('video факт'),
        'video_fact': fields.function(
            _fact,
            type='float',
            string='video факт'
        ),
        'video_fact_part': fields.function(
            _part,
            type='float',
            string='video факт доля'
        ),
        'video_per': fields.function(
            _per,
            type='float',
            string='video процент выполнения'
        ),
        
        'mp_plan': fields.float('mp план'),
        'mp_plan_part': fields.function(
            _part,
            type='float',
            string='mp план доля'
        ),
        'mp_fact_s': fields.float('mp факт'),
        'mp_fact': fields.function(
            _fact,
            type='float',
            string='mp факт'
        ),
        'mp_fact_part': fields.function(
            _part,
            type='float',
            string='mp факт доля'
        ),
        'mp_per': fields.function(
            _per,
            type='float',
            string='mp процент выполнения'
        ),
        
        'total_plan': fields.float('total план'),
        'total_fact_s': fields.float('total факт'),
        'total_fact': fields.function(
            _fact,
            type='float',
            string='total факт'
        ),
        'total_per': fields.function(
            _per,
            type='float',
            string='total процент выполнения'
        ),
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'day_report_structure')
        cr.execute("""
            create or replace view day_report_structure as (
                SELECT
                  row_number() over() as id,
                  to_char(ip.date_pay, 'YYYY-MM-DD') date_end,
                  to_char(ip.date_pay, 'YYYY-MM-DD') date_start,
                  ip.date_pay paid_date,
                  max(ppc_plan) ppc_plan,
                  sum(case when bss.direction='PPC' then ipl.factor else 0 end) ppc_fact_s,
                  max(smm_plan) smm_plan,
                  sum(case when bss.direction='SMM' then ipl.factor else 0 end) smm_fact_s,
                  max(seo_plan) seo_plan,
                  sum(case when bss.direction='SEO' then ipl.factor else 0 end) seo_fact_s,
                  max(call_plan) call_plan,
                  sum(case when bss.direction='CALL' then ipl.factor else 0 end) call_fact_s,
                  max(web_plan) web_plan,
                  sum(case when bss.direction='SITE' then ipl.factor else 0 end) web_fact_s,
                  max(video_plan) video_plan,
                  sum(case when bss.direction='VIDEO' then ipl.factor else 0 end) video_fact_s,
                  max(mp_plan) mp_plan,
                  sum(case when bss.direction='MP' then ipl.factor else 0 end) mp_fact_s,
                  max(total_plan) total_plan,
                  sum(case when bss.direction in ('PPC', 'SMM', 'SEO', 'CALL', 'SITE', 'VIDEO', 'MP') then ipl.factor else 0 end) total_fact_s

                FROM
                  account_invoice_pay ip
                  LEFT JOIN account_invoice_pay_line ipl on (ipl.invoice_pay_id=ip.id)
                  LEFT JOIN brief_services_stage bss on (bss.id=ipl.service_id)
                  LEFT JOIN (
                    SELECT
                      p.name,
                      max(case when s.name=464 then s.plan else 0 end) ppc_plan,
                      max(case when s.name=465 then s.plan else 0 end) smm_plan,
                      max(case when s.name=466 then s.plan else 0 end) seo_plan,
                      max(case when s.name=467 then s.plan else 0 end) call_plan,
                      max(case when s.name=468 then s.plan else 0 end) web_plan,
                      max(case when s.name=469 then s.plan else 0 end) video_plan,
                      max(case when s.name=475 then s.plan else 0 end) mp_plan,
                      sum(s.plan) total_plan
                    FROM kpi_period p
                      LEFT JOIN kpi_kpi k on (k.period_id=p.id AND k.employee_id=10)
                      LEFT JOIN kpi_sla_sale s on (s.kpi_id=k.id)
                    WHERE p.calendar='rus'
                    GROUP BY s.kpi_id, p.name
                  ) y on (y.name=to_char(ip.date_pay, 'YYYY/MM'))
                  LEFT JOIN account_invoice i on (i.id=ip.invoice_id)
                  WHERE i.user_id <> 170
                  GROUP BY date_pay
            )""")

    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        for item in args:
            if item[0] == 'date_start':
                item[0] = 'paid_date'
                item[1] = '>='
            if item[0] == 'date_end':
                item[0] = 'paid_date'
                item[1] = '<='
                item[2] = "{date} 23:59:59".format(date=item[2],)
        return super(ReportStructure, self).search(cr, user, args, offset, limit, order, context, count)
ReportStructure()