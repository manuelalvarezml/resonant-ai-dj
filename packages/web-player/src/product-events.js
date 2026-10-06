export function attachProductEvents(cloud){
 let events=[],busy=false,lastView='';
 const view=()=>{const v=(location.hash.slice(1)||'library').split('/')[0];return ['library','favorites','playlists','playlist','analysis','playlistiq','mixes','status','account'].includes(v)?v:'library';};
 function add(type,action){if(events.length>=100)return;events.push({id:crypto.randomUUID(),at:Date.now(),type,action,view:view()});}
 async function flush(){if(busy||!events.length||!cloud.csrf)return;busy=true;const batch=events.slice(0,20);try{await cloud.fetchJSON('/api/events',{method:'POST',headers:{'Content-Type':'application/json','X-Resonant-CSRF':cloud.csrf},body:JSON.stringify({events:batch}),keepalive:true});events.splice(0,batch.length);}catch{}finally{busy=false;}}
 const navigate=()=>{const v=view();if(v!==lastView){lastView=v;add('view','navigate');}};
 document.addEventListener('click',e=>{const node=e.target.closest('[data-action],button[id],a[href^="#"]');if(!node)return;let action=node.dataset.action||node.id||'navigate';if(!/^[a-z0-9_-]{1,64}$/.test(action))action='control';add('click',action);});
 window.addEventListener('hashchange',navigate);window.addEventListener('pagehide',()=>void flush());document.addEventListener('visibilitychange',()=>{if(document.hidden)void flush();});
 const timer=setInterval(()=>void flush(),15000);window.addEventListener('pagehide',()=>clearInterval(timer),{once:true});
 add('visit','open');navigate();return{error:()=>add('error','operation-failed'),flush};
}
