"""Bounded memory sampler for the child evaluation process; exits when evaluation exits."""
import subprocess,time,sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with (root/'runs/test_progress.log').open('x') as out:
 p=subprocess.Popen([sys.executable,str(root/'experiment.py'),'test'],cwd=root,stdout=out,stderr=subprocess.STDOUT)
 with (root/'runs/memory_samples.jsonl').open('x') as mem:
  while p.poll() is None:
   raw=subprocess.check_output(['ps','-axo','pid=,rss=,comm='],text=True)
   procs=[]
   for line in raw.splitlines():
    cols=line.strip().split(None,2)
    if len(cols)==3 and (int(cols[0])==p.pid or 'LM Studio' in cols[2] or 'llama' in cols[2].lower()):procs.append({'pid':int(cols[0]),'rss_kib':int(cols[1]),'process':cols[2]})
   mem.write(json.dumps({'time':time.time(),'processes':procs})+'\n');mem.flush();time.sleep(1)
 sys.exit(p.returncode)
