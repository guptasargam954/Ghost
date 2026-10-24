import csv
from datetime import datetime

repo = 'repo/hackerrank-orchestrate-october26-main'

with open(f'{repo}/dataset/system_activity.csv') as f:
    acts = list(csv.DictReader(f))

del_acts = [a for a in acts if a['source_system'] == 'deletion_worker']
print(f'Total deletion_worker activities: {len(del_acts)}')

# Let's inspect the time gaps between consecutive deletion_worker activities
batches = []
current_batch = []
for a in del_acts:
    t = datetime.fromisoformat(a['event_time'].replace('Z', '+00:00'))
    if not current_batch:
        current_batch.append((t, a))
    else:
        prev_t = current_batch[-1][0]
        # If within 4 hours, same batch
        if (t - prev_t).total_seconds() <= 4 * 3600:
            current_batch.append((t, a))
        else:
            batches.append(current_batch)
            current_batch = [(t, a)]
if current_batch:
    batches.append(current_batch)

print(f'Total batches clustered by <=4h gap: {len(batches)}')
for i, b in enumerate(batches[:15]):
    start = b[0][0].isoformat()
    end = b[-1][0].isoformat()
    res = [item[1]['resource_id'] for item in b]
    print(f'Batch {i}: {len(b)} items, from {start} to {end}: {res}')
