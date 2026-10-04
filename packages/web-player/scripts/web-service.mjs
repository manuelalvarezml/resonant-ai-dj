import {readFile} from 'node:fs/promises';
import path from 'node:path';
import {project} from './web-library.mjs';
import {serveAudio} from './mix-service.mjs';
const mixKey='12fd88424ba311ff55d3d55d85a9a169d095e61620099f4a3ac6698971350b41';
export function createWebService({manifest,sources}){
 const byId=new Map(manifest.tracks.map(t=>[t.id,t]));
 return async(req,res,port)=>{
  const u=new URL(req.url,'http://localhost'),send=(code,data)=>{res.writeHead(code,{'Content-Type':'application/json'});res.end(JSON.stringify(data));};
  if(!u.pathname.startsWith('/api/web/')&&!u.pathname.startsWith('/api/v1/'))return false;
  try{
   if(req.method==='GET'&&u.pathname==='/api/v1/tracks'){
    const cursor=Number(u.searchParams.get('cursor')||0);if(!Number.isSafeInteger(cursor)||cursor<0)throw Error('Invalid cursor');
    send(200,{contract_version:'resonant-player/library/1',revision:manifest.revision,tracks:manifest.tracks.slice(cursor,cursor+100),next_cursor:cursor+100<manifest.tracks.length?String(cursor+100):null});return true;
   }
   if(req.method==='POST'&&u.pathname==='/api/v1/playback-sessions'){
    if(req.headers.origin!==`http://${req.headers.host}`)throw Error('Use this app to play music.');
    let text='';for await(const b of req){text+=b;if(text.length>10000)throw Error('Request too large');}
    const input=JSON.parse(text),track=byId.get(input.track_id);if(!track||track.sourceVersion!==input.source_version)throw Error('Unknown track version');
    send(200,{contract_version:'resonant-player/playback-session/1',track_id:track.id,source_version:track.sourceVersion,url:`http://${req.headers.host}/api/web/audio/${track.id}`,expires_at:new Date(Date.now()+3600000).toISOString()});return true;
   }
   const spectrumId=u.pathname.match(/^\/api\/web\/spectrum\/([a-f0-9]{64}|mix-house-example)$/)?.[1];
   if(req.method==='GET'&&spectrumId&&(byId.has(spectrumId)||spectrumId==='mix-house-example')){const raw=await readFile(path.join(project,'output/display-spectra/v1',spectrumId+'.json'));res.writeHead(200,{'Content-Type':'application/json','Cache-Control':'private,max-age=86400'});res.end(raw);return true;}
   const id=u.pathname.match(/^\/api\/web\/audio\/([a-f0-9]{64})$/)?.[1];
   if(['GET','HEAD'].includes(req.method)&&id&&sources[id]){await serveAudio(req,res,sources[id],'audio/mpeg');return true;}
   if(req.method==='GET'&&u.pathname==='/api/web/mix'){
    const dir=path.join(project,'output/mix-delivery',mixKey),m=JSON.parse(await readFile(path.join(dir,'manifest.json'),'utf8')),graph=await readFile(path.join(dir,'graph.txt'),'utf8');
    const starts=[...graph.matchAll(/\[h\d_out_prefix_source\]atrim=end=([0-9.]+)/g)].map(m=>Number(m[1]));
    send(200,{title:'Three-track house mix',duration_s:m.duration_s,url:'/api/web/mix/audio',transitions:starts.map(start=>({start_s:start,end_s:start+29.09})),tracks:['My Paradise – Edit','Rock the House','Lemon8']});return true;
   }
   if(['GET','HEAD'].includes(req.method)&&u.pathname==='/api/web/mix/audio'){await serveAudio(req,res,path.join(project,'output/mix-delivery',mixKey,'stream.m4a'),'audio/mp4');return true;}
   send(404,{error:'Not available in the web edition.'});return true;
  }catch(e){if(!res.headersSent)send(400,{error:e.message});else res.destroy();return true;}
 };
}
