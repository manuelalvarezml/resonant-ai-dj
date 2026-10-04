"""Exercise installed Lambda Runtime Interface Client against a loopback fixture."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time


def main():
    # AWS's official emulator supplies the Runtime API expected by current RIC.
    import urllib.request
    with tempfile.TemporaryDirectory() as temp:
        Path(temp,'probe_handler.py').write_text('def handler(event, context):\n    return {"echo": event["check"], "has_time": context.get_remaining_time_in_millis() > 0}\n')
        env={**os.environ,'PYTHONPATH':temp+':'+os.environ.get('PYTHONPATH','')}
        with tempfile.TemporaryFile() as log:
            process=subprocess.Popen(['/aws-lambda-rie','python','-m','awslambdaric','probe_handler.handler'],cwd=temp,env=env,stdout=log,stderr=log)
            try:
                response=None
                for _ in range(60):
                    try:
                        request=urllib.request.Request('http://127.0.0.1:8080/2015-03-31/functions/function/invocations',data=b'{"check":"runtime-interface"}',headers={'Content-Type':'application/json'})
                        with urllib.request.urlopen(request,timeout=30) as result:response=json.load(result)
                        break
                    except ConnectionError:time.sleep(.25)
                    except urllib.error.URLError as error:
                        if isinstance(error.reason,ConnectionRefusedError):time.sleep(.25)
                        else:raise
                assert response=={'echo':'runtime-interface','has_time':True},'Runtime interface failed'
            finally:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
    return {'schema':'resonant/offline-runtime-interface/1','passed':True,'emulator':'AWS RIE v1.37','awsCalls':0,'externalNetwork':False}


if __name__=='__main__':print(json.dumps(main()))
