import os, csv, json, re, glob, sqlite3, base64, zlib
from collections import defaultdict
from datetime import datetime

repo = 'repo/hackerrank-orchestrate-october26-main'

# Load user identities
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

# Evidence files manifest
with open(f'{repo}/dataset/evidence_files.csv') as f:
    ev_files = {r['file_id']: r for r in csv.DictReader(f)}

with open(f'{repo}/dataset/sample_deletion_requests.csv') as f:
    s_reqs = list(csv.DictReader(f))

with open(f'{repo}/dataset/sample_output.csv') as f:
    s_outs = {r['case_id']: r for r in csv.DictReader(f)}

print(f'Sample requests: {len(s_reqs)}')
