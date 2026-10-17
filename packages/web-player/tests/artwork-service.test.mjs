import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import {mkdtemp,rm,readFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createArtworkService} from '../scripts/artwork-service.mjs';

const project=fileURLToPath(new URL('../../..',import.meta.url));
test('stored event returns before artwork completes; scope, origin and image paths stay bounded',async()=>{
 const temp=await mkdtemp(path.join(tmpdir(),'resonant-artwork-test-'));
 const python=path.join(project,'tools/artwork/.venv/bin/python');
 const script=`import sys,wave,io
from pathlib import Path
from PIL import Image
from mutagen.wave import WAVE
from mutagen.id3 import APIC,TPE1,TALB
p=Path(sys.argv[1])/'fixture.wav'
with wave.open(str(p),'wb') as w:
 w.setparams((1,2,8000,0,'NONE',''));w.writeframes(b'\\0\\0'*800)
b=io.BytesIO();Image.new('RGB',(600,600),'blue').save(b,'PNG')
a=WAVE(p);a.add_tags();a.tags.add(APIC(mime='image/png',type=3,data=b.getvalue()));a.tags.add(TPE1(text=['Fixture artist']));a.tags.add(TALB(text=['Fixture album']));a.save()`;
 const fixture=spawnSync(python,['-c',script,temp],{encoding:'utf8'});assert.equal(fixture.status,0,fixture.stderr);
 const service=createArtworkService({cache:path.join(temp,'cache'),python});
 let port;const server=http.createServer(async(req,res)=>{if(!await service(req,res,port)){res.writeHead(404);res.end();}});
 try{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));port=server.address().port;const base=`http://127.0.0.1:${port}`;
  const body=await readFile(path.join(temp,'fixture.wav'));
  assert.equal((await fetch(base+'/api/artwork/stored?id=one&version=v1',{method:'POST',body})).status,403);
  const response=await fetch(base+'/api/artwork/stored?id=one&version=v1',{method:'POST',body,headers:{Origin:base,'X-Resonant-Local':'1'}});
  assert.equal(response.status,202);assert.deepEqual(await response.json(),{queued:true});
  let record;
  for(let n=0;n<60;n++){record=(await (await fetch(base+'/api/artwork/manifest')).json()).tracks.one;if(record?.status==='ready')break;await new Promise(r=>setTimeout(r,100));}
  assert.equal(record?.status,'ready');assert.equal(record.source_version,'v1');assert.equal(record.provider,'embedded');
  const image=await fetch(base+'/api/artwork/images/'+record.thumbnail.file);assert.equal(image.status,200);assert.equal(image.headers.get('content-type'),'image/jpeg');assert.ok((await image.arrayBuffer()).byteLength>100);
  assert.equal((await fetch(base+'/api/artwork/images/not-a-digest.jpg')).status,404);
  assert.equal((await fetch(base+'/api/artwork/manifest',{headers:{Origin:'https://unrelated.example'}})).status,403);
  const changed=await fetch(base+'/api/artwork/stored?id=one&version=v2',{method:'POST',body,headers:{Origin:base,'X-Resonant-Local':'1'}});assert.equal(changed.status,202);
 }finally{await service.close();await new Promise(resolve=>server.close(resolve));await rm(temp,{recursive:true,force:true});}
});
