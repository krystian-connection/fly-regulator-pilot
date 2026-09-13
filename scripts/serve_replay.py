"""Optional local viewing of one static replay file. No inference or general file server."""
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[1]
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.headers.get('Host') not in ['127.0.0.1:8766','localhost:8766']:
   self.send_error(400);return
  if self.path not in ['/','/replay.html']:
   self.send_error(404);return
  data=(ROOT/'replay.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(data)));self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
if __name__=='__main__':
 print('Saved replay only: http://127.0.0.1:8766 — Ctrl+C stops. No model connection.',flush=True)
 ThreadingHTTPServer(('127.0.0.1',8766),Handler).serve_forever()
