"""Main execution CLI for Ghost Data Still Exists audit solution.

Processes deletion requests, executes evidence-based policy audit,
and generates the submission deliverable output.csv.
"""

import os
import sys
import csv
import json
import re
import argparse
from typing import List

from models import Case
from identity import IdentityResolver
from evidence_reader import EvidenceReader
from classifier import RequestClassifier
from policy_engine import PolicyEngine

def extract_case_num(case_id: str) -> int:
    m = re.search(r'\d+', case_id)
    return int(m.group(0)) if m else 0

def run_audit(dataset_dir: str, input_csv: str, output_csv: str):
    print(f"Loading dataset from: {dataset_dir}")
    print(f"Processing cases from: {input_csv}")
    
    # 1. Initialize identity resolver
    id_csv = os.path.join(dataset_dir, "user_identities.csv")
    audit_log_csv = os.path.join(dataset_dir, "user_audit_log.csv")
    resolver = IdentityResolver(id_csv, audit_log_csv)
    
    # 2. Ingest evidence
    reader = EvidenceReader(dataset_dir, resolver)
    reader.parse_all()
    print(f"Loaded {len(reader.facts)} facts across {len(reader.ev_files)} evidence files.")
    
    # 3. Initialize classifier & policy engine
    classifier = RequestClassifier()
    engine = PolicyEngine(dataset_dir, resolver, reader, classifier)
    
    # 4. Load cases
    cases: List[Case] = []
    with open(input_csv, mode='r', encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            cases.append(Case(
                case_id=row['case_id'],
                email=row['email'],
                requested_at=row['requested_at'],
                reported_status=row['reported_status'],
                reported_at=row['reported_at'],
                audit_at=row['audit_at'],
                request_text=row['request_text']
            ))
            
    # Sort cases numerically by case_id
    cases.sort(key=lambda c: extract_case_num(c.case_id))
    print(f"Auditing {len(cases)} cases...")
    
    results = []
    status_counts = {}
    for c in cases:
        status, steps = engine.audit_case(c)
        status_counts[status] = status_counts.get(status, 0) + 1
        steps_dict = [s.to_dict() for s in steps]
        steps_json = json.dumps(steps_dict, separators=(',', ':'))
        results.append({
            'case_id': c.case_id,
            'deletion_status': status,
            'steps_json': steps_json
        })
        
    # Write output.csv
    os.makedirs(os.path.dirname(os.path.abspath(output_csv)), exist_ok=True)
    with open(output_csv, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['case_id', 'deletion_status', 'steps_json'])
        writer.writeheader()
        writer.writerows(results)
        
    print(f"Successfully generated {output_csv} with {len(results)} rows.")
    print("Status breakdown:", status_counts)
    
    # Also mirror to repo root and workspace root if different
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(curr_dir)
    workspace_root = os.path.dirname(repo_root)
    
    repo_out = os.path.join(repo_root, "output.csv")
    if os.path.abspath(output_csv) != os.path.abspath(repo_out):
        import shutil
        shutil.copyfile(output_csv, repo_out)
        print(f"Mirrored output to repo root: {repo_out}")

    workspace_out = os.path.join(workspace_root, "output.csv")
    if os.path.abspath(output_csv) != os.path.abspath(workspace_out):
        import shutil
        shutil.copyfile(output_csv, workspace_out)
        print(f"Mirrored output to workspace root: {workspace_out}")

def main():
    parser = argparse.ArgumentParser(description="Ghost Data Still Exists Deletion Audit CLI")
    parser.add_argument("--dataset-dir", default="dataset", help="Path to dataset directory")
    parser.add_argument("--input", default="dataset/deletion_requests.csv", help="Input deletion requests CSV")
    parser.add_argument("--output", default="output.csv", help="Target output.csv path")
    args = parser.parse_args()
    
    # If paths are relative, make them relative to repo root
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(curr_dir)
    
    d_dir = args.dataset_dir if os.path.isabs(args.dataset_dir) else os.path.join(repo_root, args.dataset_dir)
    inp = args.input if os.path.isabs(args.input) else os.path.join(repo_root, args.input)
    out = args.output if os.path.isabs(args.output) else os.path.join(repo_root, args.output)
    
    run_audit(d_dir, inp, out)

if __name__ == "__main__":
    main()
