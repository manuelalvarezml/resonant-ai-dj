import {randomBytes,randomUUID,scrypt as derive,timingSafeEqual,createHash} from 'node:crypto';
import {promisify} from 'node:util';
import {createRemoteJWKSet,jwtVerify} from 'jose';
const scrypt=promisify(derive),options={N:131072,r:8,p:1,maxmem:256*1024*1024};
const fail=(status,message)=>{throw Object.assign(Error(message),{status});};
const digest=s=>createHash('sha256').update(s).digest('hex');
export const identityKey=(kind,value)=>'IDENTITY#'+kind+'#'+digest(value);
export const publicUser=u=>({id:u.id,username:u.username,email:u.email,role:u.role});
export async function hashPassword(password){if(typeof password!=='string'||password.length<12||password.length>128)fail(400,'Use a password with 12–128 characters.');const salt=randomBytes(16).toString('hex'),key=await scrypt(password,salt,64,options);return `scrypt1$${salt}$${key.toString('hex')}`;}
export async function verifyPassword(password,hash){const [,salt,key]=String(hash??'').split('$');const actual=await scrypt(typeof password==='string'?password:'',salt??'00000000000000000000000000000000',64,options);return !!key&&/^[a-f0-9]{128}$/.test(key)&&timingSafeEqual(actual,Buffer.from(key,'hex'));}
const jwks=createRemoteJWKSet(new URL('https://www.googleapis.com/oauth2/v3/certs'),{timeoutDuration:5000});
export async function verifyGoogle(credential,clientId,nonce,keyset=jwks){
 try{const{payload:p}=await jwtVerify(credential,keyset,{audience:clientId,issuer:['https://accounts.google.com','accounts.google.com'],algorithms:['RS256'],requiredClaims:['exp','iat','sub','email','nonce']});if(p.nonce!==nonce||p.email_verified!==true||typeof p.sub!=='string'||typeof p.email!=='string')throw Error();return p;}catch{fail(401,'Google sign-in could not be verified. Please try again.');}
}
export function createAccounts(db,now){
 const lookup=async(kind,value)=>{const identity=await db.get(identityKey(kind,value));return identity?db.get('USER#'+identity.userId):null;};
 async function register({email,username,password,googleSub,role='listener'}){
  email=String(email??'').trim().toLowerCase();username=String(username??'').trim().toLowerCase();
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||email.length>254)fail(400,'Enter a valid email address.');
  if(!/^[a-z0-9_]{3,24}$/.test(username))fail(400,'Use 3–24 letters, numbers or underscores for your username.');
  const passwordHash=googleSub?null:await hashPassword(password),id=randomUUID();
  const user={pk:'USER#'+id,sk:'META',id,email,username,passwordHash,googleSub:googleSub??null,role,created:now(),disabled:false};
  const keys=[identityKey('email',email),identityKey('username',username),...(googleSub?[identityKey('google',googleSub)]:[])];
  const put=Item=>({Put:{Item,ConditionExpression:'attribute_not_exists(pk)'}});
  try{await db.transact([put(user),...keys.map(pk=>put({pk,sk:'META',userId:id})),put({pk:'USERS',sk:id,data:publicUser(user)}),{Update:{Key:{pk:'ACCOUNTS#COUNT',sk:'META'},UpdateExpression:'SET #n = if_not_exists(#n,:zero) + :one',ConditionExpression:'attribute_not_exists(#n) OR #n < :limit',ExpressionAttributeNames:{'#n':'count'},ExpressionAttributeValues:{':zero':0,':one':1,':limit':10}}}]);}
  catch(e){if(!db.conditional(e))throw e;fail(409,'Registration is unavailable for these details, or the testing group is full. Try another username or sign in.');}
  return user;
 }
 async function login(identifier,password){
  if(typeof identifier!=='string'||identifier.length>254||typeof password!=='string'||password.length>128)fail(401,'Email/username or password not recognized.');
  const value=identifier.trim().toLowerCase(),u=await lookup(value.includes('@')?'email':'username',value);
  if(!await verifyPassword(password,u?.passwordHash)||u.disabled)fail(401,'Email/username or password not recognized.');return u;
 }
 return{register,login,lookup};
}
