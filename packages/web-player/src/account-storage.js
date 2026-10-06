// Hosted accounts never import the old shared listener's device data.
export function accountStorage(storage,userId){
 const prefix='resonant:account:v1:'+userId+':';
 return{get length(){return keys().length;},key:i=>keys()[i]??null,getItem:key=>storage.getItem(prefix+key),setItem:(key,value)=>storage.setItem(prefix+key,value),removeItem:key=>storage.removeItem(prefix+key)};
 function keys(){const result=[];for(let i=0;i<storage.length;i++){const key=storage.key(i);if(key?.startsWith(prefix))result.push(key.slice(prefix.length));}return result;}
}
export function clearHostedPrivateCaches(storage){
 for(let i=storage.length-1;i>=0;i--){const k=storage.key(i);if(k?.startsWith('resonant:account:')||k?.startsWith('resonant:owner:')||k==='resonant:playlist-review-v1'||k==='resonant-player:preferences:1:http')storage.removeItem(k);}
}
export function purgeLegacyHostedCaches(storage){
 for(let i=storage.length-1;i>=0;i--){const k=storage.key(i);if(k?.startsWith('resonant:owner:')||k==='resonant:playlist-review-v1'||k==='resonant-player:preferences:1:http')storage.removeItem(k);}
}
