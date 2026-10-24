import csv, json

repo = 'repo/hackerrank-orchestrate-october26-main'

with open(f'{repo}/dataset/sample_deletion_requests.csv') as f:
    s_reqs = list(csv.DictReader(f))

with open(f'{repo}/dataset/sample_output.csv') as f:
    s_outs = {r['case_id']: r for r in csv.DictReader(f)}

with open(f'{repo}/dataset/system_activity.csv') as f:
    acts = list(csv.DictReader(f))

# Let's see how account_service resource_id in sample_output matches deletion_worker activity
for req in s_reqs:
    cid = req['case_id']
    rep_at = req['reported_at']
    steps = json.loads(s_outs[cid]['steps_json'])
    acc_res = [s['resource_id'] for s in steps if s['system_id'] == 'account_service']
    if not acc_res:
        print(f'{cid}: No account_service resource')
        continue
    expected_acc = acc_res[0]
    
    # Check deletion_worker activity for account_service
    # Find activities near rep_at
    matching_acts = [a for a in acts if a['resource_id'] == expected_acc and a['source_system'] == 'deletion_worker']
    act_times = [a['event_time'] for a in matching_acts]
    print(f'{cid}: rep_at={rep_at} expected={expected_acc} matched_acts={act_times}')
