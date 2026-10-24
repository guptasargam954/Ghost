import os, csv, json

repo = 'repo/hackerrank-orchestrate-october26-main'
with open(f'{repo}/dataset/sample_output.csv') as f:
    s_outs = list(csv.DictReader(f))
with open(f'{repo}/dataset/evidence_files.csv') as f:
    ev_files = {r['file_id']: r for r in csv.DictReader(f)}

for o in s_outs:
    cid = o['case_id']
    status = o['deletion_status']
    steps = json.loads(o['steps_json'])
    ev_steps = [(s['resource_id'], s['system_id'], s['operation'], s['evidence_id']) for s in steps if s['evidence_id']]
    print(f'=== {cid} === ({status})')
    for res, sys, op, evid in ev_steps:
        ef = ev_files.get(evid)
        fpath = f'{repo}/dataset/{ef["file_path"]}' if ef else None
        matched_snippet = 'NOT FOUND'
        if fpath and os.path.exists(fpath):
            with open(fpath, 'r', errors='ignore') as fp:
                content = fp.read()
                for line in content.splitlines():
                    if res in line:
                        matched_snippet = line.strip()[:100]
                        break
        efpath = ef["file_path"] if ef else "?"
        print(f'  {res} ({sys}, {op}) in {evid} ({efpath}): {matched_snippet}')
