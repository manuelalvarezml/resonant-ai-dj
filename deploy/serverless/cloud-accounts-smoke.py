#!/usr/bin/env python3
"""Production account isolation/range checks. No model invocation. Temporary state is reset separately."""
import http.cookiejar,json,time,urllib.request,urllib.error,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ORIGIN='https://resonant.lat'
def client(name):
 credentials=json.loads((ROOT/f'output/accounts/{name}.json').read_text());opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));auth={}
 def request(path,body=None,headers=None,expect=200,raw=False):
  h={'Origin':ORIGIN,'Content-Type':'application/json',**({'X-Resonant-CSRF':auth['csrf'],'X-Resonant-User':auth['user']['id']} if auth else {}),**(headers or {})}
  try:
   with opener.open(urllib.request.Request(ORIGIN+path,headers=h,data=None if body is None else json.dumps(body).encode()),timeout=30) as r:status=r.status;data=r.read();rh=dict(r.headers)
  except urllib.error.HTTPError as e:status=e.code;data=e.read();rh=dict(e.headers)
  assert status==expect,(path,status,data[:200] if status!=expect else '')
  return (data,rh) if raw else json.loads(data)
 auth.update(request('/api/session/login',{'identifier':credentials['username'],'password':credentials['password']}));assert auth['user']['id']==credentials['id'];return request,auth
one,a=client('manuel');two,b=client('tester');assert a['user']['role']=='owner' and b['user']['role']=='listener'
for c in [one,two]:
 assert c('/api/profile')['items']==[];assert c('/api/profile?kind=prompt')['items']==[]
manifest=one('/library/current.json');page=one(manifest['pages'][0]);track=page['tracks'][0]
base={'id':str(uuid.uuid4()),'at':int(time.time()*1000),'type':'playlist','playlistId':'account-smoke','action':'create','name':'Owner private fixture','trackIds':[track['id']]}
assert one('/api/profile',{'operations':[base]})['saved']==[base['id']]
assert two('/api/profile')['items']==[]
base2={**base,'name':'Tester private fixture'};assert two('/api/profile',{'operations':[base2]})['saved']==[base['id']]
assert one('/api/profile')['items'][0]['name']=='Owner private fixture';assert two('/api/profile')['items'][0]['name']=='Tester private fixture'
# Same account, new session can see its own saves using email login.
three,c=client('tester');assert three('/api/profile')['items'][0]['name']=='Tester private fixture'
two('/api/admin/analytics',expect=403)
two('/api/profile',headers={'X-Resonant-User':a['user']['id']},expect=401)
two('/api/profile',{'operations':[base]},headers={'X-Resonant-CSRF':'invalid'},expect=403)
event={'id':str(uuid.uuid4()),'at':int(time.time()*1000),'type':'click','view':'library','action':'play-track'}
two('/api/events',{'events':[event]});summary=one('/api/admin/analytics');assert next(u for u in summary['users'] if u['id']==b['user']['id'])['events']==1
assert 'Owner private fixture' not in json.dumps(summary)
audio,headers=two('/media/'+track['fileHash']+'.mp3',headers={'Range':'bytes=0-1023'},expect=206,raw=True);assert len(audio)==1024
spectrum=two('/library/spectra/v1/'+track['fileHash']+'.json');assert spectrum['schema']=='resonant-spectrum/1'
for c in [one,two,three]:c('/api/session/logout',{})
two('/api/profile',expect=401)
receipt={'origin':ORIGIN,'freshProfiles':True,'crossAccountIsolation':True,'crossSessionPersistence':True,'ownerOnlyAnalytics':True,'csrfAndAccountBinding':True,'events':True,'privateAudioRange':len(audio),'nativeSpectrum':True,'logout':True,'openaiCalls':0,'testedAt':int(time.time())}
(ROOT/'output/accounts/cloud-smoke.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
