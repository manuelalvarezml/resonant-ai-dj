import {LocalLibrary} from './adapters.js';
import {fullyAnalyzed} from './release-policy.js';
import {cachedFeatures} from './features.js';
const button=document.querySelector('#prepare'),result=document.querySelector('#result');
button.onclick=async()=>{
 button.disabled=true;let copied=0;const failures=[];
 try{
  const response=await fetch('/api/local/web-library',{headers:{'X-Resonant-Local':'1'}});if(!response.ok)throw Error('Restart the local server before preparing the preview.');
  const {availableHashes}=await response.json(),available=new Set(availableHashes),library=new LocalLibrary();await library.init();
  const tracks=await library.read('tracks');
  for(const [i,t] of tracks.entries()){
   result.textContent=`Checking ${i+1}/${tracks.length}; ${copied} MP3s copied.`;
   if(!t.fileHash||available.has(t.fileHash))continue;
   try{
    const features=await cachedFeatures(t.fileHash);if(!fullyAnalyzed(features))continue;
    const audio=await library.read('audio',t.id);if(!audio||!audio.name?.toLowerCase().endsWith('.mp3'))continue;
    const r=await fetch('/api/local/web-library?hash='+t.fileHash,{method:'POST',headers:{'X-Resonant-Local':'1'},body:audio});if(!r.ok)throw Error((await r.json()).error);available.add(t.fileHash);copied++;
   }catch(e){failures.push(t.title+': '+e.message);}
  }
  library.db?.close();result.textContent=`Ready: ${available.size} fully analyzed MP3s. Copied ${copied} browser-only sources.\n${failures.join('\n')}`;
 }catch(e){result.textContent=e.message;}finally{button.disabled=false;}
};
