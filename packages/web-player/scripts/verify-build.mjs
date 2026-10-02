import {readFile,readdir,stat} from 'node:fs/promises';
import path from 'node:path';import {fileURLToPath} from 'node:url';import {createHash} from 'node:crypto';import assert from 'node:assert/strict';
const root=fileURLToPath(new URL('../dist/',import.meta.url));
const manifest=JSON.parse(await readFile(path.join(root,'build-manifest.json'),'utf8'));
const files=[];async function walk(dir){for(const e of await readdir(dir,{withFileTypes:true})){const file=path.join(dir,e.name);if(e.isDirectory())await walk(file);else files.push(path.relative(root,file));}}await walk(root);
assert.deepEqual(files.filter(f=>f!=='build-manifest.json').sort(),Object.keys(manifest.files).sort());
let bytes=0;for(const [name,hash] of Object.entries(manifest.files)){
  assert.match(name,/\.(html|css|js|json|svg|ttf|txt)$/);const content=await readFile(path.join(root,name));bytes+=content.length;assert.equal(createHash('sha256').update(content).digest('hex'),hash,name);
  assert.ok(!/\/Users\/|AUTODJ_OPENAI_API_DEV_KEY|BEGIN PRIVATE KEY/.test(content.toString()),`Private material in ${name}`);
  if(name.endsWith('.js'))for(const match of content.toString().matchAll(/from ['"](\.[^'"]+)['"]/g))assert.ok((await stat(path.resolve(root,path.dirname(name),match[1]))).isFile(),name);
}
const css=await readFile(path.join(root,'src/styles.css'),'utf8');
for(const match of css.matchAll(/url\(['"]?(\.\.[^'"\)]+)['"]?\)/g))assert.ok((await stat(path.resolve(root,'src',match[1]))).isFile(),match[1]);
assert.match(await readFile(path.join(root,'fonts/OFL.txt'),'utf8'),/SIL OPEN FONT LICENSE/);
const config=JSON.parse(await readFile(path.join(root,'config.json'),'utf8'));assert.equal(config.mode,'local');
console.log(JSON.stringify({status:'passed',files:Object.keys(manifest.files).length,bytes,manifest_sha256:createHash('sha256').update(await readFile(path.join(root,'build-manifest.json'))).digest('hex'),private_audio_included:false}));
