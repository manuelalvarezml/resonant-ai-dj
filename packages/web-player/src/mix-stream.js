// One continuous AAC encode: no per-song padding or decoder switching at transitions.
export const MIX_MIME='audio/mp4; codecs="mp4a.40.2"';
export function canStreamMix(){return Boolean(globalThis.MediaSource?.isTypeSupported(MIX_MIME));}
export function bufferedAhead(audio){for(let i=0;i<audio.buffered.length;i++)if(audio.currentTime>=audio.buffered.start(i)&&audio.currentTime<=audio.buffered.end(i))return audio.buffered.end(i)-audio.currentTime;return 0;}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function update(buffer,operation,signal){return new Promise((resolve,reject)=>{
 const cleanup=()=>{buffer.removeEventListener('updateend',done);buffer.removeEventListener('error',fail);signal.removeEventListener('abort',abort);};
 const done=()=>{cleanup();resolve();},fail=()=>{cleanup();reject(Error('The mix stream could not be decoded.'));},abort=()=>{cleanup();reject(new DOMException('Stopped','AbortError'));};
 buffer.addEventListener('updateend',done,{once:true});buffer.addEventListener('error',fail,{once:true});signal.addEventListener('abort',abort,{once:true});
 try{if(signal.aborted)abort();else operation();}catch(e){cleanup();reject(e);}
});}
export function streamMix(audio,url,{duration,onReady=()=>{},onError=()=>{}}={}){
 const controller=new AbortController(),signal=controller.signal,source=new MediaSource(),objectURL=URL.createObjectURL(source);
 let buffer;
 audio.src=objectURL;audio.load();
 source.addEventListener('sourceopen',async()=>{
  let reader;
  try{
   if(signal.aborted)return;
   buffer=source.addSourceBuffer(MIX_MIME);
   if(Number.isFinite(duration)){source.duration=duration;buffer.appendWindowEnd=duration;}
   const response=await fetch(url,{signal});if(!response.ok)throw Error('The mix preview is not available yet.');
   reader=response.body.getReader();let ready=false;
   while(!signal.aborted){
    // Keep client memory bounded even when the renderer is much faster than playback.
    while(bufferedAhead(audio)>60&&!signal.aborted)await sleep(100);
    if(signal.aborted)break;
    const {done,value}=await reader.read();if(done)break;
    for(let offset=0;offset<value.length&&!signal.aborted;offset+=65536){
     while(bufferedAhead(audio)>60&&!signal.aborted)await sleep(100);
     if(signal.aborted)break;
     if(audio.currentTime>40&&buffer.buffered.length&&buffer.buffered.start(0)<audio.currentTime-30)await update(buffer,()=>buffer.remove(0,audio.currentTime-30),signal);
     await update(buffer,()=>buffer.appendBuffer(value.subarray(offset,offset+65536)),signal);
     if(!ready&&buffer.buffered.length){ready=true;onReady();}
    }
   }
   if(!signal.aborted&&source.readyState==='open')source.endOfStream();
  }catch(error){if(error.name!=='AbortError'&&!signal.aborted)onError(error);}
  finally{try{await reader?.cancel();}catch{}}
 },{once:true});
 return ()=>{controller.abort();try{if(source.readyState==='open'&&buffer?.updating)buffer.abort();}catch{}audio.pause();audio.removeAttribute('src');audio.load();URL.revokeObjectURL(objectURL);};
}
