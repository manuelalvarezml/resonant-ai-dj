// Disposable component acceptance harness. No PlaylistIQ calls or profile writes.
// Start the real app on 4177 first, then run this file and open port 4191.
import http from 'node:http';
const markup=`<!doctype html><html lang="en"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Artwork result layout check</title>
<link rel="stylesheet" href="/src/styles.css"><link rel="stylesheet" href="/src/web-refresh.css"><link rel="stylesheet" href="/src/artwork.css">
<style>body{display:block;overflow:auto;padding:16px;box-sizing:border-box}main{max-width:720px;margin:auto}h1{font-size:22px}section{margin:30px 0}p{line-height:1.5}.iq-matches{padding-left:22px}button{color:inherit}</style>
<body class="web-edition"><main><h1>Artwork result layout check</h1><p>Display fixtures using existing library tracks. No model request, ranking evaluation or profile write.</p><section id="fresh"></section><section id="saved"></section></main><script type="module" src="/artwork-check.js"></script></body></html>`;
const script=`import {webIntentHTML} from '/src/web-presentation.js';
import {promptResultsHTML} from '/src/profile-views.js';
import {startArtwork} from '/src/artwork.js';
const data=await(await fetch('/api/v1/tracks')).json();
const tracks=data.tracks;
const art=await(await fetch('/api/artwork/manifest')).json();
const sample=tracks.filter(t=>art.tracks[t.id]?.status==='ready').slice(0,3);
document.querySelector('#fresh').innerHTML='<h2>Fresh results fixture</h2>'+webIntentHTML({status:'complete',result:{matches:sample.map(t=>({track:{track_id:t.id,title:t.title,artist:t.artist},score:0}))}});
document.querySelector('#saved').innerHTML='<h2>Saved results fixture</h2>'+promptResultsHTML({prompt:'Artwork layout fixture',trackIds:sample.map(t=>t.id)},tracks);
startArtwork({library:{mode:'http'},getTracks:()=>tracks});`;
const server=http.createServer(async(req,res)=>{
 if(req.headers.host!=='127.0.0.1:4191'){res.writeHead(403);res.end();return;}
 if(req.method!=='GET'){res.writeHead(405);res.end();return;}
 if(req.url==='/'||req.url==='/artwork-check.js'){res.writeHead(200,{'Content-Type':req.url==='/'?'text/html':'text/javascript'});res.end(req.url==='/'?markup:script);return;}
 try{const response=await fetch('http://127.0.0.1:4177'+req.url);res.writeHead(response.status,{'Content-Type':response.headers.get('content-type')??'application/octet-stream'});res.end(Buffer.from(await response.arrayBuffer()));}catch{res.writeHead(503);res.end('Start the app on port 4177 first.');}
});
server.listen(4191,'127.0.0.1',()=>console.log('Artwork layout fixtures: http://127.0.0.1:4191'));
