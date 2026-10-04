import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import {readFileSync} from 'node:fs';
const template=JSON.parse(readFileSync(new URL('../../edge-template.json',import.meta.url)));const code=template.Resources.Entry.Properties.FunctionCode;
function request(uri,cookies={}){return vm.runInNewContext(code+';handler(event)',{event:{request:{uri,cookies}},Buffer,Date});}
test('document entry sends unsigned and expired viewers to sign-in',()=>{assert.equal(request('/').statusCode,302);const expired=Buffer.from(JSON.stringify({Statement:[{Condition:{DateLessThan:{'AWS:EpochTime':1}}}]})).toString('base64').replaceAll('+','-').replaceAll('=','_').replaceAll('/','~');assert.equal(request('/index.html',{'CloudFront-Policy':{value:expired}}).headers.location.value,'/login/index.html');});
test('entry function leaves API/assets untouched; CDN handles cookie signature validation',()=>{assert.equal(request('/api/session').uri,'/api/session');assert.equal(request('/media/fixture.mp3').uri,'/media/fixture.mp3');});
test('public shell can run first-visit redirect while library and media require signed cookies',()=>{
 const config=template.Resources.Distribution.Properties.DistributionConfig;
 assert.equal(config.DefaultCacheBehavior.TrustedKeyGroups,undefined);
 assert.equal(config.DefaultCacheBehavior.FunctionAssociations[0].EventType,'viewer-request');
 for(const path of ['/library/*','/media/*']) assert.equal(config.CacheBehaviors.find(b=>b.PathPattern===path).TrustedKeyGroups.length,1);
 assert.equal(config.CacheBehaviors.length,4);
});
