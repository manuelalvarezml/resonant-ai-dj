#!/usr/bin/env python3
"""Real hosted login/CSRF/logout checks, with private cookie storage and no AI work."""
import http.cookiejar,json,os,urllib.error,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
 os.umask(0o077)
 def outputs(name):return {r['OutputKey']:r['OutputValue'] for r in json.loads((ROOT/f'output/serverless-cloud/{name}/outputs.json').read_text())['Stacks'][0]['Outputs']}
 f,e=outputs('resonant-data'),outputs('resonant-edge');origin='https://'+e['Domain']
 folder=ROOT/'output/serverless-cloud/acceptance';folder.mkdir(mode=0o700,exist_ok=True)
 jar=http.cookiejar.MozillaCookieJar(str(folder/'listener.cookies'));opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar));checks=[]
 def request(path,body=None,headers=None,url=None):
  h={'Origin':origin,'Content-Type':'application/json',**(headers or {})}
  try:r=opener.open(urllib.request.Request(url or origin+path,data=None if body is None else json.dumps(body).encode(),headers=h),timeout=30)
  except urllib.error.HTTPError as error:r=error
  with r:
   data=r.read(65536)
   try:payload=json.loads(data)
   except ValueError:payload={}
   return r.code,payload
 assert request('/api/session')[0]==401;checks.append('unsigned API session denied')
 assert request('/api/session/login',{'password':'wrong-fixture-password'})[0]==401;checks.append('wrong password denied')
 password=(ROOT/'output/cloud-config/first-release/listener-password.txt').read_text().strip()
 status,session=request('/api/session/login',{'password':password});assert status==200,(status,session);csrf=session['csrf'];checks.append('real shared-password login succeeds')
 assert len(list(jar))==4 and all(c.secure for c in jar);checks.append('four Secure cookies issued')
 assert request('/api/session')[0]==200;checks.append('session validates through CloudFront')
 assert request('/api/session/refresh',{},headers={'x-resonant-csrf':'wrong'})[0]==403;checks.append('CSRF enforced by deployed API')
 assert request('/api/session/refresh',{},headers={'x-resonant-csrf':csrf,'Origin':'https://foreign.invalid'})[0]==403;checks.append('foreign POST origin denied')
 assert request('/api/session/refresh',{},headers={'x-resonant-csrf':csrf})[0]==200;checks.append('cookie refresh succeeds')
 assert request('/api/session',url='https://'+f['HttpApi']+'.execute-api.us-east-2.amazonaws.com/api/session')[0]==403;checks.append('direct API endpoint denied')
 member=json.loads((ROOT/'output/serverless-assets/candidate-1/api/membership.json').read_text())
 status,reply=request('/api/playlist',{'releaseId':member['releaseId'],'idempotencyKey':str(uuid.uuid4()),'prompt':'Disabled admission fixture','tracks':[member['tracks'][0]]},headers={'x-resonant-csrf':csrf});assert status==503 and 'playback' in reply['error'];checks.append('disabled AI admission leaves session usable')
 assert request('/api/session/logout',{},headers={'x-resonant-csrf':csrf})[0]==200
 assert request('/api/session')[0]==401;checks.append('logout invalidates API session')
 status,session=request('/api/session/login',{'password':password});assert status==200
 jar.save(ignore_discard=True,ignore_expires=True);Path(jar.filename).chmod(0o600)
 file=folder/'login-session.json';file.write_text(json.dumps({'origin':origin,'csrf':session['csrf'],'expiresAt':session['expiresAt']}));file.chmod(0o600)
 result={'status':'passed','checks':checks,'openaiCalls':0,'cookieFilePrivate':True};file=folder/'login-smoke.json';file.write_text(json.dumps(result,indent=2));file.chmod(0o600);print(json.dumps(result))
if __name__=='__main__':main()
