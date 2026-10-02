import {isStorageFailure} from './analysis-queue.js';
import {fileHash} from './adapters.js';
import {cachedFeatures} from './features.js';

export async function recoverAnalyzedTracks(library,onProgress=()=>{},request=fetch){
 const get=async path=>{const response=await request(path,{cache:'no-store',headers:{'X-Resonant-Local':'1'}});if(!response.ok)throw Error('Saved batch recovery is unavailable. Restart the local player service and retry.');return response;};
 const {tracks}=await (await get('/api/local/recovery')).json();
 if(!Array.isArray(tracks)||tracks.length>500)throw Error('Invalid recovery list.');
 const existing=new Set((await library.duplicateIndex()).map(t=>t.hash));
 let added=0,omitted=0;const errors=[];
 for(const [i,entry] of tracks.entries()){
  onProgress(`Restoring ${i+1}/${tracks.length}: ${entry.filename}`);
  try{
   if(!/^[a-f0-9]{64}$/.test(entry.sha256)||typeof entry.filename!=='string')throw Error('Invalid recovery entry.');
   if(existing.has(entry.sha256)){omitted++;continue;}
   const blob=await (await get('/api/local/recovery/audio/'+entry.sha256)).blob();
   const file=new File([blob],entry.filename);
   if(await fileHash(file)!==entry.sha256)throw Error('Audio hash does not match the saved analysis.');
   const features=entry.hasAnalysis===false?null:await cachedFeatures(entry.sha256,request);
   const track=await library.importFile(file,{hash:entry.sha256});
   existing.add(entry.sha256);added++;
   if(features)await library.saveFeatures(track.id,features);
  }catch(error){errors.push(`${entry.filename}: ${error.message}`);if(isStorageFailure(error))break;}
 }
 const restored=await library.restoreCachedFeatures(hash=>cachedFeatures(hash,request));
 return {added,omitted,restored,errors};
}
