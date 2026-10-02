export async function prepareMp3(file,request=fetch){
 if(!file.size||file.size>512*1024*1024)throw Error('Each audio file must be between 1 byte and 512 MB.');
 if(/\.mp3$/i.test(file.name))return file;
 if(!/\.m4a$/i.test(file.name))throw Error('Choose MP3 or M4A files. Other new upload formats are not supported yet.');
 const response=await request('/api/local/convert-m4a?filename='+encodeURIComponent(file.name),{method:'POST',headers:{'X-Resonant-Local':'1','Content-Type':'application/octet-stream'},body:file});
 if(!response.ok){const data=await response.json().catch(()=>({}));throw Error(data.error||'Conversion failed; original audio was kept.');}
 const bytes=await response.blob();if(!bytes.size)throw Error('Conversion returned empty audio.');
 return new File([bytes],file.name.replace(/\.m4a$/i,'.mp3'),{type:'audio/mpeg',lastModified:file.lastModified});
}
