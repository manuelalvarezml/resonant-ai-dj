import {escapeHTML as esc} from './model.js';
export function isIOSWebKit(nav=globalThis.navigator){return /iPad|iPhone|iPod/.test(nav?.userAgent??'')||(nav?.platform==='MacIntel'&&nav.maxTouchPoints>1);}
export function swipeDirection(dx,dy){return Math.abs(dx)>=48&&Math.abs(dx)>Math.abs(dy)*1.5?(dx<0?'next':'previous'):null;}
export function adjacentTrack(player,direction){
 const index=player.index+(direction==='next'?1:-1);
 return player.queue[index]??(player.repeat==='all'?player.queue[direction==='next'?0:player.queue.length-1]:null);
}
export function shouldDismiss(distance,elapsed){return distance>100||(distance>38&&distance/Math.max(elapsed,1)>.55);}
export function mountMobilePlayer(player,{nativeAudio=false,closeQueue=()=>{}}={}){
 const footer=document.querySelector('.player'),canvas=document.querySelector('.spectrum-accent'),track=document.querySelector('#player-track');
 const home=document.createComment('desktop visualizer');canvas.before(home);
 const stage=document.createElement('div');stage.className='mobile-visualizer';
 const handle=document.createElement('div');handle.className='sheet-handle';handle.setAttribute('aria-hidden','true');
 const mini=document.createElement('canvas');mini.className='mini-spectrum';mini.setAttribute('role','img');mini.setAttribute('aria-label',nativeAudio?'Audio-derived frequency spectrum':'Live frequency spectrum');
 const expand=document.createElement('button');expand.type='button';expand.className='player-expand';expand.setAttribute('aria-label','Open now playing and visualization');
 const preview=document.createElement('div');preview.className='swipe-preview';preview.setAttribute('aria-hidden','true');
 const viewport=document.createElement('div');viewport.className='swipe-viewport';track.before(viewport);viewport.append(track,preview);
 footer.prepend(handle,stage);footer.append(mini,expand);footer.tabIndex=-1;
 const media=matchMedia('(max-width:700px)'),reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const isOpen=()=>document.body.classList.contains('player-expanded');
 let sheetAnimation=null;
 function setExpanded(value){
  const open=value&&media.matches,wasOpen=isOpen();sheetAnimation?.cancel();sheetAnimation=null;
  if(open===wasOpen)return;
  if(!open&&wasOpen&&media.matches){
   const current=getComputedStyle(footer).transform;settling=true;
   sheetAnimation=footer.animate([{transform:current==='none'?'translate3d(0,0,0)':current,borderRadius:getComputedStyle(footer).borderRadius},{transform:'translate3d(0,100dvh,0)',borderRadius:'42px 42px 0 0'}],{duration:reduced.matches?100:660,easing:'cubic-bezier(.32,.72,0,1)',fill:'forwards'});
   sheetAnimation.finished.then(()=>{apply(false);reset();sheetAnimation?.cancel();sheetAnimation=null;settling=false;}).catch(()=>{settling=false;});return;
  }
  const y=footer.getBoundingClientRect().top;apply(open);
  if(open){footer.getBoundingClientRect();sheetAnimation=footer.animate([{transform:`translate3d(0,${y}px,0)`,borderRadius:'42px 42px 0 0'},{transform:'translate3d(0,0,0)',borderRadius:'0px'}],{duration:reduced.matches?100:780,easing:'cubic-bezier(.32,.72,0,1)'});}
 }
 function apply(open){
  document.body.classList.toggle('player-expanded',open);expand.setAttribute('aria-expanded',String(open));
  document.querySelector('#app').inert=open;footer.setAttribute('role',open?'dialog':'contentinfo');footer.setAttribute('aria-label',open?'Now playing. Swipe down or press Escape to minimize.':'Audio player');
  if(open){footer.setAttribute('aria-modal','true');footer.focus({preventScroll:true});}else{footer.removeAttribute('aria-modal');expand.focus({preventScroll:true});}
 }

 expand.onclick=()=>setExpanded(true);
 function layout(){if(media.matches){document.body.append(footer);stage.prepend(canvas);}else{home.after(canvas);document.querySelector('.workspace').insertBefore(footer,document.querySelector('main'));setExpanded(false);}}
 media.addEventListener('change',layout);layout();
 let gesture=null,consumeClick=false,settling=false;
 function reset(){track.style.transform='';preview.style.transform='';preview.style.opacity='0';footer.style.transform='';footer.style.borderRadius='';footer.classList.remove('gesture-moving');}
 footer.addEventListener('pointerdown',event=>{
  if(!media.matches||settling||event.button>0)return;consumeClick=false;footer.getAnimations().forEach(animation=>animation.cancel());
  if(!isOpen()&&event.target.closest('button,input')!==expand)return;
  gesture={x:event.clientX,y:event.clientY,t:performance.now(),axis:null,open:isOpen(),width:viewport.clientWidth,pointer:event.pointerId,target:event.target};
 });
 footer.addEventListener('pointermove',event=>{
  if(!gesture)return;const dx=event.clientX-gesture.x,dy=event.clientY-gesture.y;
  if(!gesture.axis&&Math.max(Math.abs(dx),Math.abs(dy))>8){
   gesture.axis=gesture.open?(dy>0&&dy>Math.abs(dx)?'y':'ignore'):(Math.abs(dx)>Math.abs(dy)*1.3?'x':'ignore');
   if(gesture.axis==='ignore')return;
   footer.setPointerCapture(event.pointerId);footer.classList.add('gesture-moving');consumeClick=true;
  }
  if(gesture.axis==='y'){event.preventDefault();footer.style.transform=`translate3d(0,${Math.max(0,dy)}px,0)`;const radius=42*(1-Math.exp(-Math.max(0,dy)/95));footer.style.borderRadius=`${radius}px ${radius}px 0 0`;}
  if(gesture.axis==='x'){
   event.preventDefault();const direction=dx<0?'next':'previous',next=adjacentTrack(player,direction);
   const shift=next?dx:dx*.22;track.style.transform=`translate3d(${shift}px,0,0)`;
   if(gesture.direction!==direction){gesture.direction=direction;preview.innerHTML=next?`<strong>${esc(next.title)}</strong><span>${esc(next.artist)}</span>`:'';}
   preview.style.opacity=next?'1':'0';preview.style.transform=`translate3d(${shift+(dx<0?gesture.width:-gesture.width)}px,0,0)`;
  }
 },{passive:false});
 async function finish(event,cancel=false){
  if(!gesture)return;const g=gesture;gesture=null;if(footer.hasPointerCapture(g.pointer))footer.releasePointerCapture(g.pointer);
  const dx=event.clientX-g.x,dy=event.clientY-g.y;
  footer.classList.remove('gesture-moving');
  if(g.axis==='y'&&!cancel&&shouldDismiss(dy,performance.now()-g.t)){
   setExpanded(false);
  }else if(g.axis==='x'&&!cancel&&swipeDirection(dx,dy)&&adjacentTrack(player,dx<0?'next':'previous')){
   settling=true;const direction=dx<0?'next':'previous';track.style.transform=`translate3d(${dx<0?-g.width:g.width}px,0,0)`;preview.style.transform='translate3d(0,0,0)';
   setTimeout(async()=>{try{if(direction==='next')await player.next();else if(player.index===0&&player.repeat==='all'){player.index=player.queue.length-1;await player.load();}else await player.previous(false);}finally{footer.classList.add('gesture-reset');reset();requestAnimationFrame(()=>footer.classList.remove('gesture-reset'));settling=false;}},reduced.matches?0:160);
  }else reset();
 }
 footer.addEventListener('pointerup',event=>void finish(event));footer.addEventListener('pointercancel',event=>void finish(event,true));
 footer.addEventListener('click',event=>{if(consumeClick){event.stopPropagation();event.preventDefault();consumeClick=false;}},true);
 document.addEventListener('keydown',event=>{if(document.querySelector('dialog[open]'))return;if(event.key==='Escape'&&isOpen())setExpanded(false);if(event.key==='Tab'&&isOpen()){
  const buttons=[...footer.querySelectorAll('button,input')].filter(el=>!el.disabled&&el.getClientRects().length);const first=buttons[0],last=buttons.at(-1);
  if(event.shiftKey&&(document.activeElement===first||document.activeElement===footer)){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
 }});
 // Queue preserves normal upward scrolling; pull down only from its scroll origin.
 const queue=document.querySelector('#queue-panel');let pull=null;
 queue.addEventListener('touchstart',event=>{if(event.touches.length===1)pull={x:event.touches[0].clientX,y:event.touches[0].clientY,t:performance.now(),active:false,top:queue.scrollTop};},{passive:true});
 queue.addEventListener('touchmove',event=>{if(!pull)return;const p=event.touches[0],dy=p.clientY-pull.y;
  if(pull.top<=0&&dy>8&&dy>Math.abs(p.clientX-pull.x)){pull.active=true;event.preventDefault();queue.classList.add('gesture-moving');queue.style.transform=`translate3d(0,${dy}px,0)`;}
 },{passive:false});
 function endPull(event,cancel=false){if(!pull)return;const p=event.changedTouches[0],close=pull.active&&!cancel&&shouldDismiss(p.clientY-pull.y,performance.now()-pull.t);queue.classList.remove('gesture-moving');pull=null;if(close)closeQueue();else queue.style.transform='';}
 queue.addEventListener('touchend',event=>endPull(event));queue.addEventListener('touchcancel',event=>endPull(event,true));
 // Mouse/pen dragging follows the same dismissal rule in desktop device previews.
 let mousePull=null,queueDragged=false;
 queue.addEventListener('pointerdown',event=>{if(!media.matches||event.pointerType==='touch'||event.button>0)return;queueDragged=false;mousePull={x:event.clientX,y:event.clientY,t:performance.now(),top:queue.scrollTop,id:event.pointerId};});
 queue.addEventListener('pointermove',event=>{if(!mousePull)return;const dy=event.clientY-mousePull.y;if(mousePull.top<=0&&dy>8&&dy>Math.abs(event.clientX-mousePull.x)){queueDragged=true;queue.setPointerCapture(event.pointerId);queue.classList.add('gesture-moving');queue.style.transform=`translate3d(0,${dy}px,0)`;event.preventDefault();}});
 const endMousePull=(event,cancel=false)=>{if(!mousePull)return;const close=queueDragged&&!cancel&&shouldDismiss(event.clientY-mousePull.y,performance.now()-mousePull.t);if(queue.hasPointerCapture(mousePull.id))queue.releasePointerCapture(mousePull.id);mousePull=null;queue.classList.remove('gesture-moving');if(close)closeQueue();else queue.style.transform='';};
 queue.addEventListener('pointerup',event=>endMousePull(event));queue.addEventListener('pointercancel',event=>endMousePull(event,true));
 queue.addEventListener('click',event=>{if(queueDragged){event.preventDefault();event.stopPropagation();queueDragged=false;}},true);
}
