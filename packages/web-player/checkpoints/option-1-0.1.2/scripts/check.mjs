import {readdir,readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
const root=fileURLToPath(new URL('..',import.meta.url));
let checked=0;for(const directory of ['src','scripts','tests'])for(const file of await readdir(path.join(root,directory))){if(!/\.(js|mjs)$/.test(file))continue;const result=spawnSync(process.execPath,['--check',path.join(root,directory,file)],{encoding:'utf8'});if(result.status!==0)throw new Error(result.stderr);checked++;}
const config=JSON.parse(await readFile(path.join(root,'public/config.json'),'utf8'));if(config.mode!=='local')throw new Error('The checked-in release configuration must remain local.');
console.log(`Syntax passed for ${checked} JavaScript modules; release config defaults to local.`);
