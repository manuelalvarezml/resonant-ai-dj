// Log-frequency display sampling. Interpolation is visual, not extra measured resolution.
export function spectrumBands(bins, sampleRate, fftSize, columns=96,minHz=40,upperHz=18000){
 const row=new Float32Array(columns), maxHz=Math.min(upperHz,sampleRate/2);
 const db=i=>Number.isFinite(bins[i])?Math.max(-90,Math.min(0,bins[i])):-90;
 const sample=position=>{
  const p=Math.max(0,Math.min(bins.length-1,position)),i=Math.floor(p),fraction=p-i;
  return db(i)*(1-fraction)+db(Math.min(i+1,bins.length-1))*fraction;
 };
 for(let x=0;x<columns;x++){
  const hz=minHz*(maxHz/minHz)**(x/(columns-1));
  const center=hz*fftSize/sampleRate;
  const bandwidth=center*((maxHz/minHz)**(.5/(columns-1))-(maxHz/minHz)**(-.5/(columns-1)));
  // Narrow bands interpolate a single position. Wider bands retain peaks,
  // with continuous edges instead of floor/ceil inclusion jumps.
  const radius=Math.max(0,(bandwidth-1)/2);
  const a=Math.max(0,center-radius),b=Math.min(bins.length-1,center+radius);
  let value=Math.max(sample(a),sample(b));
  for(let i=Math.ceil(a);i<=Math.floor(b);i++)value=Math.max(value,db(i));
  row[x]=(value+90)/90;
 }
 return row;
}

export function splitSpectrumBands(lowBins,highBins,sampleRate,columns=96,minHz=40,upperHz=18000){
 const low=spectrumBands(lowBins,sampleRate,8192,columns,minHz,upperHz);
 const high=spectrumBands(highBins,sampleRate,2048,columns,minHz,upperHz);
 const maxHz=Math.min(upperHz,sampleRate/2);
 return low.map((value,x)=>minHz*(maxHz/minHz)**(x/(columns-1))<350?value:high[x]);
}
