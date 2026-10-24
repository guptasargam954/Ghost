import csv
from datetime import datetime, timezone

repo = 'repo/hackerrank-orchestrate-october26-main'

with open(f'{repo}/dataset/system_activity.csv') as f:
    acts = list(csv.DictReader(f))

del_acts = [a for a in acts if a['source_system'] == 'deletion_worker']

# Parse times
for a in del_acts:
    a['dt'] = datetime.fromisoformat(a['event_time'].replace('Z', '+00:00'))

# Group del_acts by clustering (items within 2 hours of each other)
batches = []
cur_batch = []
for a in del_acts:
    if not cur_batch:
        cur_batch.append(a)
    else:
        if (a['dt'] - cur_batch[-1]['dt']).total_seconds() <= 2 * 3600:
            cur_batch.append(a)
        else:
            batches.append(cur_batch)
            cur_batch = [a]
if cur_batch:
    batches.append(cur_batch)

print(f'Total deletion batches: {len(batches)}')

# Test on sample requests
with open(f'{repo}/dataset/sample_deletion_requests.csv') as f:
    s_reqs = list(csv.DictReader(f))

# Match each sample request to its batch
matched = 0
for req in s_reqs:
    rep_dt = datetime.fromisoformat(req['reported_at'].replace('Z', '+00:00'))
    # Find batch closest to reported_at
    best_b = None
    min_dist = float('inf')
    for b in batches:
        # Distance to batch time range
        b_start = b[0]['dt']
        b_end = b[-1]['dt']
        dist = min(abs((rep_dt - b_start).total_seconds()), abs((rep_dt - b_end).total_seconds()))
        if dist < min_dist:
            min_dist = dist
            best_b = b
    if min_dist <= 3 * 3600:
        matched += 1
    else:
        print(f"Unmatched: {req['case_id']} rep_at={req['reported_at']} min_dist={min_dist/3600:.1f}h")

print(f'Sample requests matched to batch within 3 hours: {matched} / {len(s_reqs)}')
