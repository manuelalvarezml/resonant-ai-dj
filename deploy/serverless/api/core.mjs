import {recordEvents,adminAnalytics} from './analytics.mjs';
import {createProfileStore} from './profile.mjs';
import {createHash,randomBytes,createSign,timingSafeEqual} from 'node:crypto';
import {createAccounts,publicUser,verifyGoogle,identityKey} from './accounts.mjs';
export const canonical=value=>JSON.stringify(Array.isArray(value)?value.map(v=>JSON.parse(canonical(v))):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,JSON.parse(canonical(value[k]))])):value).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
export const sha=value=>createHash('sha256').update(value).digest('hex');
const uuid=/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/;
const terminal=new Set(['succeeded','needs_clarification','failed','expired','outcome_unknown','dispatch_failed']);
const fail=(status,message)=>{throw Object.assign(Error(message),{status});};
const equal=(a,b)=>typeof a==='string'&&typeof b==='string'&&Buffer.byteLength(a)===Buffer.byteLength(b)&&timingSafeEqual(Buffer.from(a),Buffer.from(b));
const cookie=(name,value,age=86400)=>`${name}=${value}; Path=/; Secure; HttpOnly; SameSite=Lax; Max-Age=${age}`;
const encode=s=>Buffer.from(s).toString('base64').replaceAll('+','-').replaceAll('=','_').replaceAll('/','~');
export function signedCookies(origin,keyPairId,privateKey,expires){
 const policy=JSON.stringify({Statement:[{Resource:origin+'/*',Condition:{DateLessThan:{'AWS:EpochTime':expires}}}]});
 const signature=createSign('RSA-SHA1').update(policy).sign(privateKey);
 return [cookie('CloudFront-Policy',encode(policy)),cookie('CloudFront-Signature',encode(signature)),cookie('CloudFront-Key-Pair-Id',keyPairId)];
}
export function playlistRequest(body,member){
 if(!body||typeof body!=='object'||Array.isArray(body)||Object.keys(body).some(k=>!['prompt','tracks','clarifications','estimator_profile','releaseId','idempotencyKey'].includes(k))||typeof body.prompt!=='string'||!body.prompt.trim()||body.prompt.length>4000||!uuid.test(body.idempotencyKey??'')||!Array.isArray(body.tracks)||!body.tracks.length||body.tracks.length>member.size)fail(400,'Invalid playlist request.');
 const ids=new Set();const tracks=body.tracks.map(row=>{const saved=member.get(row?.id);if(!saved||row.sha256!==saved.sha256||ids.has(row.id))fail(400,'Invalid library selection.');ids.add(row.id);return{id:row.id,sha256:saved.sha256};});
 const profile=body.estimator_profile??'reference';if(!['reference','quality','music2emo','musicnn-dance','supervised'].includes(profile))fail(400,'Invalid estimator profile.');
 const answers=body.clarifications??[];if(!Array.isArray(answers)||answers.length>3||answers.some(a=>!a||Object.keys(a).some(k=>!['question','answer'].includes(k))||typeof a.question!=='string'||!a.question.trim()||a.question.length>500||typeof a.answer!=='string'||!a.answer.trim()||a.answer.length>1000))fail(400,'Invalid clarification.');
 return{prompt:body.prompt,tracks,clarifications:answers,estimator_profile:profile};
}
export function createHandler({db,objects,dispatch,secrets,config,now=()=>Math.floor(Date.now()/1000)}){
 const members=new Map(config.tracks.map(t=>[t.id,t]));
 const allowedOrigins=new Set([config.origin,...(config.additionalOrigins??[])]);
 const accounts=createAccounts(db,now);
 const cookieValue=(event,headers,name)=>(event.cookies??[headers.cookie??'']).join(';').split(';').map(x=>x.trim()).find(x=>x.startsWith(name+'='))?.slice(name.length+1);
 async function sessionFor(user,origin,values){
  const token=randomBytes(32).toString('base64url'),csrf=randomBytes(32).toString('base64url'),expires=now()+30*86400;
  await db.put({pk:'SESSION#'+sha(token),sk:'META',userId:user.id,csrf,expires,ttl:expires});
  return response(200,{csrf,expiresAt:expires*1000,user:publicUser(user)},[cookie('__Host-resonant_session',token,30*86400),...signedCookies(origin,config.keyPairId,values.signingKey,now()+86400)]);
 }
 const response=(status,body,cookies)=>({statusCode:status,headers:{'content-type':'application/json','cache-control':'private,no-store','x-content-type-options':'nosniff'},...(cookies?{cookies}:{}),body:JSON.stringify(body)});
 async function googleIdentity(event,headers,body){
  const auth=await db.get('AUTH#CONFIG'),nonce=cookieValue(event,headers,'__Host-resonant_nonce');
  if(!auth?.googleClientId)fail(503,'Google sign-in is not configured yet. Use email and password.');
  if(!nonce||nonce.length!==43||typeof body.credential!=='string'||body.credential.length>10000)fail(401,'Restart Google sign-in.');
  const saved=await db.get('NONCE#'+sha(nonce));if(!saved||saved.ttl<=now())fail(401,'Restart Google sign-in.');
  const g=await verifyGoogle(body.credential,auth.googleClientId,nonce);
  try{await db.update({pk:saved.pk,sk:'META'},'SET used = :yes','attribute_not_exists(used)',{}, {':yes':true});}catch(e){if(db.conditional(e))fail(401,'Restart Google sign-in.');throw e;}
  return g;
 }
 async function expire(job){
  if(!job||terminal.has(job.status)||job.deadline>now())return job;
  const status=job.providerStarted?'outcome_unknown':'expired';
  try{await db.update({pk:job.pk,sk:'META'},'SET #s = :s','#s IN (:a,:b,:c) AND deadline <= :now',{'#s':'status'},{':s':status,':a':'dispatching',':b':'queued',':c':'running',':now':now()});}catch(e){if(!db.conditional(e))throw e;}
  return await db.get(job.pk);
 }
 async function send(job){
  if(job.status!=='dispatching')return{id:job.id};
  try{await dispatch({jobId:job.id,releaseId:job.releaseId});}
  catch{fail(503,'Dispatch could not be confirmed. Retry this request with the same request key.');}
  try{await db.update({pk:job.pk,sk:'META'},'SET #s = :queued','#s = :dispatching',{'#s':'status'},{':queued':'queued',':dispatching':'dispatching'});}catch(e){if(!db.conditional(e))throw e;}
  return{id:job.id};
 }
 async function submit(body,owner){
  if(body.releaseId!==config.releaseId)fail(409,'The library changed. Refresh before creating a playlist.');
  const active=await db.get('CONFIG#ACTIVE');if(!active?.enabled||active.releaseId!==config.releaseId)fail(503,'PlaylistIQ is temporarily unavailable. Library playback is still available.');
  const request=playlistRequest(body,members),digest=sha(canonical(request));
  const hex=sha(owner+'\n'+body.idempotencyKey).slice(0,32),id=[hex.slice(0,8),hex.slice(8,12),hex.slice(12,16),hex.slice(16,20),hex.slice(20)].join('-');
  const pk='JOB#'+id;
  let job=await db.get(pk);
  if(job){if(job.owner!==owner||job.requestSha256!==digest)fail(409,'This request key was already used for different inputs.');if(job.ttl<=now())fail(410,'This request has expired. Start a new request.');return send(await expire(job));}
  await objects.immutableRequest('requests/'+id+'.json',request,digest);
  const stamp=now(),day=new Date(stamp*1000).toISOString().slice(0,10),month=day.slice(0,7);
  job={pk,sk:'META',id,owner,releaseId:config.releaseId,requestSha256:digest,status:'dispatching',created:stamp,deadline:stamp+1020,ttl:stamp+86400};
  for(let slot=0;slot<3;slot++){
   const slotPK='SLOT#'+slot,old=await db.get(slotPK);let previous;
   if(old?.jobId){previous=await expire(await db.get('JOB#'+old.jobId));if(old.deadline>stamp&&(!previous||!terminal.has(previous.status)))continue;}
   const guard=old?.jobId?'jobId = :old':'attribute_not_exists(jobId)';
   const operations=[{Put:{Item:job,ConditionExpression:'attribute_not_exists(pk)'}},
    {Update:{Key:{pk:slotPK,sk:'META'},UpdateExpression:'SET jobId = :id, deadline = :deadline',ConditionExpression:guard,ExpressionAttributeValues:{':id':id,':deadline':job.deadline,...(old?.jobId?{':old':old.jobId}:{})}}},
    ...[[`DAY#${day}`,30,stamp+172800],[`MONTH#${month}`,900,stamp+5356800]].map(([counter,limit,ttl])=>({Update:{Key:{pk:counter,sk:'META'},UpdateExpression:'SET #n = if_not_exists(#n,:zero) + :one, #ttl = :ttl',ConditionExpression:'attribute_not_exists(#n) OR #n < :limit',ExpressionAttributeNames:{'#n':'count','#ttl':'ttl'},ExpressionAttributeValues:{':zero':0,':one':1,':limit':limit,':ttl':ttl}}}))];
   try{await db.transact(operations);return send(job);}catch(e){if(!db.conditional(e))throw e;const existing=await db.get(pk);if(existing){if(existing.requestSha256!==digest)fail(409,'Conflicting request key.');return send(await expire(existing));}}
  }
  fail(429,'The playlist request limit or queue capacity has been reached. Try again later.');
 }
 return async event=>{
  try{
   const values=await secrets();
   const headers=Object.fromEntries(Object.entries(event.headers??{}).map(([k,v])=>[k.toLowerCase(),v]));
   if(!equal(headers['x-resonant-origin'],values.originSecret))fail(403,'Access denied.');
   const method=event.requestContext?.http?.method,path=event.rawPath;
   if(method==='POST'&&!allowedOrigins.has(headers.origin))fail(403,'Invalid request origin.');
   const bytes=event.isBase64Encoded?Buffer.from(event.body??'','base64'):Buffer.from(event.body??'');
   if(bytes.length>65536)fail(413,'Request too large.');
   let body={};if(bytes.length){if(!headers['content-type']?.toLowerCase().startsWith('application/json'))fail(415,'JSON required.');try{body=JSON.parse(bytes.toString('utf8'));}catch{fail(400,'Invalid JSON.');}}
   if(!body||typeof body!=='object'||Array.isArray(body))fail(400,'Invalid JSON object.');
   if(method==='GET'&&path==='/api/auth/config'){
    const auth=await db.get('AUTH#CONFIG'),nonce=randomBytes(32).toString('base64url');
    await db.put({pk:'NONCE#'+sha(nonce),sk:'META',ttl:now()+600});
    return response(200,{googleClientId:auth?.googleClientId??null,nonce},[cookie('__Host-resonant_nonce',nonce,600)]);
   }
   if(method==='POST'&&['/api/session/login','/api/session/signup','/api/session/google'].includes(path)){
    const throttle='LOGIN#'+sha(values.originSecret+'\n'+(headers['x-forwarded-for']?.split(',').at(-1).trim()||event.requestContext.http.sourceIp))+'#'+Math.floor(now()/300);
    try{await db.update({pk:throttle,sk:'META'},'SET #n = if_not_exists(#n,:zero) + :one, #ttl = :ttl','attribute_not_exists(#n) OR #n < :limit',{'#n':'count','#ttl':'ttl'},{':zero':0,':one':1,':ttl':now()+600,':limit':10});}catch(e){if(db.conditional(e))fail(429,'Too many sign-in attempts. Wait a few minutes.');throw e;}
    let user;
    if(path.endsWith('/signup'))user=await accounts.register({email:body.email,username:body.username,password:body.password});
    else if(path.endsWith('/google')){
     const g=await googleIdentity(event,headers,body);
     user=await accounts.lookup('google',g.sub);
     if(!user){if(await accounts.lookup('email',g.email.toLowerCase()))fail(409,'An email/password account already uses this email. Sign in with your password.');user=await accounts.register({email:g.email,username:body.username||('dj_'+sha(g.sub).slice(0,10)),googleSub:g.sub});}
     if(user.disabled)fail(401,'This account is unavailable.');
    }else user=await accounts.login(body.identifier,body.password);
    return sessionFor(user,headers.origin,values);
   }
   const raw=(event.cookies??[headers.cookie??'']).join(';').split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-resonant_session='))?.slice('__Host-resonant_session='.length);
   if(!raw||!/^[A-Za-z0-9_-]{43}$/.test(raw))fail(401,'Sign in to continue.');
   const session=await db.get('SESSION#'+sha(raw));
   if(!session?.userId||session.expires<=now())fail(401,'Your session has expired. Sign in again.');
   const user=await db.get('USER#'+session.userId);if(!user||user.disabled)fail(401,'Sign in to continue.');
   if(!path.startsWith('/api/session')&&!equal(headers['x-resonant-user'],user.id))fail(401,'Account changed. Sign in to continue.');
   const owner=user.id,profile=createProfileStore(db,new Set(members.keys()),'PROFILE#'+owner);
   if(method==='POST'&&!equal(headers['x-resonant-csrf'],session.csrf))fail(403,'Refresh the page before retrying.');
   if(method==='GET'&&path==='/api/session')return response(200,{csrf:session.csrf,expiresAt:session.expires*1000,user:publicUser(user)});
   if(method==='POST'&&path==='/api/session/refresh'){
    const expires=now()+30*86400;await db.update({pk:session.pk,sk:'META'},'SET expires = :expiry, #ttl = :expiry','expires > :now',{'#ttl':'ttl'},{':expiry':expires,':now':now()});
    return response(200,{csrf:session.csrf,expiresAt:expires*1000,user:publicUser(user)},[cookie('__Host-resonant_session',raw,30*86400),...signedCookies(headers.origin,config.keyPairId,values.signingKey,now()+86400)]);
   }
   if(method==='POST'&&path==='/api/session/logout'){
    await db.delete(session.pk);return response(200,{signedOut:true},['__Host-resonant_session','CloudFront-Policy','CloudFront-Signature','CloudFront-Key-Pair-Id'].map(n=>cookie(n,'',0)));
   }
   if(path==='/api/session/link-google'&&method==='POST'){
    const g=await googleIdentity(event,headers,body);if(g.email.toLowerCase()!==user.email)fail(400,'Choose the Google account with the same email as your Resonant account.');
    if(user.googleSub===g.sub)return response(200,{linked:true});
    if(user.googleSub)fail(409,'A Google account is already linked.');
    try{await db.transact([{Put:{Item:{pk:identityKey('google',g.sub),sk:'META',userId:user.id},ConditionExpression:'attribute_not_exists(pk)'}},{Update:{Key:{pk:user.pk,sk:'META'},UpdateExpression:'SET googleSub = :sub',ConditionExpression:'googleSub = :empty',ExpressionAttributeValues:{':sub':g.sub,':empty':null}}}]);}catch(e){if(db.conditional(e))fail(409,'This Google account is already linked.');throw e;}
    return response(200,{linked:true});
   }
   if(path==='/api/events'&&method==='POST')return response(200,await recordEvents(db,owner,sha(raw),body,now()));
   if(path==='/api/admin/analytics'&&method==='GET'){if(user.role!=='owner')fail(403,'Owner access required.');return response(200,await adminAnalytics(db,now()));}
   if(path==='/api/profile'&&method==='GET')return response(200,await profile.list(event.queryStringParameters?.kind??'state',event.queryStringParameters?.cursor??''));
   if(path==='/api/profile'&&method==='POST')return response(200,await profile.apply(body.operations));
   if(method==='POST'&&path==='/api/playlist')return response(202,await submit(body,owner));
   const match=path?.match(/^\/api\/jobs\/([a-f0-9-]+)$/);
   if(method==='GET'&&match&&uuid.test(match[1])){
    let job=await db.get('JOB#'+match[1]);if(!job||job.owner!==owner||job.ttl<=now())fail(404,'Job not found.');
    job=await expire(job);
    if(['succeeded','needs_clarification'].includes(job.status))return response(200,{id:job.id,status:'complete',resultUrl:await objects.resultUrl(job.resultKey),resultSha256:job.resultSha256});
    if(terminal.has(job.status))return response(200,{id:job.id,status:'failed',error:job.status==='outcome_unknown'?'The previous attempt could not be confirmed. A new retry may incur another AI charge.':'Playlist preparation did not finish. Please retry.'});
    return response(200,{id:job.id,status:'running',message:job.status==='running'?'Preparing your playlist…':'Your playlist request is queued…'});
   }
   return response(404,{error:'Not found.'});
  }catch(e){return response(e.status??503,{error:e.status?e.message:'The service is temporarily unavailable. Please retry shortly.'});}
 };
}
