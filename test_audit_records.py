import os, csv, json

repo = 'repo/hackerrank-orchestrate-october26-main'

# User mapping
with open(f'{repo}/dataset/user_identities.csv') as f:
    users = {r['user_id']: r for r in csv.DictReader(f)}
    email_to_uid = {r['email'].strip().lower(): r['user_id'] for r in users.values()}

with open(f'{repo}/dataset/user_audit_log.csv') as f:
    for r in csv.DictReader(f):
        if r['field_name'] == 'email':
            email_to_uid[r['old_value'].strip().lower()] = r['user_id']
            email_to_uid[r['new_value'].strip().lower()] = r['user_id']

with open(f'{repo}/dataset/sample_deletion_requests.csv') as f:
    s_reqs = list(csv.DictReader(f))
with open(f'{repo}/dataset/sample_output.csv') as f:
    s_outs = {r['case_id']: r for r in csv.DictReader(f)}

# Let's inspect audit records expected in sample_output
for req in s_reqs:
    cid = req['case_id']
    uid = email_to_uid[req['email'].strip().lower()]
    steps = json.loads(s_outs[cid]['steps_json'])
    audit_steps = [s for s in steps if s['system_id'] == 'security_service']
    if audit_steps:
        for s in audit_steps:
            print(f'{cid} ({uid}) expects {s["resource_id"]}')
