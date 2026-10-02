import assert from 'node:assert/strict';
const base=process.argv[2]??'http://127.0.0.1:4173';
const files=['/','/src/styles.css','/src/app.js','/src/player.js','/src/adapters.js','/config.json','/favicon.svg','/fonts/geist-mono-light.ttf','/fonts/geist-mono-regular.ttf','/fonts/OFL.txt'];
for(const file of files){const response=await fetch(base+file);assert.equal(response.status,200,file);assert.ok(response.headers.get('Content-Security-Policy'));assert.equal(response.headers.get('Referrer-Policy'),'no-referrer');if(file.endsWith('.js'))assert.match(response.headers.get('Content-Type'),/javascript/);if(file.endsWith('.ttf')){assert.equal(response.headers.get('Content-Type'),'font/ttf');assert.ok(Number(response.headers.get('Content-Length'))>0);}}
for(const file of ['/package.json','/scripts/serve.mjs','/.git/config','/nonexistent'])assert.equal((await fetch(base+file)).status,404,file);
assert.equal((await fetch(base+'/',{method:'POST'})).status,405);
console.log('15 preview checks passed: app assets, private-file denial, security headers and method restriction.');
