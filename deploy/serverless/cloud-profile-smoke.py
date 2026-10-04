#!/usr/bin/env python3
"""Verify shared saved state using a uniquely named temporary playlist; no AI call."""
import socket
import argparse,http.cookiejar,json,time,urllib.request,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--origin',required=True,choices=['https://dl3pumk9rpbun.cloudfront.net','https://resonant.lat']);p.add_argument("--connect-via-cloudfront",action="store_true");a=p.parse_args()
if a.connect_via_cloudfront:
 assert a.origin=="https://resonant.lat"
 resolve=socket.getaddrinfo
 socket.getaddrinfo=lambda host,*args,**kw:resolve("dl3pumk9rpbun.cloudfront.net" if host=="resonant.lat" else host,*args,**kw)
password=(ROOT/'output/cloud-config/first-release/listener-password.txt').read_text().strip()
def session():
 opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def request(path,body=None,csrf=None):
  headers={'Origin':a.origin,'Content-Type':'application/json'}
  if csrf:headers['x-resonant-csrf']=csrf
  with opener.open(urllib.request.Request(a.origin+path,headers=headers,data=None if body is None else json.dumps(body).encode()),timeout=30) as response:return json.load(response)
 auth=request('/api/session/login',{'password':password});return request,auth['csrf']
one,csrf=session();two=None;playlist=str(uuid.uuid4());created=False
try:
 op={'id':str(uuid.uuid4()),'at':int(time.time()*1000),'type':'playlist','playlistId':playlist,'action':'create','name':'Deployment verification','trackIds':[]};body={'operations':[op]}
 result=one('/api/profile',body,csrf);assert op['id'] in result['saved'];created=True
 assert one('/api/profile',body,csrf)==result
 two,csrf2=session();rows=two('/api/profile')['items'];assert any(r.get('id')==playlist and r['name']=='Deployment verification' for r in rows)
finally:
 if created:
  one('/api/profile',{'operations':[{'id':str(uuid.uuid4()),'at':int(time.time()*1000),'type':'playlist','playlistId':playlist,'action':'delete'}]},csrf)
 if two:two('/api/session/logout',{},csrf2)
 one('/api/session/logout',{},csrf)
print(json.dumps({'origin':a.origin,'transport':'CloudFront DNS override; custom-host TLS verified' if a.connect_via_cloudfront else 'public DNS','sharedPlaylistPersistence':'passed','retryIdempotency':'passed','temporaryPlaylistRemoved':created,'openaiCalls':0}))
