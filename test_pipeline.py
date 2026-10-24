import os, csv, json, re, glob, sqlite3, base64, zlib
from collections import defaultdict

repo = 'repo/hackerrank-orchestrate-october26-main'

# Load user identities and audit log
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
for uid, u in users.items():
    user_idents[uid] = {
        'uid': uid,
        'emails': {u['email'].strip().lower()},
        'phones': {u['phone'].strip()},
        'names': {u['name'].strip()},
        'hashes': {u['email_hash'].strip().lower()}
    }

for r in audit_rows:
    uid = r['user_id']
    if uid in user_idents:
        fn = r['field_name']
        if fn == 'email':
            user_idents[uid]['emails'].add(r['old_value'].strip().lower())
            user_idents[uid]['emails'].add(r['new_value'].strip().lower())
        elif fn == 'phone':
            user_idents[uid]['phones'].add(r['old_value'].strip())
            user_idents[uid]['phones'].add(r['new_value'].strip())
        elif fn == 'name':
            user_idents[uid]['names'].add(r['old_value'].strip())
            user_idents[uid]['names'].add(r['new_value'].strip())

# Evidence manifest
with open(f'{repo}/dataset/evidence_files.csv') as f:
    ev_files = {r['file_id']: r for r in csv.DictReader(f)}
    path_to_ev = {r['file_path']: r['file_id'] for r in ev_files.values()}

# System activity
with open(f'{repo}/dataset/system_activity.csv') as f:
    acts = list(csv.DictReader(f))

# Let's see: LINK_RESOURCE_IDENTITY in system_activity
# activity_4000: Data catalog linked account_5762 (account_5762) to haruka.s1838@zoho.com and user_11.
user_linked_resources = defaultdict(list)
for a in acts:
    if a['event_type'] == 'LINK_RESOURCE_IDENTITY':
        m = re.search(r'to (.*?) and (user_\d+)', a['details'])
        if m:
            em, uid = m.group(1), m.group(2)
            user_linked_resources[uid].append({
                'system_id': a['target_system'],
                'resource_id': a['resource_id'],
                'activity_id': a['activity_id'],
                'event_time': a['event_time']
            })

print('Linked resources by catalog:', len(user_linked_resources))

