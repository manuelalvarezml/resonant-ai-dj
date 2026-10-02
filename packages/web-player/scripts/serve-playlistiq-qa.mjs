// Isolated presentation harness: recorded plans and generated audio, no provider calls.
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('..',import.meta.url));
const files={'/':'tests/browser/playlistiq.html','/__iq-qa.html':'tests/browser/playlistiq.html','/__iq-qa.js':'tests/browser/playlistiq.js','/__iq-qa-data.json':'tests/browser/playlistiq-data.json'};
http.createServer(async(req,res)=>{
 try{
  if(req.headers.host!=='127.0.0.1:4188'||req.method!=='GET')throw Error();
  const name=new URL(req.url,'http://127.0.0.1:4188').pathname;
  const file=files[name]??(/^\/src\/[a-z-]+\.(js|css)$/.test(name)?name.slice(1):null);if(!file)throw Error();
  res.setHeader('Content-Type',file.endsWith('.html')?'text/html':file.endsWith('.js')?'text/javascript':file.endsWith('.css')?'text/css':'application/json');
  res.setHeader('Cache-Control','no-store');res.end(await readFile(path.join(root,file)));
 }catch{res.writeHead(404);res.end('Not found');}
}).listen(4188,'127.0.0.1',()=>console.log('Isolated PlaylistIQ QA: http://127.0.0.1:4188'));
