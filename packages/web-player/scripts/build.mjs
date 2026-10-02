import './sync-app-status.mjs';
import {cp,mkdir,rm,readdir,readFile,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {createHash} from 'node:crypto';
const webEdition=process.argv.includes('--web');
const root=fileURLToPath(new URL('..',import.meta.url)),out=path.join(root,webEdition?'dist-web':'dist');
await rm(out,{recursive:true,force:true});await mkdir(out,{recursive:true});
await cp(path.join(root,'public'),out,{recursive:true});await cp(path.join(root,'src'),path.join(out,'src'),{recursive:true});
if(webEdition){await writeFile(path.join(out,'config.json'),JSON.stringify({contract_version:'resonant-player/config/1',mode:'http',edition:'web',apiBase:'/api/',mediaOrigins:[]}));await rm(path.join(out,'app-status.json'),{force:true});await rm(path.join(out,'prepare-web.html'),{force:true});}
const files=[];async function walk(dir){for(const entry of await readdir(dir,{withFileTypes:true})){const name=path.join(dir,entry.name);if(entry.isDirectory())await walk(name);else files.push(path.relative(out,name));}}await walk(out);
const metadata=JSON.parse(await readFile(path.join(root,'package.json'),'utf8'));
const hashes={};for(const file of files.sort())hashes[file]=createHash('sha256').update(await readFile(path.join(out,file))).digest('hex');
await writeFile(path.join(out,'build-manifest.json'),JSON.stringify({package:'@resonant/web-player',version:metadata.version,files:hashes},null,2)+'\n');
console.log(`Built ${files.length} static files to ${out}. No source audio included.`);
