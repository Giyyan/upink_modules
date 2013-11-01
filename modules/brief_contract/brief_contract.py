# -*- encoding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv
from openerp.osv.orm import Model
from notify import notify


class BriefContract(Model):
    _name = "brief.contract"
    _description = u'Бриф на договор'
    _log_create = True
    _rec_name = 'contract_number'
    _order = 'id desc'
    _table = 'brief_contract'

    workflow_name = 'brief.contract'

    _states = {
        'draft': 'Черновик',
        'approval': 'Бриф на согласовании',
        'completion': 'Бриф на доработке',
        'preparation': 'Подготовка договора',
        'contract_approval': 'Согласование договора с обслуживающим направлением',
        'contract_completion': 'Доработка договора',
        'contract_agreed': 'Договор согласован',
        'approval_partner': 'Утверждение договора с партнером',
        'partner_cancel': 'Отмена',
        'contract_approved': 'Договор утвержден',
        'send_mail': 'Отправление договора по почте России',
        'send_express': 'Отправление договора экспресс-почтой',
        'send_courier': 'Отправка договора курьером',
        'waiting_receipt': 'Ожидание квитанции об возврате договора',
        'receipt_obtained': 'Квитанция получена',
        'meeting_scheduled': 'Встреча назначена',
        'meeting_cancel': 'Отмена встречи',
        'contract_signed': 'Оригинал договора',
        'cancel': 'Отмена',
        'cancel_2': 'Отмена',
    }

    def _check_access(self, cr, uid, ids, name, arg, context=None):
        """
            Динамически определяет роли на форме
        """
        res = {}
        if ids:
            data_ids = self.browse(cr, uid, ids, context)

            for data in data_ids:
                access = str()

                #  Менеджеры 2 и 3
                group_work = self.pool.get('res.groups').search(
                    cr,
                    1,
                    [
                        ('name', 'in', (
                            'Продажи / Менеджер по работе с партнерами',
                            'Продажи / Менеджер по развитию партнеров',
                            'Продажи / Руководитель по развитию партнеров',
                            'Продажи / Руководитель по работе с партнерами',
                            'Продажи / Менеджер по привлечению партнеров',
                            'Продажи / Руководитель по привлечению партнеров',
                        ))
                    ])
                users_work = self.pool.get('res.users').search(cr, 1, [('groups_id', 'in', group_work)], order='id')
                if uid in users_work:
                    access += 'm'

                #  Менеджер Москвы
                if data.responsible_id.id == uid:
                    access += 'r'

                #  Юрист
                if data.lawyer_id.id == uid:
                    access += 'l'

                #  Руководитель направления
                if data.service_id:
                    users = self.pool.get('res.users').search(cr, 1, [('groups_id', 'in', data.service_id.leader_group_id.id)], order='id')
                    users = [x for x in users if x not in [1, 5, 13, 18, 354]]
                    if uid in users:
                        access += 's'

                val = False

                letter = name[6]

                if letter in access:
                    val = True
                res[data.id] = val
        return res

    def _get_head(self, cr, user, ids, name, arg, context=None):
        res = {}
        if ids:
            data_ids = self.browse(cr, user, ids, context)
            for data in data_ids:
                service = self.pool.get('brief.services.stage').browse(cr, user, data.service_id)
                if service:
                    users = self.pool.get('res.users').search(cr, 1, [('groups_id', 'in', data.leader_group_id.id)], order='id')
                    if users:
                        u = [x for x in users if x not in [1, 5, 13, 18, 354, 472]]
                        if u:
                            res = {'service_head_id': u[0]}
        return {'value': res}

    _columns = {
        'state': fields.selection(
            zip(_states.keys(), _states.values()),
            'Статус',
            readonly=True,
            help='Поле отображает текущий этап Брифа.'),
        'usr_id': fields.many2one(
            'res.users',
            'Автор',
            readonly=True,
            select=True,
            help='Автор (менеджер продаж).'),
        'partner_id': fields.many2one(
            'res.partner',
            'Партнер',
            select=True,
            help='Партнер, по которому создан Бриф. Заполняется на этапе "Черновик". Обязательное к заполнению'),
        'lead_id': fields.many2one(
            'crm.lead',
            'Кандидат',
            select=True,
            help=''),
        'responsible_id': fields.many2one(
            'res.users',
            'Ответственный за подписание',
            select=True,
            domain="[('groups_id','in',[131])]",
            help='Заполняется при создании Брифа, указывается отетственный сотрудник за подписание договора'
        ),
        'lawyer_id': fields.many2one(
            'res.users',
            'Юрист',
            readonly=True,
            help='Заполняется автоматически'),
        'contract_number': fields.char(
            'Номер договора',
            size=150,
            help='Номер договора заполняется вручную в формате 13/АГ/06,\n'
                 'где 13 -год (2013),'
                 ' АГ - инициалы (имя, фамилия) менеджера, создавшего бриф,'
                 ' 06 - порядковый нормер договора по данному менеджеру'),
        'contract_date': fields.date(
            'Дата договора',
            help='Заполяется вручную'),
        'service_id': fields.many2one(
            'brief.services.stage',
            'Наименование услуги',
            select=True,
            help='Услуга по которой подписывается договор'),
        'service_head_id': fields.many2one(
            'res.users',
            'Руководитель направления',
            help='Руководитель направления по которому составлен договор.'),
        'for_calculation': fields.selection(
            [
                ('1', 'Тестовый период'),
                ('2', 'Ежемесячная услуга'),
                ('3', 'Единоразовая услуга')
            ],
            'Условия для расчета',
            help='Выпадающий список условий. Обязательное к заполнению.'),
        'amount': fields.char(
            'Сумма',
            size=50,
            help='Денежная сумма, на которую заключается договор.'),
        'currency': fields.many2one(
            'partner.currency',
            'Валюта',
            help='Валюта в которой составлен договор.'),
        'term': fields.selection(
            [
                ('year', 'Год'),
                ('mounth', 'Месяц'),
                ('week', 'Неделя'),
                ('un', 'Бессрочный')
            ],
            'Период',
            size=250,
            help='Срок действия договора.'),

        'payment_schedule': fields.selection(
            [
                ('100', '100% предоплаты'),
                ('0', 'Иное')
            ],
            'График оплаты',
            help='Заполняется в соответствии с оговоренным с клиентом графиком оплат.'),
        'amount_of_payment_ids': fields.one2many(
            'brief.contract.amount',
            'contract_id',
            'Размер платежа',
            help='Разбивка высталения счетов и проведения оплат.'),
        'type_of': fields.selection(
            [
                ('cash', 'Наличными'),
                ('settlement', 'Расчетный счет'),
                ('emoney', 'Электронные деньги')
            ],
            'Тип оплаты',
            help='Заполняется в соответствии с оговоренным с клиентом типом оплаты.'),

        'delivery_contract': fields.selection(
            [
                ('mail', 'Почта России'),
                ('express_mail', 'Экспресс-почта'),
                ('courier', 'Курьерская доставка')
            ],
            'Способ доставки договора',
            help='Способы доставки договора партнеру.'),

        'send_to_email': fields.selection(
            [
                ('yes', 'Да'),
                ('no', 'Нет')
            ],
            "Направить партнеру договор по эл. почте",
            help='Направить партнеру договор по эл. почте?'),
        'delivery_original': fields.selection(
            [
                ('mail', 'Почта России'),
                ('express_mail', 'Экспресс-почта'),
                ('courier', 'Курьерская доставка')
            ],
            "Способ доставки закрывающих документов",
            help='Способы доставки закрывающих документов партнеру'),
        'contract_file': fields.many2one(
            'attach.files',
            'Проект договора',
            help='Прикрепленный файл проекта договора (до согласования с Партнером)'),
        'contract_re_file': fields.many2one(
            'attach.files',
            'Файл доработки договора',
            help='Прикрепленный файл доработок по договору'),
        'contract_approved_file': fields.many2one(
            'attach.files',
            'Утвержденный договор',
            help='Окончательный вариант договора (для подписания)'),
        'icontract_file': fields.many2one(
            'attach.files',
            'Договор с электронной печатью',
            help='Окончательный вариант договора с эл. печатью'),
        'pcontract_file': fields.many2one(
            'attach.files',
            'Подписанный договор',
            help='Прикрепляется скан-копия подписанного договора'),

        'notes': fields.text(
            "Примечания",
            help=''),

        'history_ids': fields.one2many(
            "brief.contract.history",
            "contract_id",
            "История переходов",
            help='Записывается история смены этапов Брифа. Заполняется автоматически.'),

        'comment_ids': fields.one2many(
            "brief.contract.comment",
            "contract_id",
            "Комментарии",
            help='Таблица для добавления комментариев в случае необходимости'),
        'comment_rework': fields.text(
            "Комментарий по доработке брифа",
            help='Текстовое обязательное к заполнению поле в случае перевода брифа "Бриф на доработку"'),
        'comment_rework_2': fields.text(
            "Комментарий по доработке договора",
            help='Текстовое обязательное к заполнению поле в случае перевода брифа "Договор на доработку"'),
        'comment_rework_3': fields.text(
            "Комментарий по доработке перед утверждением договора",
            help='Текстовое обязательное к заполнению поле в случае перевода брифа "Доработка перед утверждением"'),
        'canceled_reasons': fields.text(
            "Причины отмены встречи",
            help='Текстовое обязательное к заполнению поле в случае перевода брифа "Встреча отменена"'),
        'file_ids': fields.one2many(
            "attach.files",
            "obj_id",
            "Прикрепленные файлы",
            help='Таблица для прикрепления дополниельных файлов'
        ),

        'bank_id': fields.many2one(
            'res.partner.bank',
            'Реквизиты партнера',
            help='Банковские реквизиты Партнера.'),
        'send_query': fields.boolean(
            'Клиенту отправлен запрос на уставные документы',
            help=''),

        'receipt_get': fields.boolean(
            'Квитанции получена',
            help='Отметка о получении квитанции об оплате'),
        'receipt_file': fields.many2one(
            'attach.files',
            'Копия квитанции',
            help='Прикрепленный файл квитации'),

        'check_m': fields.function(
            _check_access,
            method=True,
            string="Менеджеры 2 и 3",
            type="boolean",
            invisible=True),
        'check_r': fields.function(
            _check_access,
            method=True,
            string="Менеджеры Москвы",
            type="boolean",
            invisible=True),
        'check_l': fields.function(
            _check_access,
            method=True,
            string="Юрист",
            type="boolean",
            invisible=True),
        'check_s': fields.function(
            _check_access,
            method=True,
            string="Руковолитель направления",
            type="boolean",
            invisible=True),
        'create_date': fields.datetime(
            'Дата создания',
            readonly=True,
            help=''),
        'from': fields.char('from', size=10),

        'wuser_ids': fields.integer("Без этих людей"),
        'account_id': fields.many2one(
            'account.account',
            'Фирма',
            domain=[('type', '!=', 'closed'), ('company_id', '=', 4)],
            required=True,
            help='Фирма, от лица которой создается данный счет.'
        ),

    }

    _defaults = {
        'usr_id': lambda self, cr, uid, context: uid,
        'lawyer_id': lambda *a: 474,
        'partner_id': lambda self, cr, uid, context: context.get('partner_id', False),
        'service_id': lambda self, cr, uid, context: context.get('service_id', False),
        'lead_id': lambda self, cr, uid, context: context.get('lead_id', False),
        'state': 'draft',
        'from': lambda self, cr, uid, context: context.get('from', False),
        'wuser_ids': 153,
    }

    def _get_name(self, number='', date=''):
        if number:
            name = number.encode('utf-8')
        else:
            name = ''
        if date and number:
            name += ' ({0})'.format(date.encode('utf-8'))
        elif date and not number:
            name += '{0}'.format(date.encode('utf-8'))
        return name

    def name_get(self, cr, user, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]

        return [(r['id'], tools.ustr(self._get_name(r['contract_number'], r['contract_date']))) for r in self.read(cr, user, ids,
            ['contract_number', 'contract_date'], context, load='_classic_write')]

    def onchange_service(self, cr, user, ids, service, context=None):
        res = {}
        if service:
            data = self.pool.get('brief.services.stage').browse(cr, user, service)
            users = self.pool.get('res.users').search(cr, 1, [('groups_id', 'in', data.leader_group_id.id)], order='id')
            if users:
                u = [x for x in users if x not in [1, 5, 13, 18, 354]]
                if u:
                    res = {'service_head_id': u[0]}

        return {'value': res}

    def workflow_setter(self, cr, uid, ids, state='draft'):
        return self.write(cr, uid, ids, {'state': state})

    def action_add(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        pool = self.pool.get('res.partner.bank')
        bank_id = 0
        if partner_id:
            obj_ids = pool.search(cr, uid, [('partner_id', '=', partner_id)])

            if obj_ids:
                bank_id = obj_ids[0]

        return {'value': {'bank_id': bank_id}}

    @notify.msg_send(_name, 'brief.contract')
    def write(self, cr, user, ids, values, context=None):
        if values.get('from'):
            del values['from']
        data = self.browse(cr, user, ids)[0]
        if data.service_id or values.get('service_id', False):
            service_id = values['service_id'] if values.get('service_id', False) else data.service_id.id
            service = self.pool.get('brief.services.stage').browse(cr, 1, service_id)
            if service:
                users = self.pool.get('res.users').search(cr, 1, [('groups_id', 'in', service.leader_group_id.id)], order='id')
                if users:
                    u = [x for x in users if x not in [1, 5, 13, 18, 354, 472]]
                    if u:
                        values['service_head_id'] = u[0]
        next_state = values.get('state', False)
        state = data.state

        error = ''
        if next_state and next_state != state:
            #  draft -> approval
            if state == 'draft' and next_state == 'approval':
                #if (not values.get('partner_id', False) and not data.partner_id) or (not values.get('lead_id', False) and not data.lead_id):
                #    error += " Выберите Партнера или Кандидата; "
                if not values.get('contract_number', False) and not data.contract_number:
                    error += " Введите Номер договора; "
                if not values.get('contract_date', False) and not data.contract_date:
                    error += " Введите Дату договора; "
                if not values.get('service_id', False) and not data.service_id:
                    error += " Выберите Услугу; "

                for_calc = values['for_calculation'] if values.get('for_calculation', False) else data.for_calculation
                if not for_calc:
                    error += " Выберите Условия для расчета; "
                else:
                    if for_calc in ('1', '2') and not values.get('term', False) and not data.term:
                        error += " Введите период оплаты; "
                    if not values.get('amount') and not data.amount:
                        error += " Введите сумму оплаты; "
                    if not values.get('currency', False) and not data.currency:
                        error += " Выберите Валюту оплаты; "
                payment_schedule = values['payment_schedule'] if values.get('payment_schedule', False) else data.payment_schedule
                if not payment_schedule:
                    error += " Выберите График оплаты; "
                else:
                    if payment_schedule == "0" and not data.amount_of_payment_ids:
                        error += " Введите Размеры платежа; "

                if not values.get('type_of', False) and not data.type_of:
                    error += " Выберите Тип оплаты; "

                if not values.get('bank_id', False) and not data.bank_id:
                    error += " Укажите Банковский счет; "

                if not values.get('delivery_contract', False) and not data.delivery_contract:
                    error += " Выберите Способ доставки договора; "

                if not values.get('send_to_email', False) and not data.send_to_email:
                    error += " Укажите Отправлять договор партнеру по эл. почте?; "

                if not values.get('delivery_original', False) and not data.delivery_original:
                    error += " Выберите Способ доставки закрывающих документов; "

            #  draft -> cancel
            if state == 'draft' and next_state == 'cancel':
                print values
            #  approval -> completion
            if state == 'approval' and next_state == 'completion':
                if not values.get('comment_rework', False) and not data.comment_rework:
                    error += " Введите Комментарий по доработке брифа; "
            #  completion -> approval
            if state == 'completion' and next_state == 'approval':
                pass
            #  approval -> preparation
            if state == 'approval' and next_state == 'preparation':
                pass
            #  preparation -> contract_approval
            if state == 'preparation' and next_state == 'contract_approval':
                if not values.get('contract_file', False) and not data.contract_file:
                    error += " Необходимо вложить Проект договора; "
            #  contract_approval -> contract_completion
            if state == 'contract_approval' and next_state == 'contract_completion':
                if not values.get('comment_rework_2', False) and not data.comment_rework_2 and not values.get('contract_re_file', False) and not data.contract_re_file:
                    error += " Введите Комментарий по доработке договора или прикрепите файл доработки; "
            #  contract_completion -> contract_approval
            if state == 'contract_completion' and next_state == 'contract_approval':
                pass
            #  contract_approval -> contract_agreed
            if state == 'contract_approval' and next_state == 'contract_agreed':
                pass
            #  contract_agreed -> approval_partner
            if state == 'contract_agreed' and next_state == 'approval_partner':
                pass
            #  approval_partner -> contract_completion
            if state == 'approval_partner' and next_state == 'contract_completion':
                if not values.get('comment_rework_3', False) and not data.comment_rework_3 and not values.get('contract_re_file', False) and not data.contract_re_file:
                    error += " Введите Комментарий по доработке перед утверждением договора или прикрепите файл доработки; "
            #  approval_partner -> partner_cancel
            if state == 'approval_partner' and next_state == 'partner_cancel':
                pass
            #  partner_cancel -> approval_partner
            if state == 'partner_cancel' and next_state == 'approval_partner':
                pass
            #  approval_partner -> contract_approved
            if state == 'approval_partner' and next_state == 'contract_approved':
                if not values.get('contract_approved_file', False) and not data.contract_approved_file:
                    error += " Прикрепите утвержденный договор; "

            #  contract_approved -> send_mail
            if state == 'contract_approved' and next_state == 'send_mail':
                pass
            #  contract_approved -> send_express
            if state == 'contract_approved' and next_state == 'send_express':
                pass
            #  contract_approved -> send_courier
            if state == 'contract_approved' and next_state == 'send_courier':
                pass
            #  send_courier -> meeting_scheduled
            if state == 'send_courier' and next_state == 'meeting_scheduled':
                pass
            #  send_mail -> waiting_receipt
            if state == 'send_mail' and next_state == 'waiting_receipt':
                pass
            #  send_express -> waiting_receipt
            if state == 'send_express' and next_state == 'waiting_receipt':
                pass
            #  waiting_receipt -> meeting_scheduled
            if state == 'waiting_receipt' and next_state == 'meeting_scheduled':
                pass
            #  meeting_scheduled -> meeting_cancel
            if state == 'meeting_scheduled' and next_state == 'meeting_cancel':
                pass
            #  meeting_scheduled -> contract_signed
            if state == 'meeting_scheduled' and next_state == 'contract_signed':
                if not data.pcontract_file and not values.get('pcontract_file', False):
                    error += " Вложите подписанный договр; "
            #  waiting_receipt -> receipt_obtained
            if state == 'waiting_receipt' and next_state == 'receipt_obtained':
                if not values.get('receipt_file', False) and not data.receipt_file:
                    error += "Получена ли квитанция? Вложите копию квитанции; "
            #  receipt_obtained -> contract_signed
            if state == 'receipt_obtained' and next_state == 'contract_signed':
                if not data.pcontract_file and not values.get('pcontract_file', False):
                    error += " Вложите подписанный договр; "

            if error:
                raise osv.except_osv("Ошибка в незаполенных полях", error)

            values.update({'history_ids': [(0, 0, {
                'usr_id': user,
                'state': self._states[next_state]
            })]})

        return super(BriefContract, self).write(cr, user, ids, values, context)

    def create(self, cr, user, vals, context=None):
        if vals.get('from'):
            vals['from'] = None

        if vals.get('partner_id'):
            self.pool.get('res.partner').write(cr, user, [vals['partner_id']], {'partner_base': 'hot'})
        return super(BriefContract, self).create(cr, user, vals, context)


BriefContract()


class BriefContractAmount(Model):
    _name = 'brief.contract.amount'
    _description = u'Бриф на договор - Размер платежа'
    _log_create = True

    _columns = {
        'name': fields.char('Размер платежа', size=255),
        'term': fields.char('Срок выставления счета на оплату', size=255),
        'contract_id': fields.many2one('brief.contract', 'Бриф на договор', invisible=True),
    }


BriefContractAmount()


class BriefContractComments(Model):
    _name = 'brief.contract.comment'
    _description = u'Бриф на договор - Комментарии'
    _log_create = True
    _order = "create_date desc"

    _columns = {
        'name': fields.text('Комментарий'),
        'usr_id': fields.many2one('res.users', 'Автор', readonly=True),
        'contract_id': fields.many2one('brief.contract', 'Бриф на встречу', invisible=True),
    }

    _defaults = {
        'usr_id': lambda self, cr, uid, context: uid,
    }


BriefContractComments()


class BriefContractHistory(Model):
    _name = 'brief.contract.history'
    _description = u'Бриф на договор - История переходов'
    _log_create = True
    _order = "create_date desc"
    _rec_name = 'state'

    _columns = {
        'usr_id': fields.many2one('res.users', 'Перевел'),
        'state': fields.char('На этап', size=65),
        'contract_id': fields.many2one('brief.contract', 'Бриф на встречу', invisible=True),
        'create_date': fields.datetime('Дата', readonly=True),
    }


BriefContractHistory()


class res_partner(Model):
    _inherit = "res.partner"

    _columns = {
        'brief_contract_ids': fields.one2many(
            'brief.contract',
            'partner_id',
            u'Брифы на договор'
        ),
    }

    def create_brief_contract(self, cr, uid, ids, context=None):
        """
            Открывает окно с брифом и переданными данными
        """
        data = False
        if ids:
            action_pool = self.pool.get('ir.actions.act_window')
            action_id = action_pool.search(cr, uid, [('name', '=', 'Создать бриф на договор ')], context=context)
            if action_id:
                data = action_pool.read(cr, uid, action_id[0], context=context)

                data.update({
                    'nodestroy': True,
                    'context': {
                        'partner_id': ids[0],
                        'from': 'lp'
                    }
                })

        return data

res_partner()
