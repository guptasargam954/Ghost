import csv
from datetime import datetime

repo = 'repo/hackerrank-orchestrate-october26-main'

# Load users
with open(f'{repo}/dataset/user_identities.csv') as f:
    users = {r['user_id']: r for r in csv.DictReader(f)}
    email_to_uid = {r['email'].strip().lower(): r['user_id'] for r in users.values()}

with open(f'{repo}/dataset/user_audit_log.csv') as f:
    for r in csv.DictReader(f):
        if r['field_name'] == 'email':
            email_to_uid[r['old_value'].strip().lower()] = r['user_id']
            email_to_uid[r['new_value'].strip().lower()] = r['user_id']

with open(f'{repo}/dataset/system_activity.csv') as f:
    acts = list(csv.DictReader(f))

# Look at deletion_worker actions
del_acts = [a for a in acts if a['source_system'] == 'deletion_worker']
print(f'Total deletion_worker activities: {len(del_acts)}')

# Group into deletion runs
# Notice: what is the structure of a deletion run?
# Usually a run starts with DELETE_RECORD account_...
# followed by actions on search, support, analytics, integration, backup, etc.
runs = []
cur_run = []
for a in del_acts:
    if a['target_system'] == 'account_service' and a['event_type'] == 'DELETE_RECORD':
        if cur_run:
            runs.append(cur_run)
        cur_run = [a]
    else:
        if cur_run:
            cur_run.append(a)
        else:
            cur_run = [a]
if cur_run:
    runs.append(cur_run)

print(f'Total runs identified by starting with DELETE_RECORD account_*: {len(runs)}')
for i, r in enumerate(runs[:10]):
    t0 = r[0]['event_time']
    t1 = r[-1]['event_time']
    resources = [item['resource_id'] for item in r]
    print(f'Run {i} ({t0} to {t1}): {resources}')
