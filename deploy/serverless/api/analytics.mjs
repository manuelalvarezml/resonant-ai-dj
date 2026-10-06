const fail=(status,message)=>{throw Object.assign(Error(message),{status});};
export const views=new Set(['library','favorites','playlists','playlist','analysis','playlistiq','mixes','status','account']);
export async function recordEvents(db,userId,sessionId,body,now){
 if(!Array.isArray(body.events)||!body.events.length||body.events.length>20)fail(400,'Invalid event batch.');
 const clean=body.events.map(e=>{
  if(!e||!['view','click','error','visit'].includes(e.type)||!views.has(e.view)||!/^[a-z0-9_-]{1,64}$/.test(e.action??'')||!/^[a-f0-9-]{36}$/.test(e.id??'')||!Number.isSafeInteger(e.at)||Math.abs(e.at-now*1000)>86400000)fail(400,'Invalid product event.');
  return{id:e.id,at:e.at,type:e.type,view:e.view,action:e.action,session:sessionId.slice(0,16)};
 });
 try{await db.update({pk:`EVENTLIMIT#${userId}#${Math.floor(now/86400)}`,sk:'META'},'SET #n = if_not_exists(#n,:zero) + :one, #ttl = :ttl','attribute_not_exists(#n) OR #n < :limit',{'#n':'count','#ttl':'ttl'},{':zero':0,':one':1,':limit':300,':ttl':now+172800});}catch(e){if(db.conditional(e))fail(429,'Event limit reached.');throw e;}
 for(const data of clean){try{await db.transact([{Put:{Item:{pk:'EVENTS#'+userId,sk:'event#'+data.at+'#'+data.id,ttl:now+90*86400,data},ConditionExpression:'attribute_not_exists(pk)'}}]);}catch(e){if(!db.conditional(e))throw e;}}
 return{saved:clean.map(e=>e.id)};
}
async function all(db,pk,prefix,limit=5000){let cursor='',items=[];do{const p=await db.profilePage(pk,prefix,cursor,false);items.push(...p.items);cursor=p.cursor;}while(cursor&&items.length<limit);return{items,truncated:!!cursor};}
export async function adminAnalytics(db,now){
 const users=(await all(db,'USERS','',20)).items,rows=[];
 for(const u of users){
  const state=await all(db,'PROFILE#'+u.id,'state#'),prompts=await all(db,'PROFILE#'+u.id,'prompt#'),events=await all(db,'EVENTS#'+u.id,'event#',1000);
  const listens=state.items.filter(i=>i.kind==='track-stats'),recent=events.items.filter(e=>e.at>(now-90*86400)*1000),counts={};for(const e of recent){const key=e.type+':'+e.view+':'+e.action;counts[key]=(counts[key]??0)+1;}
  rows.push({id:u.id,username:u.username,role:u.role,seconds:listens.reduce((n,i)=>n+i.seconds,0),starts:listens.reduce((n,i)=>n+i.starts,0),qualified:listens.reduce((n,i)=>n+i.qualified,0),completed:listens.reduce((n,i)=>n+i.completed,0),skipped:listens.reduce((n,i)=>n+i.skipped,0),playlists:state.items.filter(i=>i.kind==='playlist'&&!i.deleted).length,prompts:prompts.items.length,events:recent.length,eventCounts:counts,recentPath:recent.slice(0,100).reverse(),truncated:state.truncated||prompts.truncated||events.truncated});
 }
 return{users:rows,generatedAt:now*1000,retentionDays:90,totals:{users:rows.length,seconds:rows.reduce((n,r)=>n+r.seconds,0),prompts:rows.reduce((n,r)=>n+r.prompts,0),events:rows.reduce((n,r)=>n+r.events,0)}};
}
