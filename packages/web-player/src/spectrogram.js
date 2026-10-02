import {splitSpectrumBands} from './spectrum-bands.js';
// Live frequency × time × amplitude point surface. No decoded-track cache.
export function attachSpectrogram(audio, canvas, enabled=true) {
  const controls=canvas.parentElement.querySelector('.spectrum-modes');
  const paint=canvas.getContext('2d');
  if(!paint || !enabled){canvas.hidden=true;controls.hidden=true;return;}
  let context, analyser, source, bins, highAnalyser, highBins, frame=0, last=0, pauseAt=null, riseAt=null;
  const pauseDuration=2800, riseDuration=1600;
  const amplitudeGain=1.30, pointScale=1.60;
  const rows=[], columns=96, depth=64, extendedDepth=Math.round(depth*1.3);
  let mode='front';
  try{const saved=localStorage.getItem('resonant:spectrogram-view');if(['front','isometric','mountain','falling'].includes(saved))mode=saved;}catch{}
  function selectMode(next){
    mode=next;
    for(const button of controls.querySelectorAll('button'))button.setAttribute('aria-pressed',String(button.dataset.spectrum===mode));
    canvas.setAttribute('aria-label',`Live spectrogram: ${mode} view. Logarithmic frequency in Hz; FFT magnitude in dBFS, referenced to the newest time slice.`);
    try{localStorage.setItem('resonant:spectrogram-view',mode);}catch{}
    draw();
  }
  controls.addEventListener('click',event=>{const next=event.target.closest('button')?.dataset.spectrum;if(next)selectMode(next);});
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  const visible=()=>!document.hidden && canvas.getBoundingClientRect().width>0;
  function draw(){
    const bounds=canvas.getBoundingClientRect();
    if(!bounds.width || !bounds.height)return;
    const width=Math.max(1,bounds.width-68),height=Math.max(1,bounds.height-52);
    const ratio=Math.min(devicePixelRatio||1,2);
    if(canvas.width!==Math.round(bounds.width*ratio)||canvas.height!==Math.round(bounds.height*ratio)){
      canvas.width=Math.round(bounds.width*ratio);canvas.height=Math.round(bounds.height*ratio);
    }
    paint.setTransform(ratio,0,0,ratio,0,0);paint.clearRect(0,0,bounds.width,bounds.height);
    paint.translate(56,24);
    const descent=pauseAt===null?0:Math.min(1,(performance.now()-pauseAt)/pauseDuration);
    const rise=riseAt===null?1:Math.min(1,((pauseAt??performance.now())-riseAt)/riseDuration);
    const riseOffset=(1-rise)**3;
    const pauseFade=1-descent*descent*(3-2*descent);
    const falling=mode==='falling', textured=mode==='mountain'||falling;
    const visibleDepth=falling?extendedDepth:depth;
    const base=falling?.78:textured?.91:.9;
    const vertical=Math.min(base-.05,(textured?(falling?.6:.73):.55)*amplitudeGain);
    paint.save();paint.beginPath();paint.rect(0,0,width,height);paint.clip();
    if(textured){
      // Fine registration grid, no invented measurements or tiny labels.
      paint.fillStyle='rgba(220,220,210,.12)';
      for(let y=height*.12;y<height*.94;y+=height*.2)
        for(let x=width*.04;x<width*.96;x+=7)paint.fillRect(x,y,.6,.6);
    }
    for(let z=visibleDepth-1;z>=0;z--){
      const row=rows[z], distance=z/(visibleDepth-1), scale=1-distance*.28;
      if(!row)continue;
      // A smooth accelerating descent over the oldest 30% of Falling history.
      const fall=falling?Math.max(0,(distance-.7)/.3):0;
      const fade=1-fall*fall*(3-2*fall);
      paint.fillStyle=`rgba(226,226,218,${(textured?.12+(1-distance)*.36:.14+(1-distance)*.42)*fade*pauseFade})`;
      const steps=textured?columns*3:columns;
      for(let x=0;x<steps;x++){
        const u=x/(steps-1), at=u*(columns-1), low=Math.floor(at), mix=at-low;
        let energy=(row?.[low]||0)*(1-mix)+(row?.[Math.min(columns-1,low+1)]||0)*mix;
        let px=width*(.08+u*.82), py=height*(base-energy*vertical);
        if(mode==='isometric'){
          px=width*(.08+distance*.16+u*.82*scale);
          py=height*(base-distance*.31-energy*vertical*scale);
        }else if(textured){
          // Interpolate the measured dB values without artistic magnitude taper.
          if(energy<.012)continue;
          const grain=Math.sin(x*127.1+z*311.7);
          px=width*(.03+u*.94)+grain*.65;
          py=height*(base-distance*.12-energy*vertical+fall*fall*.32)+(Math.cos(x*73.3+z*19.7))*.8;
        }
        py+=(height*1.06-py)*riseOffset;
        py+=height*1.1*descent*descent;
        const pointSize=(textured?.8:1)*pointScale;
        paint.fillRect(px,py,pointSize,pointSize);
      }
    }
    paint.restore();
    // The dBFS axis references the newest slice; historical rows retain perspective.
    const startX=textured?.03:.08, spanX=textured?.94:.82;
    const maxHz=Math.min(18000,(context?.sampleRate??48000)/2);
    paint.font='11px "Geist Mono", monospace';
    paint.fillStyle='rgba(226,226,218,.7)';
    paint.textAlign='right';paint.textBaseline='middle';
    for(const value of [-90,-75,-60,-45,-30,-15,0]){
      const y=height*(base-((value+90)/90)*vertical);if(y<0)continue;
      paint.fillText(String(value),-8,y);
      paint.fillRect(-3,y,4,1);
    }
    paint.textAlign='left';paint.textBaseline='alphabetic';
    paint.fillText('dBFS',-36,-8);
    const ticks=width<380?[40,100,250,1000,4000,10000]:[40,80,160,315,630,1250,2500,5000,10000,16000];
    let lastTick=-Infinity;
    for(const hz of ticks){
      if(hz>maxHz)continue;
      const u=Math.log(hz/40)/Math.log(maxHz/40),x=width*(startX+u*spanX);
      if(x-lastTick<28||x>width-24)continue;lastTick=x;
      paint.textAlign=hz===40?'left':'center';
      paint.fillText(hz>=1000?`${hz/1000}k`:String(hz),x,height+18);
      paint.fillRect(x,height+1,1,4);
    }
    paint.textAlign='right';paint.fillText('Hz',width,height+18);
  }

  function stop(){cancelAnimationFrame(frame);frame=0;}
  function tick(now){
    frame=0;
    if(!visible())return;
    if(audio.paused||audio.ended){
      if(pauseAt===null)return;
      if(now-last>=(reduced.matches?200:50)){last=now;draw();}
      if(now-pauseAt>=pauseDuration){rows.length=0;pauseAt=null;draw();return;}
      frame=requestAnimationFrame(tick);return;
    }
    if(analyser && context.state==='running' && now-last>=(reduced.matches?200:50)){
      last=now;analyser.getFloatFrequencyData(bins);
      highAnalyser.getFloatFrequencyData(highBins);
      const row=splitSpectrumBands(bins,highBins,context.sampleRate,columns);
      rows.unshift(row);if(rows.length>extendedDepth)rows.pop();draw();
    }
    frame=requestAnimationFrame(tick);
  }
  function start(){if(!frame && analyser && (!audio.paused||pauseAt!==null) && visible())frame=requestAnimationFrame(tick);}
  function settle(){if(rows.length && pauseAt===null)pauseAt=performance.now();start();}
  function unlock(){
    const Audio=window.AudioContext||window.webkitAudioContext;
    if(!Audio)return;
    try{
      if(!context){
        context=new Audio();analyser=context.createAnalyser();analyser.fftSize=8192;
        analyser.smoothingTimeConstant=.65;analyser.minDecibels=-90;analyser.maxDecibels=-15;
        bins=new Float32Array(analyser.frequencyBinCount);
        highAnalyser=context.createAnalyser();highAnalyser.fftSize=2048;highAnalyser.smoothingTimeConstant=.65;
        highBins=new Float32Array(highAnalyser.frequencyBinCount);
        source=context.createMediaElementSource(audio);
        // Single audible path, separate analysis tap: never double the volume.
        source.connect(context.destination);source.connect(analyser);source.connect(highAnalyser);
      }
      void context.resume().then(start).catch(()=>{});
    }catch{canvas.hidden=true;}
  }
  document.addEventListener('pointerdown',unlock,{capture:true});
  document.addEventListener('keydown',unlock,{capture:true});
  audio.addEventListener('play',()=>{rows.length=0;pauseAt=null;riseAt=performance.now();});
  audio.addEventListener('playing',start);
  audio.addEventListener('pause',settle);audio.addEventListener('ended',settle);
  for(const event of ['emptied','seeking'])audio.addEventListener(event,()=>{rows.length=0;pauseAt=null;riseAt=null;draw();});
  document.addEventListener('visibilitychange',()=>{stop();start();});
  new ResizeObserver(()=>{stop();draw();start();}).observe(canvas);
  window.addEventListener('pagehide',stop);
  window.addEventListener('pageshow',start);
  selectMode(mode);
}
