"""Export parallel episode-level tables and intervals for reuse without parsing JSON logs."""
from pathlib import Path
import csv,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
r=json.loads((e.ROOT/'runs/analysis.json').read_text())
for name,rows in [('condition_summary',r['summary']),('paired_intervals',r['paired_contrasts'])]:
 with (e.ROOT/f'runs/{name}.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
episodes=[json.loads(l) for l in (e.ROOT/'runs/test_episodes.jsonl').read_text().splitlines()]
rows=[{'task':x['task'],'env_seed':x['env_seed'],'interface_seed':x['interface_seed'],'condition':x['condition'],**x['summary'],'actions':''.join(s['outcome']['action'] for s in x['steps'])} for x in episodes]
with (e.ROOT/'runs/episode_summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
