import {mkdtemp,writeFile,readFile,rm,stat} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {allowedLocalRequest,isAnalysisRunning} from './local-features.mjs';
let converting=false;
export const isConverting=()=>converting;
const limit=512*1024*1024;
export async function convertM4a(bytes,{signal}={}){
 if(!bytes.length||bytes.length>limit)throw Error('Audio must be between 1 byte and 512 MB.');
 const dir=await mkdtemp(path.join(tmpdir(),'resonant-mp3-'));
 try{
  const input=path.join(dir,'source.m4a'),output=path.join(dir,'converted.mp3');await writeFile(input,bytes);
  await new Promise((resolve,reject)=>{
   const child=spawn('ffmpeg',['-nostdin','-hide_banner','-loglevel','error','-y','-i',input,'-map','0:a:0','-vn','-map_metadata','0','-c:a','libmp3lame','-q:a','2','-threads','1','-id3v2_version','3',output],{stdio:['ignore','ignore','pipe']});
   let error='',reason;child.stderr.on('data',b=>{error=(error+b.toString()).slice(-2000)});
   const abort=()=>{reason='Conversion cancelled.';child.kill('SIGKILL');};
   const timer=setTimeout(()=>{reason='Conversion timed out; original audio was kept.';child.kill('SIGKILL');},300000);
   signal?.addEventListener('abort',abort,{once:true});if(signal?.aborted)abort();
   const cleanup=()=>{clearTimeout(timer);signal?.removeEventListener('abort',abort);};
   child.on('error',()=>{cleanup();reject(Error('FFmpeg is unavailable. Restart the local player with FFmpeg installed.'));});
   child.on('close',code=>{cleanup();code===0?resolve():reject(Error(reason||'M4A conversion failed: '+error.replaceAll(dir,'[temporary audio]').slice(-600)));});
  });
  const info=await stat(output);if(!info.size||info.size>limit)throw Error('Converted audio exceeds the supported size.');
  return await readFile(output);
 }finally{await rm(dir,{recursive:true,force:true});}
}
export async function localConversion(req,res,port){
 const url=new URL(req.url,'http://localhost');if(url.pathname!=='/api/local/convert-m4a')return false;
 const send=(status,error)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify({error}));};
 if(req.method!=='POST'||!allowedLocalRequest(req,port)){send(403,'Use the local player to convert audio.');return true;}
 if(!/\.m4a$/i.test(url.searchParams.get('filename')??'')){send(400,'Only M4A conversion is supported.');return true;}
 if(converting||isAnalysisRunning()){send(409,'Another analysis or conversion is running. Wait for it to finish.');return true;}
 converting=true;const controller=new AbortController();const disconnected=()=>{if(!res.writableEnded)controller.abort();};res.on('close',disconnected);
 try{
  const chunks=[];let size=0;for await(const chunk of req){size+=chunk.length;if(size>limit)throw Error('Audio exceeds 512 MB.');chunks.push(chunk);}
  const output=await convertM4a(Buffer.concat(chunks),{signal:controller.signal});
  if(!res.destroyed){res.writeHead(200,{'Content-Type':'audio/mpeg','Content-Length':output.length});res.end(output);}
 }catch(error){if(!res.destroyed)send(400,error.message);}
 finally{converting=false;res.removeListener('close',disconnected);}
 return true;
}
