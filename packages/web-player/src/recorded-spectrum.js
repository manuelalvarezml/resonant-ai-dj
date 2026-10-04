import {serverlessTransport} from './serverless.js';
export function decodeSpectrum(value){
 if(value?.schema!=='resonant-spectrum/1'||value.columns!==96||value.fps!==10||!Number.isInteger(value.frames)||value.frames<1||value.frames>216000||typeof value.data!=='string'||value.data.length>28000000)throw Error('Invalid display spectrum');
 const bytes=Uint8Array.from(atob(value.data),c=>c.charCodeAt(0));if(bytes.length!==value.frames*96)throw Error('Incomplete display spectrum');
 return {...value,bytes};
}
export function spectrumAt(data,time){
 if(!data||!Number.isFinite(time))return null;
 const position=Math.max(0,Math.min(data.frames-1,time*data.fps-1)),a=Math.floor(position),b=Math.min(data.frames-1,a+1),mix=position-a,row=new Float32Array(96);
 for(let i=0;i<96;i++)row[i]=(data.bytes[a*96+i]*(1-mix)+data.bytes[b*96+i]*mix)/255;
 return row;
}
export function recordedSpectrum(audio){
 let data=null,request=null,url='';const cache=new Map();
 async function load(){
  const source=audio.currentSrc||audio.src;if(!source||source===url)return;url=source;request?.abort();request=new AbortController();data=null;
  const path=new URL(source,location.href).pathname,id=path.match(/(?:audio\/|media\/)([a-f0-9]{64})(?:\.mp3)?$/)?.[1]??(/mix/.test(path)?'mix-house-example':null);
  if(!id)return;if(cache.has(id)){data=cache.get(id);return;}
  const signal=request.signal;
  try{const response=await fetch(serverlessTransport()?`/library/spectra/v1/${id}.json`:`/api/web/spectrum/${id}`,{signal,credentials:'same-origin'});if(!response.ok)throw Error('Spectrum unavailable');const value=decodeSpectrum(await response.json());if(signal.aborted)return;data=value;cache.set(id,value);if(cache.size>3)cache.delete(cache.keys().next().value);}catch(error){if(error.name!=='AbortError')console.warn('Display spectrum unavailable; native playback continues.');}
 }
 audio.addEventListener('loadstart',()=>void load());audio.addEventListener('loadedmetadata',()=>void load());
 return time=>spectrumAt(data,time);
}
