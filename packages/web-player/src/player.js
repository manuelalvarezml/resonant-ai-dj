import {moveItem, shuffled} from './model.js';

export class Player extends EventTarget {
  constructor(audio,resolver) {
    super(); this.audio=audio; this.resolver=resolver; this.queue=[]; this.index=-1; this.status='idle'; this.error=''; this.repeat='off'; this.shuffle=false; this.epoch=0; this.wantPlay=false; this.renewals=0;
    audio.preload='metadata';
    audio.addEventListener('playing',()=>{if(this.wantPlay){this.status='playing';this.emit();} else audio.pause();});
    audio.addEventListener('pause',()=>{if(this.status!=='loading' && this.status!=='error'){this.status='paused';this.emit();}});
    audio.addEventListener('waiting',()=>{if(this.wantPlay){this.status='buffering';this.emit();}});
    audio.addEventListener('timeupdate',()=>{if(this.renewals && this.status==='playing' && audio.currentTime>(this.renewedAt??Infinity)+1)this.renewals=0;this.emit('progress');});
    audio.addEventListener('durationchange',()=>this.emit('progress'));
    audio.addEventListener('loadedmetadata',()=>{
      if(this.pendingSeek != null && Number.isFinite(audio.duration)) { audio.currentTime=Math.min(this.pendingSeek,Math.max(0,audio.duration-0.05)); this.pendingSeek=null; }
      this.emit('progress');
    });
    audio.addEventListener('ended',()=>this.next(true));
    audio.addEventListener('error',()=>this.mediaError());
  }
  get current() { return this.queue[this.index] ?? null; }
  emit(type='change') {this.dispatchEvent(new Event(type));}
  setQueue(tracks,index=0) {
    this.queue=[...tracks]; this.index=index;
    if(this.shuffle && this.current) {const first=this.current;this.queue=[first,...shuffled(tracks.filter((_,i)=>i!==index))];this.index=0;}
    this.renewals=0; return this.load(0);
  }
  async load(position=0,renewal=false,autoplay=true) {
    const epoch=++this.epoch; this.controller?.abort(); this.controller=new AbortController();
    this.audio.pause(); this.audio.removeAttribute('src'); this.audio.load(); this.session?.release(); this.session=null;
    if(!this.current) {this.status='idle';this.wantPlay=false;this.pendingSeek=null;this.emit();return;}
    if(!renewal) this.renewals=0;
    this.wantPlay=autoplay;this.status='loading';this.error='';this.pendingSeek=position;this.renewedAt=position;this.emit();
    try {
      const session=await this.resolver(this.current,{position,signal:this.controller.signal});
      if(epoch!==this.epoch){session.release();return;}
      this.session=session;this.audio.src=session.url;this.audio.load();
      if(this.wantPlay) await this.attemptPlay(epoch); else {this.status='paused';this.emit();}
    } catch(error) { if(epoch===this.epoch && error.name!=='AbortError') this.fail(error.message); }
  }
  async attemptPlay(epoch=this.epoch) {
    try { await this.audio.play(); if(epoch===this.epoch && !this.wantPlay) this.audio.pause(); }
    catch(error) {
      if(epoch!==this.epoch || !this.wantPlay || error.name==='AbortError') return;
      // Unsupported-media failures are handled here; capability expiry by the media error event.
      if(this.session?.expiresAt && this.session.expiresAt<=Date.now()+5000 && this.renewals<1) return this.mediaError();
      this.fail(error.name==='NotAllowedError' ? 'Playback was blocked by the browser. Press Play to try again.' : 'This audio could not play. Retry or choose another track.');
    }
  }
  fail(message) {this.wantPlay=false;this.status='error';this.error=message;this.audio.pause();this.emit();}
  async mediaError() {
    if(!this.session || !this.current || this.status==='error') return;
    if(this.session.expiresAt && this.session.expiresAt<=Date.now()+5000 && this.renewals<1 && this.wantPlay) {this.renewals++; return this.load(this.audio.currentTime || this.pendingSeek || 0,true);}
    this.fail('The audio is unavailable or could not be decoded. Retry playback or choose another track.');
  }
  toggle() {
    if(!this.current) return;
    if(this.wantPlay){this.wantPlay=false;this.audio.pause();this.status='paused';this.emit();return;}
    this.wantPlay=true;
    if(!this.session || this.status==='error' || (this.session.expiresAt && this.session.expiresAt<=Date.now()+5000)) return this.load(this.audio.currentTime || this.pendingSeek || 0);
    return this.attemptPlay();
  }
  next(ended=false) {
    if(!this.current) return;
    if(ended && this.repeat==='one') return this.load(0);
    if(this.index+1<this.queue.length){this.index++;return this.load(0);}
    if(this.repeat==='all'){this.index=0;return this.load(0);}
    this.wantPlay=false;this.audio.pause();this.status='ended';this.emit();
  }
  previous() {if(this.audio.currentTime>3) return this.seek(0); if(this.index>0){this.index--;return this.load(0);} this.seek(0);}
  seek(seconds) {
    if(!this.current || !Number.isFinite(seconds)) return;
    const target=Math.max(0,Math.min(seconds,Number.isFinite(this.audio.duration)?this.audio.duration:seconds));
    if(this.session?.expiresAt && this.session.expiresAt<=Date.now()+5000) return this.load(target,false,this.wantPlay);
    if(this.audio.readyState>0)this.audio.currentTime=target; else this.pendingSeek=target;
    this.emit('progress');
  }
  enqueue(track,next=false) {
    if(!this.current) {this.queue=[track];this.index=0;this.pendingSeek=null;this.status='paused';this.emit();return;}
    this.queue.splice(next?this.index+1:this.queue.length,0,track);this.emit();
  }
  remove(index) {
    if(index<0 || index>=this.queue.length)return;
    const wasCurrent=index===this.index,wanted=this.wantPlay;this.queue.splice(index,1);
    if(index<this.index)this.index--;
    if(wasCurrent){this.index=Math.min(this.index,this.queue.length-1);if(!this.queue.length)this.index=-1;return this.load(0,false,wanted);}
    this.emit();
  }
  move(from,to) {
    if(from<0||to<0||from>=this.queue.length||to>=this.queue.length)return;
    this.queue=moveItem(this.queue,from,to);
    if(this.index===from)this.index=to; else if(from<this.index && to>=this.index)this.index--; else if(from>this.index && to<=this.index)this.index++;
    this.emit();
  }
  toggleShuffle() {this.shuffle=!this.shuffle;if(this.shuffle){this.queue=[...this.queue.slice(0,this.index+1),...shuffled(this.queue.slice(this.index+1))];}this.emit();}
  clear() {this.epoch++;this.controller?.abort();this.wantPlay=false;this.audio.pause();this.audio.removeAttribute('src');this.audio.load();this.session?.release();this.session=null;this.queue=[];this.index=-1;this.pendingSeek=null;this.status='idle';this.error='';this.emit();}
}
