// Bounded local ID3 reads; never decode audio or infer an artist from a filename.
export async function readAudioTags(file){
 const bytes=new Uint8Array(await file.slice(0,2*1024*1024).arrayBuffer());
 const ascii=b=>String.fromCharCode(...b);
 const sync=b=>b.reduce((n,v)=>(n<<7)|(v&127),0);
 const uint=b=>b.reduce((n,v)=>n*256+v,0);
 const clean=s=>s.replace(/\0/g,' ').trim().slice(0,500);
 const decode=b=>{
  if(!b.length)return '';
  const encoding=['windows-1252','utf-16','utf-16be','utf-8'][b[0]];
  if(!encoding)return '';
  return clean(new TextDecoder(encoding).decode(b.subarray(1)));
 };
 const tags={};
 if(ascii(bytes.subarray(0,3))==='ID3'&&[2,3,4].includes(bytes[3])){
  const version=bytes[3],end=Math.min(bytes.length,10+sync(bytes.subarray(6,10)));
  let data=bytes.subarray(10,end);
  if(bytes[5]&128&&version<4)data=data.filter((v,i)=>!(v===0&&data[i-1]===255));
  let p=0;
  if(bytes[5]&64&&version!==2)p=version===4?sync(data.subarray(0,4)):4+uint(data.subarray(0,4));
  if(!(version===2&&(bytes[5]&64)))while(p+(version===2?6:10)<=data.length){
   const header=version===2?6:10,id=ascii(data.subarray(p,p+(version===2?3:4)));
   const size=version===2?uint(data.subarray(p+3,p+6)):(version===4?sync:uint)(data.subarray(p+4,p+8));
   if(!/^[A-Z0-9]+$/.test(id)||!size||p+header+size>data.length)break;
   const flags=version===2?0:data[p+9];
   let frame=data.subarray(p+header,p+header+size);
   const field={TIT2:'title',TT2:'title',TPE1:'artist',TP1:'artist',TALB:'album',TAL:'album'}[id];
   if(field&&!(flags&(version===4?0x4d:0xe0))){
    if(version===4&&((bytes[5]&128)||(flags&2)))frame=frame.filter((v,i)=>!(v===0&&frame[i-1]===255));
    const value=decode(frame);if(value)tags[field]=value;
   }
   p+=header+size;
  }
 }
 const tail=new Uint8Array(await file.slice(Math.max(0,file.size-128)).arrayBuffer());
 if(tail.length===128&&ascii(tail.subarray(0,3))==='TAG'){
  for(const [field,start] of [['title',3],['artist',33],['album',63]])
   if(!tags[field]){const value=clean(new TextDecoder('windows-1252').decode(tail.subarray(start,start+30)));if(value)tags[field]=value;}
 }
 return tags;
}
export function featureTags(track){
 const stage=track.features?.algorithms?.find(a=>a.algorithm_id==='metadata'&&a.status!=='failed');
 return Object.fromEntries(Object.entries(stage?.values?.encoded_tags??{}).filter(([k,v])=>['title','artist','album'].includes(k.toLowerCase())&&typeof v==='string'&&v.trim()).map(([k,v])=>[k.toLowerCase(),v.trim().slice(0,500)]));
}
export function applyAudioTags(track,tags){
 const next={...track,embeddedTags:tags};
 for(const field of ['title','artist','album'])if(tags[field])next[field]=tags[field];
 next.evidence=(track.evidence??[]).filter(e=>e.source!=='embedded-tags/1'&&!(tags.title&&e.field==='Title'&&e.source==='browser-file/1'));
 for(const [field,value] of Object.entries(tags))next.evidence.push({field:field[0].toUpperCase()+field.slice(1),value,authority:'encoded_fact',source:'embedded-tags/1'});
 return next;
}
