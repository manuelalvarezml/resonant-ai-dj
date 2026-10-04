// Observed media progress, not elapsed wall time or seeks. Nothing is inferred about taste.
export function listenedDelta({position,previousPosition,elapsed,playing,seeking}){
 const delta=position-previousPosition;return playing&&!seeking&&delta>0&&delta<=Math.max(1,elapsed*1.5+.25)?Math.min(delta,elapsed+.25):0;
}
export function attachListeningStats(player,profile,{clock=()=>performance.now()}={}){
 let visit=null;
 const flush=(finish=false,ended=false)=>{
  if(!visit)return;const qualified=visit.seconds>=Math.min(30,visit.duration/2),completed=ended&&visit.seconds>=visit.duration*.8;
  const delta=Math.max(0,visit.seconds-visit.sent),qual=qualified&&!visit.qualified?1:0;
  if(delta||!visit.started||finish){
   try{let remaining=delta;while(remaining>300){profile.enqueue({type:'listen',trackId:visit.id,seconds:300,requestId:visit.context?.requestId??null,playlistId:visit.context?.playlistId??null});visit.sent+=300;remaining-=300;}profile.enqueue({type:'listen',trackId:visit.id,seconds:remaining,starts:visit.started?0:1,qualified:qual,completed:completed?1:0,skipped:finish&&!ended&&visit.seconds>0&&visit.seconds<30?1:0,requestId:visit.context?.requestId??null,playlistId:visit.context?.playlistId??null});visit.sent=visit.seconds;visit.started=true;visit.qualified ||= qualified;}catch(e){profile.onError(e.message);}
  }
  if(finish)visit=null;
 };
 const sample=()=>{
  const audio=player.audio,t=clock();
  if(visit){visit.seconds+=listenedDelta({position:audio.currentTime||0,previousPosition:visit.position,elapsed:(t-visit.time)/1000,playing:player.status==='playing'&&!audio.paused,seeking:audio.seeking});visit.position=audio.currentTime||0;visit.time=t;if(visit.seconds-visit.sent>=30)flush();}
 };
 player.addEventListener('change',()=>{
  if(visit&&(visit.number!==player.listeningVisit||visit.id!==player.current?.id))flush(true);
  if(!visit&&player.current&&player.status==='playing')visit={id:player.current.id,number:player.listeningVisit,epoch:player.epoch,duration:player.audio.duration||player.current.duration||Infinity,position:player.audio.currentTime||0,time:clock(),seconds:0,sent:0,started:false,qualified:false,context:player.listeningContext};
  if(visit&&visit.epoch!==player.epoch){visit.epoch=player.epoch;visit.position=player.audio.currentTime||0;visit.time=clock();}
  if(visit&&player.status==='paused'){sample();flush();}
 });
 player.addEventListener('progress',sample);player.addEventListener('trackended',()=>{sample();flush(true,true);});
 player.audio.addEventListener('seeking',()=>{if(visit){visit.position=player.audio.currentTime;visit.time=clock();}});
 document.addEventListener('visibilitychange',()=>{sample();flush();void profile.sync();});
 window.addEventListener('pagehide',()=>{sample();flush();});
 return ()=>flush();
}
