"""Re-run original saved-log analysis in a temporary copy; no original outputs altered."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,os,math
ROOT=Path(__file__).resolve().parents[1]
def equal(a,b,path='root'):
 if isinstance(a,dict):
  assert a.keys()==b.keys(),path
  for k in a:equal(a[k],b[k],path+'.'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):equal(x,y,path+f'[{i}]')
 elif isinstance(a,(float,int)) and not isinstance(a,bool):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(path,a,b)
 else:assert a==b,(path,a,b)
# Block Python audit events for network connections before importing original analysis code.
block="import sys,runpy\ndef deny(event,args):\n if event.startswith('socket.'): raise RuntimeError('Offline analysis: sockets disabled')\nsys.addaudithook(deny)\nsys.argv=sys.argv[1:]\nrunpy.run_path(sys.argv[0],run_name='__main__')\n"
with tempfile.TemporaryDirectory(prefix='fly-saved-analysis-') as td:
 root=Path(td)/'candidate';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('__pycache__','.venv'))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for name,args in [('audit_harness',['test']),('analyze',[]),('export_tables',[])]:
  subprocess.run([sys.executable,'-B','-c',block,str(root/f'scripts/{name}.py'),*args],cwd=root,env=env,check=True,capture_output=True,text=True)
 equal(json.loads((ROOT/'runs/analysis.json').read_text()),json.loads((root/'runs/analysis.json').read_text()))
 for name in ['condition_summary.csv','episode_summary.csv','paired_intervals.csv']:
  assert (ROOT/'runs'/name).read_bytes()==(root/'runs'/name).read_bytes(),name
 print(json.dumps({'status':'passed','analysis_json_numerically_equal':True,'csvs_byte_identical':3,'original_scoring_audit':'passed','network_connections':'disabled by Python audit hook','new_llm_calls':0,'output_policy':'temporary copy removed; candidate unchanged'},indent=2))
