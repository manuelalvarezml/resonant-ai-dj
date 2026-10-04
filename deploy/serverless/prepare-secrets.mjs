#!/usr/bin/env node
// Local files only. Never prints secrets or copies the plaintext listener password.
import {generateKeyPairSync,randomBytes} from 'node:crypto';
import {readFile,mkdir,writeFile,lstat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import bcrypt from './api/node_modules/bcryptjs/index.js';
const root=fileURLToPath(new URL('../..',import.meta.url)),args=process.argv.slice(2),value=k=>args.includes(k)?args[args.indexOf(k)+1]:null;
const dest=path.resolve(value('--output')??''),passwordFile=value('--listener-password-file'),keyFile=value('--openai-key-file');
if(!dest.startsWith(path.join(root,'output')+path.sep)||!passwordFile)throw Error('Use --output NEW-OUTPUT-DIRECTORY --listener-password-file PRIVATE-FILE [--openai-key-file PRIVATE-FILE]');
try{await lstat(dest);throw Error('Output already exists. Never overwrite signing keys.');}catch(e){if(e.code!=='ENOENT')throw e;}
const password=(await readFile(passwordFile,'utf8')).trim();if(password.length<20||/[\r\n\0]/.test(password))throw Error('Expected the prepared strong shared password.');
const key=keyFile?(await readFile(keyFile,'utf8')).trim():'';if(key&&(/\s/.test(key)||!key.startsWith('sk-')))throw Error('Invalid project key file.');
const {publicKey,privateKey}=generateKeyPairSync('rsa',{modulusLength:2048,publicKeyEncoding:{type:'spki',format:'pem'},privateKeyEncoding:{type:'pkcs8',format:'pem'}});
const prefix='/resonant/first-release',origin=randomBytes(48).toString('base64url');
await mkdir(dest,{mode:0o700,recursive:true});
for(const [name,data] of Object.entries({'cookie-public.pem':publicKey,'cookie-private.pem':privateKey,'origin.txt':origin,'ssm-parameters.json':JSON.stringify(Object.entries({origin,'password-hash':await bcrypt.hash(password,12),'signing-key':privateKey,openai:key}).map(([suffix,Value])=>({Name:prefix+'/'+suffix,Type:'SecureString',Tier:'Standard',Value,Overwrite:false})),null,2)}))await writeFile(path.join(dest,name),data,{mode:0o600,flag:'wx'});
console.log(JSON.stringify({prepared:true,openaiConfigured:Boolean(key),passwordReused:true,awsWrites:0}));
