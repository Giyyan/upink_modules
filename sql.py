# -*- encoding: utf-8 -*-
import psycopg2

# conn_string = "host='217.12.219.143' dbname='zombieland' user='wichita' password='vjq1gfhjkm'"
# conn_string = "host='217.12.219.143' dbname='mask' user='stanley_ipkiss' password='vjq1gfhjkm'"
# conn_string = "host='217.12.219.143' dbname='number_23' user='fingerling' password='vjq1gfhjkm'"
conn_string = "host='46.28.67.221' dbname='die_hard' user='john_mcclane' password='vjq1gfhjkm'"
conn = psycopg2.connect(conn_string)

cursor = conn.cursor()

#  Создаем компании
cursor.execute("SELECT rml_footer1, rml_header, rml_header2, rml_header3, rml_header1, logo_web, currency_id, partner_id, schedule_range, security_lead, paper_format FROM res_company WHERE id=4;")
company = cursor.fetchone()
cursor.execute("INSERT INTO res_company (parent_id, name, rml_footer1, rml_header, rml_header2, rml_header3, rml_header1, logo_web, currency_id, partner_id, schedule_range, security_lead, paper_format) VALUES (4, 'PPC', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", company)
ppc_id = cursor.fetchone()[0]
cursor.execute("INSERT INTO res_company (parent_id, name, rml_footer1, rml_header, rml_header2, rml_header3, rml_header1, logo_web, currency_id, partner_id, schedule_range, security_lead, paper_format) VALUES (4, 'CALL', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;", company)
call_id = cursor.fetchone()[0]

cursor.execute("SELECT partner_id FROM partner_added_services WHERE service_id in (SELECT id FROM brief_services_stage WHERE direction not in ('CALL', 'SEO') and direction is not null) and partner_id is not null;")
benja = set([partner[0] for partner in cursor.fetchall()])

cursor.execute("SELECT partner_id FROM partner_added_services WHERE service_id in (SELECT id FROM brief_services_stage WHERE direction in ('CALL', 'SEO')) and partner_id is not null;")
kirja = set([partner[0] for partner in cursor.fetchall()])

double_shit = benja & kirja

cursor.execute("""SELECT id, create_uid, create_date, write_date, write_uid, comment, ean13, date, active, lang, customer, credit_limit, user_id, title, website, parent_id, employee, supplier, ref, vat, last_reconciliation_date, debit_limit, section_id, provider_category, reference, confirm_status, bonus_reason, partner_type, forward_to, corporate_admin_password, password, bonus_amount, admin_panel_login, corporate_admin_panel, section_id_sales, next_call, admin_panel_password, refusion_reason, rebate_system, refusion_description, main_partner, asterisk_date_sh, corporate_site_url, login, partner_state, delivery_type, sale_type, delivery_from, budget, activity, pay_notes, pay_type, source, price_type, author_id, cand_type, id_vat, has_eshop, what_done, bonus_friend, fin_dog, description, categ_id, color, opt_out, name_official, contract_date, contract_num, kpp, inn, okpo, terms_of_service, quality_feedback, completeness_of_reporting, client_type, conformity, lead, ur_name, priority, next_call_comment, stage_id, name, partner_base, date_finish_to, date_finish_from, date_start_to, date_start_from, zone, another, key_person, key_moment
    FROM res_partner
    WHERE id in %s;""", (tuple(double_shit),))
for partner in cursor.fetchall():
    partner = list(partner)
    partner.append(call_id)
    cursor.execute("""INSERT INTO res_partner
     (create_uid, create_date, write_date, write_uid, comment, ean13, date, active, lang, customer, credit_limit, user_id, title, website, parent_id, employee, supplier, ref, vat, last_reconciliation_date, debit_limit, section_id, provider_category, reference, confirm_status, bonus_reason, partner_type, forward_to, corporate_admin_password, password, bonus_amount, admin_panel_login, corporate_admin_panel, section_id_sales, next_call, admin_panel_password, refusion_reason, rebate_system, refusion_description, main_partner, asterisk_date_sh, corporate_site_url, login, partner_state, delivery_type, sale_type, delivery_from, budget, activity, pay_notes, pay_type, source, price_type, author_id, cand_type, id_vat, has_eshop, what_done, bonus_friend, fin_dog, description, categ_id, color, opt_out, name_official, contract_date, contract_num, kpp, inn, okpo, terms_of_service, quality_feedback, completeness_of_reporting, client_type, conformity, lead, ur_name, priority, next_call_comment, stage_id, name, partner_base, date_finish_to, date_finish_from, date_start_to, date_start_from, zone, another, key_person, key_moment, company_id)
      VALUES
       (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""", partner[1:])
    new_id = cursor.fetchone()[0]

    #  Подключенные услуги
    cursor.execute("UPDATE partner_added_services SET partner_id=%s WHERE service_id in (SELECT id FROM brief_services_stage WHERE direction in ('CALL', 'SEO')) and partner_id=%s;", (new_id, partner[0]))

    #  Брифы на просчет
    cursor.execute("UPDATE brief_main SET partner_id=%s WHERE services_ids in (SELECT id FROM brief_services_stage WHERE direction in ('CALL', 'SEO')) and partner_id=%s;", (new_id, partner[0]))

    #  Брифы на договор
    cursor.execute("UPDATE brief_contract SET partner_id=%s WHERE service_id in (SELECT id FROM brief_services_stage WHERE direction in ('CALL', 'SEO')) and partner_id=%s;", (new_id, partner[0]))

    #  Процессы
    cursor.execute("UPDATE process_launch SET partner_id=%s WHERE service_id in (SELECT id FROM brief_services_stage WHERE direction in ('CALL', 'SEO')) and partner_id=%s;", (new_id, partner[0]))

cursor.execute('UPDATE res_partner SET company_id=%s WHERE id in %s;', (call_id, tuple(kirja)))
cursor.execute('UPDATE res_partner SET company_id=%s WHERE id in %s;', (ppc_id, tuple(benja)))


# cursor.execute("SELECT domain_force FROM ir_rule WHERE model_id in (SELECT id FROM ir_model WHERE model in ('res.partner', 'brief.main', 'brief.contract', 'brief.meeting', 'account.invoice', 'task', 'kpi.kpi', 'kpi.smart', 'process.launch', 'help.desk'));")
# cursor.execute("SELECT domain_force, id FROM ir_rule WHERE model_id in (SELECT id FROM ir_model WHERE model in ('res.partner', 'hr.employee', 'res.users'));")
# for record in cursor.fetchall():
#     domain, rule_id = record
#     if 'company_id' not in domain:
#         new_domain = "{}, ('company_id.id', '=', user.company_id.id)]".format(domain[:-1].rstrip(','),)
#         cursor.execute('UPDATE ir_rule SET domain_force=%s WHERE id=%s;', (new_domain, rule_id))
# for model in ('res.partner', 'hr.employee', 'res.users'):
for model in (59, 78, 145):
    cursor.execute("""INSERT INTO ir_rule (model_id, domain_force, name, global, perm_unlink, perm_write, perm_read, perm_create) VALUES (%s, '["|", ("company_id.id", "=", user.company_id.id), ("company_id.id", "child_of", user.company_id.id)]', %s, true, true, true, true, true)""", (model, "{}_global".format(model,)))

#
# cursor.execute("SELECT domain_force, id FROM ir_rule WHERE model_id in (SELECT id FROM ir_model WHERE model in ('brief.main', 'brief.contract', 'brief.meeting', 'account.invoice', 'res.partner.address', 'process.launch'));")
# for record in cursor.fetchall():
#     domain, rule_id = record
#     if 'company_id' not in domain:
#         new_domain = "{}, ('partner_id.company_id.id', '=', user.company_id.id)]".format(domain[:-1].rstrip(','),)
#         cursor.execute('UPDATE ir_rule SET domain_force=%s WHERE id=%s;', (new_domain, rule_id))
for model in (60, 188, 492, 633, 625, 755):
    cursor.execute("""INSERT INTO ir_rule (model_id, domain_force, name, global, perm_unlink, perm_write, perm_read, perm_create) VALUES (%s, '["|", ("partner_id.company_id.id", "=", user.company_id.id), ("partner_id.company_id.id", "child_of", user.company_id.id)]', %s, true, true, true, true, true)""", (model, "{}_global".format(model,)))
#
# cursor.execute("SELECT domain_force, id FROM ir_rule WHERE model_id in (SELECT id FROM ir_model WHERE model in ('kpi.smart', 'kpi.kpi', 'help.desk'));")
# for record in cursor.fetchall():
#     domain, rule_id = record
#     if 'company_id' not in domain:
#         new_domain = "{}, ('employee_id.company_id.id', '=', user.company_id.id)]".format(domain[:-1].rstrip(','),)
#         cursor.execute('UPDATE ir_rule SET domain_force=%s WHERE id=%s;', (new_domain, rule_id))
for model in (517, 590):
    cursor.execute("""INSERT INTO ir_rule (model_id, domain_force, name, global, perm_unlink, perm_write, perm_read, perm_create) VALUES (%s, '["|", ("employee_id.company_id.id", "=", user.company_id.id), ("employee_id.company_id.id", "child_of", user.company_id.id)]', %s, true, true, true, true, true)""", (model, "{}_global".format(model,)))
#
# cursor.execute("UPDATE res_users SET active=false WHERE id in (665, 630, 563, 693, 760, 772, 631, 534, 686, 453, 658, 723, 81, 412, 384, 336, 651, 138, 548, 711, 364, 62, 469, 553, 205, 687, 652, 656, 777, 154, 348, 747, 765, 262, 634, 164, 635, 638, 713, 530)")
#
# cursor.execute("UPDATE hr_employee SET active=false WHERE user_id in (SELECT id FROM res_users WHERE id in (665, 630, 563, 693, 760, 772, 631, 534, 686, 453, 658, 723, 81, 412, 384, 336, 651, 138, 548, 711, 364, 62, 469, 553, 205, 687, 652, 656, 777, 154, 348, 747, 765, 262, 634, 164, 635, 638, 713, 530))")

# cursor.execute("UPDATE hr_employee SET active=false WHERE company_id=3)")
# cursor.execute("UPDATE res_users SET active=false WHERE company_id=3)")
# cursor.execute("UPDATE res_users SET company_id=4 WHERE company_id=1)")
# cursor.execute("UPDATE hr_employee SET company_id=4 WHERE company_id=1)")

conn.commit()
cursor.close()
conn.close()
