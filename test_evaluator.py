import csv, json

repo = 'repo/hackerrank-orchestrate-october26-main'

with open(f'{repo}/dataset/sample_output.csv') as f:
    expected = {r['case_id']: r for r in csv.DictReader(f)}

print(f'Total sample cases to evaluate: {len(expected)}')
