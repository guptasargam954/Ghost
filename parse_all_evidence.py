import os, csv, json, re, glob, sqlite3, base64, zlib
from datetime import datetime
from collections import defaultdict

repo = 'repo/hackerrank-orchestrate-october26-main'

with open(f'{repo}/dataset/evidence_files.csv') as f:
    ev_files = {r['file_id']: r for r in csv.DictReader(f)}
    path_to_ev = {r['file_path']: r['file_id'] for r in ev_files.values()}

# User identity resolution
with open(f'{repo}/dataset/user_identities.csv') as f:
    users = {r['user_id']: r for r in csv.DictReader(f)}
    email_to_uid = {r['email'].strip().lower(): r['user_id'] for r in users.values()}

with open(f'{repo}/dataset/user_audit_log.csv') as f:
    audit_rows = list(csv.DictReader(f))
    for r in audit_rows:
        if r['field_name'] == 'email':
            email_to_uid[r['old_value'].strip().lower()] = r['user_id']
            email_to_uid[r['new_value'].strip().lower()] = r['user_id']

user_idents = {}
uid_by_email = dict(email_to_uid)
uid_by_phone = {}
uid_by_hash = {}

for uid, u in users.items():
    user_idents[uid] = {
        'uid': uid,
        'emails': {u['email'].strip().lower()},
        'phones': {u['phone'].strip()},
        'names': {u['name'].strip()},
        'hashes': {u['email_hash'].strip().lower()}
    }
    uid_by_phone[u['phone'].strip()] = uid
    uid_by_hash[u['email_hash'].strip().lower()] = uid

for r in audit_rows:
    uid = r['user_id']
    if uid in user_idents:
        fn = r['field_name']
        if fn == 'email':
            user_idents[uid]['emails'].add(r['old_value'].strip().lower())
            user_idents[uid]['emails'].add(r['new_value'].strip().lower())
            uid_by_email[r['old_value'].strip().lower()] = uid
            uid_by_email[r['new_value'].strip().lower()] = uid
        elif fn == 'phone':
            user_idents[uid]['phones'].add(r['old_value'].strip())
            user_idents[uid]['phones'].add(r['new_value'].strip())
            uid_by_phone[r['old_value'].strip()] = uid
            uid_by_phone[r['new_value'].strip()] = uid
        elif fn == 'name':
            user_idents[uid]['names'].add(r['old_value'].strip())
            user_idents[uid]['names'].add(r['new_value'].strip())

def resolve_uid(email=None, phone=None, user_id=None, email_hash=None):
    if user_id and user_id in user_idents:
        return user_id
    if email and email.strip().lower() in uid_by_email:
        return uid_by_email[email.strip().lower()]
    if phone and phone.strip() in uid_by_phone:
        return uid_by_phone[phone.strip()]
    if email_hash and email_hash.strip().lower() in uid_by_hash:
        return uid_by_hash[email_hash.strip().lower()]
    return None

facts = []

def add_fact(file_id, captured_at, system_id, resource_id, uid, state, op, exposed_pii=False, note=""):
    facts.append({
        'file_id': file_id,
        'captured_at': captured_at,
        'system_id': system_id,
        'resource_id': resource_id,
        'uid': uid,
        'state': state,
        'operation': op,
        'exposed_pii': exposed_pii,
        'note': note
    })

# 1. service_resource_export_*.json
for p in sorted(glob.glob(f'{repo}/dataset/evidence/records/service_resource_export_*.json')):
    rel_p = 'evidence/records/' + os.path.basename(p)
    fid = path_to_ev.get(rel_p)
    if not fid: continue
    cap_at = ev_files[fid]['captured_at']
    with open(p) as f:
        d = json.load(f)
    se = d.get('service_exports', {})
    
    for it in se.get('account_service', {}).get('profile_lookups', []):
        prof = it.get('profile')
        rid = it['resource_id']
        if prof:
            uid = resolve_uid(email=prof.get('email'), phone=prof.get('phone'), user_id=prof.get('customer_reference'))
            add_fact(fid, cap_at, 'account_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
        else:
            add_fact(fid, cap_at, 'account_service', rid, None, 'ABSENT', 'VERIFY_RECORD_ABSENT')
            
    for it in se.get('analytics_platform', {}).get('profiles', []):
        rid = it['resource_id']
        uid = resolve_uid(email=it.get('email'), phone=it.get('phone'), user_id=it.get('customer_reference'), email_hash=it.get('email_hash'))
        has_pii = any(it.get(k) for k in ['email', 'phone', 'customer_reference', 'email_hash'])
        if has_pii:
            add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
        else:
            add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'ANONYMIZED', 'VERIFY_RECORD_ANONYMIZED')
            
    for it in se.get('backup_service', {}).get('restore_entries', []):
        rid = it['resource_id']
        uid = resolve_uid(email=it.get('customer_email'), user_id=it.get('customer_reference'))
        if it.get('restore_allowed'):
            add_fact(fid, cap_at, 'backup_service', rid, uid, 'ACTIVE', 'REPORT_RESTORE_RISK')
        else:
            add_fact(fid, cap_at, 'backup_service', rid, uid, 'BLOCKED', 'VERIFY_RESTORE_BLOCKED')
            
    for it in se.get('export_service', {}).get('exports', []):
        rid = it['resource_id']
        uid = resolve_uid(email=it.get('owner_email'), phone=it.get('owner_phone'), user_id=it.get('customer_reference'))
        add_fact(fid, cap_at, 'export_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
        
    for it in se.get('integration_service', {}).get('connectors', []):
        rid = it['resource_id']
        uid = resolve_uid(email=it.get('customer_email'), user_id=it.get('customer_reference'))
        if it.get('enabled'):
            add_fact(fid, cap_at, 'integration_service', rid, uid, 'ACTIVE', 'REPORT_ACTIVE_DATA_FLOW')
        else:
            add_fact(fid, cap_at, 'integration_service', rid, uid, 'DISABLED', 'VERIFY_DATA_FLOW_DISABLED')
            
    for it in se.get('search_service', {}).get('index_queries', []):
        rid = it['resource_id']
        hits = it.get('hits', {})
        docs = hits.get('documents', [])
        uid = None
        for doc in docs:
            doc_uid = resolve_uid(email=doc.get('email'), phone=doc.get('phone'), user_id=doc.get('customer_reference'))
            if doc_uid: uid = doc_uid
        if not uid and it.get('query'):
            uid = resolve_uid(email=it.get('query'))
        if hits.get('total', 0) > 0 or len(docs) > 0:
            add_fact(fid, cap_at, 'search_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
        else:
            add_fact(fid, cap_at, 'search_service', rid, uid, 'ABSENT', 'VERIFY_RECORD_ABSENT')
            
    for it in se.get('security_service', {}).get('audit_records', []):
        rid = it['resource_id']
        uid = resolve_uid(user_id=it.get('subject_reference'))
        add_fact(fid, cap_at, 'security_service', rid, uid, 'PRESENT', 'VERIFY_RECORD_PRESENT')
        
    for it in se.get('support_platform', {}).get('tickets', []):
        rid = it['resource_id']
        uid = resolve_uid(email=it.get('requester_email'), phone=it.get('requester_phone'), user_id=it.get('customer_reference'))
        has_pii = any(it.get(k) for k in ['requester_email', 'requester_name', 'requester_phone'])
        if has_pii:
            add_fact(fid, cap_at, 'support_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
        else:
            add_fact(fid, cap_at, 'support_platform', rid, uid, 'REDACTED', 'VERIFY_RECORD_REDACTED')

# 2. customer_data_snapshot_bundle_*.json
for p in sorted(glob.glob(f'{repo}/dataset/evidence/records/customer_data_snapshot_bundle_*.json')):
    rel_p = 'evidence/records/' + os.path.basename(p)
    fid = path_to_ev.get(rel_p)
    if not fid: continue
    cap_at = ev_files[fid]['captured_at']
    with open(p) as f:
        d = json.load(f)
    for sn in d.get('snapshots', []):
        ds = sn.get('data_store')
        recs = sn.get('records', [])
        if ds == 'account_service':
            for r in recs:
                rid = r['resource_id']
                uid = resolve_uid(email=r.get('email'), phone=r.get('phone'), user_id=r.get('user_id') or r.get('customer_reference'))
                add_fact(fid, cap_at, 'account_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
        elif ds == 'identity_service':
            for r in recs:
                rid = r['resource_id']
                uid = resolve_uid(email=r.get('email'), phone=r.get('phone'), user_id=r.get('subject_reference'), email_hash=r.get('email_hash'))
                has_pii = any(r.get(k) for k in ['name', 'email', 'phone', 'email_hash'])
                if has_pii:
                    add_fact(fid, cap_at, 'identity_service', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
                else:
                    add_fact(fid, cap_at, 'identity_service', rid, uid, 'REDACTED', 'VERIFY_RECORD_REDACTED')
        elif ds == 'security_service':
            for r in recs:
                rid = r['resource_id']
                uid = resolve_uid(user_id=r.get('subject_reference'))
                add_fact(fid, cap_at, 'security_service', rid, uid, 'PRESENT', 'VERIFY_RECORD_PRESENT')

# 3. customer_account_handover_20261001.txt
txt_path = f'{repo}/dataset/evidence/records/customer_account_handover_20261001.txt'
fid = path_to_ev.get('evidence/records/customer_account_handover_20261001.txt')
if fid and os.path.exists(txt_path):
    cap_at = ev_files[fid]['captured_at']
    with open(txt_path) as f:
        for line in f:
            line = line.strip()
            if not line.startswith('-'): continue
            parts = [p.strip() for p in line.lstrip('-').split('|')]
            if len(parts) >= 6:
                ts, sys_id, rid, cat, stat, ident = parts[:6]
                uid = resolve_uid(email=ident, user_id=ident)
                if sys_id == 'account_service':
                    if stat == 'NOT_FOUND': add_fact(fid, cap_at, sys_id, rid, uid, 'ABSENT', 'VERIFY_RECORD_ABSENT')
                    else: add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
                elif sys_id == 'analytics_platform':
                    if stat == 'ANONYMIZED': add_fact(fid, cap_at, sys_id, rid, uid, 'ANONYMIZED', 'VERIFY_RECORD_ANONYMIZED')
                    else: add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
                elif sys_id == 'backup_service':
                    if stat == 'BLOCKED': add_fact(fid, cap_at, sys_id, rid, uid, 'BLOCKED', 'VERIFY_RESTORE_BLOCKED')
                    else: add_fact(fid, cap_at, sys_id, rid, uid, 'ACTIVE', 'REPORT_RESTORE_RISK')
                elif sys_id == 'export_service':
                    add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
                elif sys_id == 'integration_service':
                    if stat == 'DISABLED': add_fact(fid, cap_at, sys_id, rid, uid, 'DISABLED', 'VERIFY_DATA_FLOW_DISABLED')
                    else: add_fact(fid, cap_at, sys_id, rid, uid, 'ACTIVE', 'REPORT_ACTIVE_DATA_FLOW')
                elif sys_id == 'search_service':
                    if stat == 'FOUND': add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
                    else: add_fact(fid, cap_at, sys_id, rid, uid, 'ABSENT', 'VERIFY_RECORD_ABSENT')
                elif sys_id == 'security_service':
                    add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'VERIFY_RECORD_PRESENT')
                elif sys_id == 'support_platform':
                    if stat == 'REDACTED': add_fact(fid, cap_at, sys_id, rid, uid, 'REDACTED', 'VERIFY_RECORD_REDACTED')
                    elif cat == 'SUPPORT_ATTACHMENT': add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
                    else: add_fact(fid, cap_at, sys_id, rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)

# 4. customer_export_jobs_20260914.json
p = f'{repo}/dataset/evidence/records/customer_export_jobs_20260914.json'
fid = path_to_ev.get('evidence/records/customer_export_jobs_20260914.json')
if fid and os.path.exists(p):
    cap_at = ev_files[fid]['captured_at']
    with open(p) as f:
        d = json.load(f)
    for r in d.get('records', []):
        rid = r['resource_id']
        uid = resolve_uid(email=r.get('owner_email'))
        if r.get('download_available'):
            add_fact(fid, cap_at, 'export_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')

# 5. customer_analytics_report_20260907.json
p = f'{repo}/dataset/evidence/records/customer_analytics_report_20260907.json'
fid = path_to_ev.get('evidence/records/customer_analytics_report_20260907.json')
if fid and os.path.exists(p):
    cap_at = ev_files[fid]['captured_at']
    with open(p) as f:
        d = json.load(f)
    for r in d.get('records', []):
        rid = r['resource_id']
        uid = resolve_uid(email=r.get('email'), user_id=r.get('customer_reference'), phone=r.get('phone'))
        has_pii = any(r.get(k) for k in ['email', 'phone', 'customer_reference', 'email_hash'])
        if has_pii:
            add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
        else:
            add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'ANONYMIZED', 'VERIFY_RECORD_ANONYMIZED')

# 6. connector_configurations_20260812.json
p = f'{repo}/dataset/evidence/records/connector_configurations_20260812.json'
fid = path_to_ev.get('evidence/records/connector_configurations_20260812.json')
if fid and os.path.exists(p):
    cap_at = ev_files[fid]['captured_at']
    with open(p) as f:
        d = json.load(f)
    for r in d.get('records', []):
        rid = r['resource_id']
        uid = resolve_uid(email=r.get('customer_email'), user_id=r.get('customer_reference'))
        if r.get('enabled'):
            add_fact(fid, cap_at, 'integration_service', rid, uid, 'ACTIVE', 'REPORT_ACTIVE_DATA_FLOW')
        else:
            add_fact(fid, cap_at, 'integration_service', rid, uid, 'DISABLED', 'VERIFY_DATA_FLOW_DISABLED')

# 7. security_audit_ledger_20261001.json
p = f'{repo}/dataset/evidence/records/security_audit_ledger_20261001.json'
fid = path_to_ev.get('evidence/records/security_audit_ledger_20261001.json')
if fid and os.path.exists(p):
    cap_at = ev_files[fid]['captured_at']
    with open(p) as f:
        d = json.load(f)
    for r in d.get('records', []):
        rid = r['resource_id']
        uid = resolve_uid(user_id=r.get('subject_reference'))
        add_fact(fid, cap_at, 'security_service', rid, uid, 'PRESENT', 'VERIFY_RECORD_PRESENT')

# 8. SQL databases
for p in sorted(glob.glob(f'{repo}/dataset/evidence/databases/*.sql')):
    rel_p = 'evidence/databases/' + os.path.basename(p)
    fid = path_to_ev.get(rel_p)
    if not fid: continue
    cap_at = ev_files[fid]['captured_at']
    con = sqlite3.connect(':memory:')
    con.row_factory = sqlite3.Row
    with open(p) as f:
        con.executescript(f.read())
    tables = [row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    
    if 'customer_profiles' in tables:
        for r in con.execute("SELECT * FROM customer_profiles"):
            rid = r['resource_id']
            u_id = r['customer_reference'] if 'customer_reference' in r.keys() else r.get('user_id')
            em = r.get('email')
            ph = r.get('phone')
            uid = resolve_uid(email=em, phone=ph, user_id=u_id)
            add_fact(fid, cap_at, 'account_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
            
    if 'customer_search_documents' in tables:
        for r in con.execute("SELECT * FROM customer_search_documents"):
            rid = r['resource_id']
            u_id = r['customer_reference'] if 'customer_reference' in r.keys() else r.get('user_id')
            em = r.get('email')
            ph = r.get('phone')
            uid = resolve_uid(email=em, phone=ph, user_id=u_id)
            add_fact(fid, cap_at, 'search_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
            
    if 'customer_analytics_profiles' in tables:
        for r in con.execute("SELECT * FROM customer_analytics_profiles"):
            rid = r['resource_id']
            cref = r['customer_reference'] if 'customer_reference' in r.keys() else r.get('user_id')
            em = r.get('email')
            ph = r.get('phone')
            eh = r.get('email_hash')
            uid = resolve_uid(email=em, phone=ph, user_id=cref, email_hash=eh)
            has_pii = any([em, ph, cref, eh])
            if has_pii:
                add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
            else:
                add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'ANONYMIZED', 'VERIFY_RECORD_ANONYMIZED')
                
    if 'support_records' in tables:
        for r in con.execute("SELECT * FROM support_records"):
            rid = r['resource_id']
            cref = r['customer_reference'] if 'customer_reference' in r.keys() else r.get('user_id')
            em = r.get('requester_email') or r.get('email')
            ph = r.get('requester_phone') or r.get('phone')
            nm = r.get('requester_name') or r.get('full_name')
            uid = resolve_uid(email=em, phone=ph, user_id=cref)
            has_pii = any([em, nm, ph])
            if has_pii:
                add_fact(fid, cap_at, 'support_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
            else:
                add_fact(fid, cap_at, 'support_platform', rid, uid, 'REDACTED', 'VERIFY_RECORD_REDACTED')
                
    if 'customer_exports' in tables:
        for r in con.execute("SELECT * FROM customer_exports"):
            rid = r['resource_id']
            em = r.get('owner_email') or r.get('email')
            cref = r.get('customer_reference') or r.get('user_id')
            uid = resolve_uid(email=em, user_id=cref)
            add_fact(fid, cap_at, 'export_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
            
    if 'connector_subscriptions' in tables:
        for r in con.execute("SELECT * FROM connector_subscriptions"):
            rid = r['resource_id']
            em = r.get('customer_email') or r.get('email')
            cref = r.get('customer_reference') or r.get('user_id')
            en = r.get('enabled')
            uid = resolve_uid(email=em, user_id=cref)
            if en:
                add_fact(fid, cap_at, 'integration_service', rid, uid, 'ACTIVE', 'REPORT_ACTIVE_DATA_FLOW')
            else:
                add_fact(fid, cap_at, 'integration_service', rid, uid, 'DISABLED', 'VERIFY_DATA_FLOW_DISABLED')
                
    if 'backup_restore_entries' in tables:
        for r in con.execute("SELECT * FROM backup_restore_entries"):
            rid = r['resource_id']
            em = r.get('customer_email') or r.get('email')
            cref = r.get('customer_reference') or r.get('user_id')
            ra = r.get('restore_allowed')
            uid = resolve_uid(email=em, user_id=cref)
            if ra:
                add_fact(fid, cap_at, 'backup_service', rid, uid, 'ACTIVE', 'REPORT_RESTORE_RISK')
            else:
                add_fact(fid, cap_at, 'backup_service', rid, uid, 'BLOCKED', 'VERIFY_RESTORE_BLOCKED')
                
    if 'security_audit_records' in tables:
        for r in con.execute("SELECT * FROM security_audit_records"):
            rid = r['resource_id']
            sref = r.get('subject_reference') or r.get('user_id')
            uid = resolve_uid(user_id=sref)
            add_fact(fid, cap_at, 'security_service', rid, uid, 'PRESENT', 'VERIFY_RECORD_PRESENT')
            
    if 'customer_profiles_failover_replica' in tables:
        for r in con.execute("SELECT * FROM customer_profiles_failover_replica"):
            rid = r['resource_id']
            u_id = r.get('user_id') or r.get('customer_reference')
            em = r.get('email')
            ph = r.get('phone')
            uid = resolve_uid(email=em, phone=ph, user_id=u_id)
            add_fact(fid, cap_at, 'account_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')

    if 'search_documents_primary' in tables:
        for r in con.execute("SELECT * FROM search_documents_primary"):
            rid = r['resource_id']
            u_id = r.get('user_id') or r.get('customer_reference')
            em = r.get('email')
            ph = r.get('phone')
            uid = resolve_uid(email=em, phone=ph, user_id=u_id)
            add_fact(fid, cap_at, 'search_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')

    rep_tables = [t for t in tables if 'replica' in t and t != 'customer_data_primary']
    for rt in rep_tables:
        cols = [col[1] for col in con.execute(f'PRAGMA table_info({rt})')]
        if 'record_json' in cols:
            for r in con.execute(f"SELECT resource_id, origin_system, collection_name, record_json FROM {rt}"):
                rid, orig_sys, col_name, rec_json = r['resource_id'], r['origin_system'], r['collection_name'], r['record_json']
                try:
                    jd = json.loads(rec_json)
                except: jd = {}
                em = jd.get('email')
                ph = jd.get('phone')
                u_id = jd.get('user_id') or jd.get('customer_reference')
                uid = resolve_uid(email=em, phone=ph, user_id=u_id)
                in_prim = con.execute("SELECT 1 FROM customer_data_primary WHERE resource_id = ?", (rid,)).fetchone()
                
                if orig_sys == 'account_service':
                    if not in_prim or jd.get('account_status') == 'ACTIVE':
                        add_fact(fid, cap_at, 'account_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
                    else:
                        add_fact(fid, cap_at, 'account_service', rid, uid, 'ABSENT', 'VERIFY_RECORD_ABSENT')
                elif orig_sys == 'search_service':
                    add_fact(fid, cap_at, 'search_service', rid, uid, 'PRESENT', 'REPORT_REMAINING_RECORD')
                elif orig_sys == 'analytics_platform':
                    has_pii = any(jd.get(k) for k in ['email', 'phone', 'user_id', 'customer_reference', 'email_hash'])
                    if has_pii:
                        add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
                    else:
                        add_fact(fid, cap_at, 'analytics_platform', rid, uid, 'ANONYMIZED', 'VERIFY_RECORD_ANONYMIZED')
                elif orig_sys == 'support_platform':
                    has_pii = any(jd.get(k) for k in ['email', 'phone', 'requester_email'])
                    if has_pii:
                        add_fact(fid, cap_at, 'support_platform', rid, uid, 'PRESENT', 'REPORT_EXPOSED_PII', exposed_pii=True)
                    else:
                        add_fact(fid, cap_at, 'support_platform', rid, uid, 'REDACTED', 'VERIFY_RECORD_REDACTED')
                elif orig_sys == 'security_service':
                    add_fact(fid, cap_at, 'security_service', rid, uid, 'PRESENT', 'VERIFY_RECORD_PRESENT')
    con.close()

print('Facts after SQL databases:', len(facts))
