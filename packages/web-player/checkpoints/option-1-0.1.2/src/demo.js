// Authored synthetic fixtures. These are never represented as the user's tracks.
const names = ['First light', 'Slow orbit', 'After hours', 'Open water', 'Soft focus', 'The long way home'];
export const demoTracks = names.map((title, i) => ({
  id:`demo-${i+1}`, sourceVersion:`synth-v1-${i+1}`, title, artist:'Resonant sessions', album:'Listening room · Generated demo',
  duration:24 + i * 4, addedAt:6-i, status:'ready', kind:'demo', color:i,
  evidence:[{field:'Audio', value:'Generated ambient tone study; fictional title and artist', authority:'encoded_fact', source:'resonant-demo/1'}]
}));
export function createDemoAudio(index) {
  const rate = 16000, duration = demoTracks[index].duration, samples = rate * duration;
  const buffer = new ArrayBuffer(44 + samples * 2), view = new DataView(buffer);
  const string = (offset, text) => [...text].forEach((c,i) => view.setUint8(offset+i,c.charCodeAt(0)));
  string(0,'RIFF'); view.setUint32(4,36+samples*2,true); string(8,'WAVE'); string(12,'fmt ');
  view.setUint32(16,16,true); view.setUint16(20,1,true); view.setUint16(22,1,true); view.setUint32(24,rate,true); view.setUint32(28,rate*2,true); view.setUint16(32,2,true); view.setUint16(34,16,true); string(36,'data'); view.setUint32(40,samples*2,true);
  const root = [130.81,146.83,110,164.81,174.61,123.47][index];
  for (let i=0; i<samples; i++) {
    const t = i/rate, fade = Math.min(1,t/1.2,(duration-t)/1.8), pulse = 0.7+0.3*Math.sin(t*Math.PI/4)**2;
    const chord = (Math.sin(t*root*2*Math.PI)+0.5*Math.sin(t*root*2.5*Math.PI)+0.35*Math.sin(t*root*3*Math.PI))/1.85;
    const bell = Math.sin(2*Math.PI*root*4*t) * Math.exp(-(t%2)*4) * 0.1;
    view.setInt16(44+i*2, Math.round((chord*0.17*pulse+bell)*fade*32767),true);
  }
  return new Blob([buffer],{type:'audio/wav'});
}
