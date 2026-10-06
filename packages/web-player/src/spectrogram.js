import {spectrumMotion} from './spectrum-preference.js';
import {splitSpectrumBands} from './spectrum-bands.js';
import {advanceSpectrumFrame} from './spectrum-timing.js';
// Live frequency × time × amplitude point surface. No decoded-track cache.
export function attachSpectrogram(audio, canvas, enabled=true,{fixedMode=null,webEdition=false,sampleSpectrum=null}={}) {
  const controls=canvas.parentElement.querySelector('.spectrum-modes');
  const paint=canvas.getContext('2d');
  if(!paint || !enabled){canvas.hidden=true;if(controls)controls.hidden=true;return;}
  let context, analyser, source, bins, highAnalyser, highBins, frame=0, last=0, lastHistory=0, pauseAt=null, riseAt=null;
  const pauseDuration=2800, riseDuration=1600, miniSettleDuration=1600;
  let miniRow=null;
  const amplitudeGain=1.30, pointScale=1.60;
  const rows=[], columns=96, depth=64, extendedDepth=Math.round(depth*1.3);
  // Grain is fixed by point/history index, not audio or time. Compute it once
  // on the first visible textured frame, retaining the exact existing design.
  let grainX,grainY;
  let mode=fixedMode||'front';
  try{const saved=!fixedMode&&localStorage.getItem('resonant:spectrogram-view');if(['front','isometric','mountain','falling'].includes(saved))mode=saved;}catch{}
  function selectMode(next){
    mode=fixedMode||next;
    for(const button of controls?.querySelectorAll('button')??[])button.setAttribute('aria-pressed',String(button.dataset.spectrum===mode));
    canvas.setAttribute('aria-label',`${sampleSpectrum?'Audio-derived':'Live'} spectrogram: ${mode} view. Logarithmic frequency in Hz; FFT magnitude in dBFS, referenced to the newest time slice.`);
    try{if(!fixedMode)localStorage.setItem('resonant:spectrogram-view',mode);}catch{}
    draw();
  }
  controls?.addEventListener('click',event=>{const next=event.target.closest('button')?.dataset.spectrum;if(next)selectMode(next);});
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let followSystem=spectrumMotion()==='system';
  const reduceSpectrum=()=>followSystem&&reduced.matches;
  window.addEventListener('spectrum-motion-change',()=>{followSystem=spectrumMotion()==='system';});
  const mini=()=>webEdition?document.querySelector('.mini-spectrum'):null;
  const visible=()=>!document.hidden && (canvas.getBoundingClientRect().width>0||(mini()?.clientWidth??0)>0);
  function draw(){
    const bounds=canvas.getBoundingClientRect();
    if(!bounds.width || !bounds.height)return;
    const width=Math.max(1,bounds.width-(webEdition?72:68)),height=Math.max(1,bounds.height-52);
    const ratio=Math.min(devicePixelRatio||1,2);
    if(canvas.width!==Math.round(bounds.width*ratio)||canvas.height!==Math.round(bounds.height*ratio)){
      canvas.width=Math.round(bounds.width*ratio);canvas.height=Math.round(bounds.height*ratio);
    }
    paint.setTransform(ratio,0,0,ratio,0,0);paint.clearRect(0,0,bounds.width,bounds.height);
    paint.translate(webEdition?36:56,24);
    const descent=pauseAt===null?0:Math.min(1,(performance.now()-pauseAt)/pauseDuration);
    const rise=riseAt===null?1:Math.min(1,((pauseAt??performance.now())-riseAt)/riseDuration);
    const riseOffset=(1-rise)**3;
    const pauseFade=1-descent*descent*(3-2*descent);
    const falling=mode==='falling', textured=mode==='mountain'||falling;
    if(textured&&!grainX){
      grainX=Array.from({length:extendedDepth},(_,z)=>Float64Array.from({length:columns*3},(_,x)=>Math.sin(x*127.1+z*311.7)*.65));
      grainY=Array.from({length:extendedDepth},(_,z)=>Float64Array.from({length:columns*3},(_,x)=>Math.cos(x*73.3+z*19.7)*.8));
    }
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
          px=width*(.03+u*.94)+grainX[z][x];
          py=height*(base-distance*.12-energy*vertical+fall*fall*.32)+grainY[z][x];
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
    const maxHz=Math.min(webEdition?20000:18000,(context?.sampleRate??48000)/2);
    paint.font='11px "Geist Mono", monospace';
    paint.fillStyle='rgba(226,226,218,.7)';
    paint.textAlign='right';paint.textBaseline='middle';
    for(const value of [-90,-75,-60,-45,-30,-15,0]){
      const y=height*(base-((value+90)/90)*vertical);if(y<0)continue;
      paint.fillText(String(value),-8,y);
      paint.fillRect(-3,y,4,1);
    }
    paint.textAlign='left';paint.textBaseline='alphabetic';
    paint.fillText('dBFS',webEdition?-32:-36,-8);
    const minHz=webEdition?20:40;
    const ticks=webEdition?(width<380?[20,100,1000,10000,20000]:[20,40,100,250,1000,4000,10000,20000]):width<380?[40,100,250,1000,4000,10000]:[40,80,160,315,630,1250,2500,5000,10000,16000];
    let lastTick=-Infinity;
    for(const hz of ticks){
      if(hz>maxHz)continue;
      const u=Math.log(hz/minHz)/Math.log(maxHz/minHz),x=width*(startX+u*spanX);
      if(x-lastTick<28||x>width-24)continue;lastTick=x;
      paint.textAlign=hz===40?'left':'center';
      paint.fillText(hz>=1000?`${hz/1000}k`:String(hz),x,height+18);
      paint.fillRect(x,height+1,1,4);
    }
    paint.textAlign='right';paint.fillText('Hz',width,height+18);
  }

  function drawMini(row,gain=1){
    const el=mini();if(!el?.clientWidth)return;const ctx=el.getContext('2d');if(!ctx)return;
    if(el.width!==128){el.width=128;el.height=52;}ctx.clearRect(0,0,128,52);ctx.fillStyle='#deded5';
    for(let i=0;i<24;i++){const value=row?Math.max(...row.subarray(i*4,i*4+4)):0,h=Math.max(2,value*48*gain);ctx.fillRect(i*5+4,(52-h)/2,2,h);}
  }
  function stop(){cancelAnimationFrame(frame);frame=0;}
  function tick(now){
    frame=0;
    if(!visible())return;
    const next=advanceSpectrumFrame(last,now,reduceSpectrum()?200:sampleSpectrum?1000/30:50);
    if(audio.paused||audio.ended){
      if(pauseAt===null)return;
      if(next!==null){last=next;draw();drawMini(miniRow,reduceSpectrum()?0:(1-Math.min(1,(now-pauseAt)/miniSettleDuration))**3);}
      if(now-pauseAt>=pauseDuration){rows.length=0;pauseAt=null;miniRow=null;drawMini(null);draw();return;}
      frame=requestAnimationFrame(tick);return;
    }
    if((sampleSpectrum||(analyser && context.state==='running')) && next!==null){
      last=next;let row;
      if(sampleSpectrum)row=sampleSpectrum(audio.currentTime);
      else{analyser.getFloatFrequencyData(bins);highAnalyser.getFloatFrequencyData(highBins);row=splitSpectrumBands(bins,highBins,context.sampleRate,columns,webEdition?20:40,webEdition?20000:18000);}
      if(!row){drawMini(null);frame=requestAnimationFrame(tick);return;}

      miniRow=row;drawMini(row);
      // Paint interpolated native data at 30 fps, but retain the existing
      // 20-slice/s history window rather than speeding up the falling trail.
      const history=advanceSpectrumFrame(lastHistory,now,reduceSpectrum()?200:50);
      if(history!==null||!rows.length){
        lastHistory=history??now;rows.unshift(row);if(rows.length>extendedDepth)rows.pop();
      }else rows[0]=row;
      draw();
    }
    frame=requestAnimationFrame(tick);
  }
  function start(){if(!frame && (analyser||sampleSpectrum) && (!audio.paused||pauseAt!==null) && visible())frame=requestAnimationFrame(tick);}
  function settle(){if((rows.length||miniRow)&&pauseAt===null)pauseAt=performance.now();if(pauseAt===null)drawMini(null);start();}
  function unlock(){
    if(sampleSpectrum){start();return;}
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
  audio.addEventListener('play',()=>{rows.length=0;pauseAt=null;riseAt=performance.now();last=riseAt;lastHistory=riseAt;});
  audio.addEventListener('playing',start);
  audio.addEventListener('pause',settle);audio.addEventListener('ended',settle);
  for(const event of ['emptied','seeking'])audio.addEventListener(event,()=>{miniRow=null;drawMini(null);rows.length=0;pauseAt=null;riseAt=null;draw();});
  document.addEventListener('visibilitychange',()=>{stop();start();});
  new ResizeObserver(()=>{stop();draw();if(audio.paused)drawMini(miniRow,pauseAt===null||reduceSpectrum()?0:(1-Math.min(1,(performance.now()-pauseAt)/miniSettleDuration))**3);start();}).observe(canvas);
  window.addEventListener('pagehide',stop);
  window.addEventListener('pageshow',start);
  selectMode(mode);
}
