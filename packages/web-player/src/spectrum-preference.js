const key='resonant:spectrum-motion';
export function spectrumMotion(){try{return localStorage.getItem(key)==='system'?'system':'full';}catch{return 'full';}}
export function setSpectrumMotion(value){if(!['full','system'].includes(value))return;try{localStorage.setItem(key,value);}catch{}window.dispatchEvent(new Event('spectrum-motion-change'));}
