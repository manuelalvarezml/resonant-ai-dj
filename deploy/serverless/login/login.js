const $=s=>document.querySelector(s),message=$('#message');
async function send(path,body){const r=await fetch(path,{method:'POST',credentials:'same-origin',redirect:'error',cache:'no-store',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:AbortSignal.timeout(20000)});const result=await r.json();if(!r.ok)throw Error(result.error||'Could not sign in. Please retry.');return result;}
function finish(){try{localStorage.setItem('resonant:account-change',crypto.randomUUID());}catch{}location.replace('/index.html');}
for(const mode of ['login','signup']){
 $('#show-'+mode).onclick=()=>{for(const name of ['login','signup']){$('#'+name).hidden=name!==mode;$('#show-'+name).setAttribute('aria-pressed',String(name===mode));}message.textContent='';};
 $('#'+mode).addEventListener('submit',async event=>{event.preventDefault();const form=event.currentTarget,button=form.querySelector('button');button.disabled=true;message.textContent='Opening your library…';try{const f=form.elements;await send('/api/session/'+mode,mode==='login'?{identifier:f.username.value,password:f.password.value}:{email:f.email.value,username:f.username.value,password:f.password.value});finish();}catch(e){message.textContent=e.message;}finally{button.disabled=false;}});
}
try{
 const r=await fetch('/api/auth/config',{credentials:'same-origin',cache:'no-store'}),config=await r.json();
 if(config.googleClientId){const script=document.createElement('script');script.src='https://accounts.google.com/gsi/client';script.async=true;script.onload=()=>{google.accounts.id.initialize({client_id:config.googleClientId,nonce:config.nonce,auto_select:false,callback:async({credential})=>{message.textContent='Signing in with Google…';try{await send('/api/session/google',{credential,username:$('#signup').hidden?'':$('#username').value});finish();}catch(e){message.textContent=e.message+' Reload this page to try Google again.';}}});google.accounts.id.renderButton($('#google'),{theme:'outline',size:'large',text:'continue_with',width:280});};document.head.append(script);}
 else $('#google-note').textContent='Google sign-in will be available once connected by the owner.';
}catch{$('#google-note').textContent='Google sign-in could not load. Email sign-in is still available.';}

// A remembered, valid session can renew its shorter media cookies.
try{const r=await fetch('/api/session',{credentials:'same-origin',cache:'no-store'});if(r.ok){const s=await r.json();const renewed=await fetch('/api/session/refresh',{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-Resonant-CSRF':s.csrf},body:'{}'});if(renewed.ok)finish();}}catch{}
