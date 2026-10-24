import csv, json

repo = 'repo/hackerrank-orchestrate-october26-main'

# 1. Load users
with open(f'{repo}/dataset/user_identities.csv') as f:
    users = {r['user_id']: r for r in csv.DictReader(f)}
    email_to_uid = {r['email'].strip().lower(): r['user_id'] for r in users.values()}

with open(f'{repo}/dataset/user_audit_log.csv') as f:
    for r in csv.DictReader(f):
        if r['field_name'] == 'email':
            email_to_uid[r['old_value'].strip().lower()] = r['user_id']
            email_to_uid[r['new_value'].strip().lower()] = r['user_id']

# 2. Load system activity runs
with open(f'{repo}/dataset/system_activity.csv') as f:
    acts = list(csv.DictReader(f))

del_acts = [a for a in acts if a['source_system'] == 'deletion_worker']
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

# Sample requests & outputs
with open(f'{repo}/dataset/sample_deletion_requests.csv') as f:
    s_reqs = list(csv.DictReader(f))
with open(f'{repo}/dataset/sample_output.csv') as f:
    s_outs = {r['case_id']: r for r in csv.DictReader(f)}

# For each sample request, let's find the matching run!
for req in s_reqs:
    cid = req['case_id']
    rep_at = req['reported_at']
    steps = json.loads(s_outs[cid]['steps_json'])
    expected_res = set(s['resource_id'] for s in steps)
    
    # Find runs near rep_at (e.g. within 3 hours)
    matched_run = None
    for r in runs:
        # Check if any resource in r is in expected_res
        r_res = set(item['resource_id'] for item in r)
        if r_res & expected_res:
            matched_run = r
            break
    if matched_run:
        r_res = [item['resource_id'] for item in matched_run]
        print(f'{cid} (rep={rep_at}): matched run {r_res} | expected={expected_res}')
    else:
        print(f'{cid} (rep={rep_at}): NO RUN MATCHED | expected={expected_res}')
