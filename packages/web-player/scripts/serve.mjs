import {fileProfileStore,profileService} from './profile-service.mjs';
import {buildWebLibrary,prepareWebAudio} from './web-library.mjs';
import {createWebService} from './web-service.mjs';
import {localConversion} from './conversion.mjs';
import {mixService} from './mix-service.mjs';
import {localFeatures} from './local-features.mjs';
import http from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(fileURLToPath(new URL('..',import.meta.url))),built=process.argv.includes('--dist');
const portArg=process.argv.indexOf('--port'),port=portArg<0?4173:Number(process.argv[portArg+1]);
const webEdition=process.argv.includes('--web');
const webData=webEdition?await buildWebLibrary():null;
const webService=webData?createWebService(webData):null;
const profiles=webData?profileService(fileProfileStore(path.resolve(root,'../../output/web-profile/account.json'),new Set(webData.manifest.tracks.map(t=>t.id)))):null;
if(webData)console.log(`Web catalog: ${webData.manifest.tracks.length} fully analyzed MP3s`);
const csp="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'";
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml','.ttf':'font/ttf','.txt':'text/plain; charset=utf-8'};
const server=http.createServer(async(req,res)=>{
  res.setHeader('Content-Security-Policy',csp);res.setHeader('Referrer-Policy','no-referrer');res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Cache-Control','no-store');
  res.setHeader('Permissions-Policy','camera=(), microphone=(), geolocation=()');
  if(req.headers.host!==`127.0.0.1:${port}`&&req.headers.host!==`localhost:${port}`){res.writeHead(403);res.end('Invalid host');return;}
  if(webEdition){
    const pathname=new URL(req.url,'http://localhost').pathname;
    if(pathname==='/config.json'){res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify({contract_version:'resonant-player/config/1',mode:'http',edition:'web',apiBase:'/api/',mediaOrigins:[]}));return;}
    if(await profiles(req,res))return;
    if(await webService(req,res,port))return;
    if(pathname==='/api/local/playlist'||pathname.startsWith('/api/local/jobs/')){await localFeatures(req,res,port,{playlistTracks:webData.manifest.tracks});return;}
    if(pathname.startsWith('/api/')||pathname==='/app-status.json'||pathname.startsWith('/prepare-web')){res.writeHead(404);res.end('Not available in web edition');return;}
  }else{
  if(await prepareWebAudio(req,res,port))return;
  if(await mixService(req,res,port))return;
  if(await localConversion(req,res,port))return;
  if(await localFeatures(req,res,port))return;
  }
  if(!['GET','HEAD'].includes(req.method)){res.writeHead(405,{'Allow':'GET, HEAD'});res.end();return;}
  if(req.headers.host!==`127.0.0.1:${port}`&&req.headers.host!==`localhost:${port}`){res.writeHead(403);res.end('Invalid host');return;}
  try{
    const url=new URL(req.url,'http://localhost'),pathname=decodeURIComponent(url.pathname);
    const relative=pathname==='/'?'index.html':pathname.replace(/^\//,'');
    if(relative.split('/').some(part=>part==='..'||part.startsWith('.'))||relative.includes('\\'))throw new Error('Invalid path');
    const base=built?path.join(root,webEdition?'dist-web':'dist'):relative.startsWith('src/')?root:path.join(root,'public');
    const file=path.resolve(base,relative);if(!file.startsWith(base+path.sep))throw new Error('Invalid path');
    if(!(await stat(file)).isFile())throw new Error('Not a file');
    const content=await readFile(file);res.writeHead(200,{'Content-Type':types[path.extname(file)]??'application/octet-stream','Content-Length':content.length});res.end(req.method==='HEAD'?undefined:content);
  }catch{res.writeHead(404,{'Content-Type':'text/plain'});res.end('Not found');}
});
server.listen(port,'127.0.0.1',()=>console.log(`Resonant ${built?'production preview':'development'}: http://127.0.0.1:${port}`));
server.on('error',error=>{console.error(error.message);process.exitCode=1;});

process.on('SIGTERM',()=>{mixService.close();server.close();});
process.on('SIGINT',()=>{mixService.close();server.close();});
