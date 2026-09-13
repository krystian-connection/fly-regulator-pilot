"""Loopback-only exploration UI; never writes locked evaluation results."""
import sys,json,threading,time,uuid
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import experiment as e
state_lock=threading.RLock();step_lock=threading.Lock();running=False;session=None;error=None;generation=0

def reset(config):
 global session,running,error,generation
 if not step_lock.acquire(blocking=False):raise ValueError('A decision is in flight. Stop, then reset when it finishes.')
 try:
  with state_lock:
   running=False;error=None;generation+=1
   task=config.get('task','resources');condition=config.get('condition','fly');seed=int(config.get('seed',42));interface_seed=int(config.get('interface_seed',11))
   if condition not in e.CONDITIONS or interface_seed not in e.SEEDS:raise ValueError('Unknown condition or interface seed')
   overrides=config.get('overrides',{})
   for k,v in overrides.items():
    if k not in ['reliability_a','reliability_b','recharge']:raise ValueError('Unknown scenario control')
    if not isinstance(v,(float,int)) or not 0<=v<=(6 if k=='recharge' else 1):raise ValueError('Control out of range')
   session={'id':str(uuid.uuid4()),'config':config,'env':e.Environment(task,seed,'explore',overrides),'controller':e.controller(condition,interface_seed),'steps':[]}
 finally:step_lock.release()

def snapshot():
 with state_lock:
  if not session:return {'running':False,'error':error}
  env=session['env'];return {'id':session['id'],'config':session['config'],'running':running,'busy':step_lock.locked(),'error':error,'step':env.t,'energy':env.energy,'summary':env.summary(),'steps':session['steps'],'complete':env.t==e.HORIZON}

def do_step():
 global running,error
 if not step_lock.acquire(blocking=False):return
 try:
  with state_lock:
   if not session or session['env'].t>=e.HORIZON:running=False;return
   s=session;env=s['env'];frames=env.advance();sig=s['controller'].signal(frames,env.task)
  action,call=e.llm(env,sig,'explore')
  with state_lock:
   result=env.step(action);record={'frames':frames,'signal':sig,'outcome':result,'latency_s':call['latency_s'],'usage':call['response'].get('usage',{}),'error':call['error']};s['steps'].append(record)
   e.append(e.ROOT/'runs/exploration_sessions.jsonl',{'session':s['id'],'config':s['config'],'step':record})
   if env.t>=e.HORIZON:running=False
 except Exception as ex:
  with state_lock:error=str(ex);running=False
 finally:step_lock.release()

def loop(my_generation):
 while True:
  with state_lock:
   if not running or generation!=my_generation:return
  do_step();time.sleep(.05)

class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,obj,status=200):
  b=json.dumps(obj,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def local(self):
  if self.headers.get('Host') not in ['127.0.0.1:8765','localhost:8765']:raise ValueError('Loopback Host required')
  origin=self.headers.get('Origin')
  if origin and origin not in ['http://127.0.0.1:8765','http://localhost:8765']:raise ValueError('Same-origin request required')
 def do_GET(self):
  try:
   self.local()
   if self.path=='/api/state':return self.send(snapshot())
   if self.path=='/api/results':
    p=e.ROOT/'runs/test_episodes.jsonl';rows=[json.loads(l) for l in p.read_text().splitlines()] if p.exists() else []
    return self.send({'locked':True,'episodes':rows})
   if self.path in ['/','/app.js','/style.css']:
    name={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[self.path];b=(Path(__file__).parent/name).read_bytes();self.send_response(200);self.send_header('Content-Type',{'html':'text/html','js':'text/javascript','css':'text/css'}[name.split('.')[-1]]);self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
   self.send({'error':'Not found'},404)
  except Exception as ex:self.send({'error':str(ex)},400)
 def do_POST(self):
  global running
  try:
   self.local()
   if self.headers.get('Content-Type')!='application/json':raise ValueError('JSON required')
   length=int(self.headers.get('Content-Length',0))
   if length>4096:raise ValueError('Request too large')
   config=json.loads(self.rfile.read(length) or b'{}')
   if self.path=='/api/reset':reset(config)
   elif self.path=='/api/stop':
    with state_lock:running=False
   elif self.path=='/api/step':
    with state_lock:
     if running:raise ValueError('Stop automatic run before stepping')
    threading.Thread(target=do_step,daemon=True).start()
   elif self.path=='/api/run':
    with state_lock:
     if not running:running=True;threading.Thread(target=loop,args=(generation,),daemon=True).start()
   else:return self.send({'error':'Not found'},404)
   self.send(snapshot())
  except Exception as ex:self.send({'error':str(ex)},400)

if __name__=='__main__':
 reset({'task':'resources','condition':'fly','seed':42,'interface_seed':11})
 print('Fly regulator lab: http://127.0.0.1:8765 — Ctrl+C stops the UI. No daemon installed.',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
