import {createHash} from 'node:crypto';
import {PROFILE_KEY,validateProfileOperation,profileTargets,mutateProfileItem} from '../../../packages/web-player/src/profile-model.js';
export function createProfileStore(db,members,profileKey=PROFILE_KEY){
 return {
  async list(kind='state',cursor=''){
   if(!['state','prompt'].includes(kind)||typeof cursor!=='string'||cursor.length>240||(cursor&&!cursor.startsWith(kind+'#')))throw Object.assign(Error('Invalid history view.'),{status:400});
   return db.profilePage(profileKey,kind+'#',cursor,kind!=='prompt');
  },
  async apply(operations){
   if(!Array.isArray(operations)||!operations.length||operations.length>20)throw Object.assign(Error('Invalid save batch.'),{status:400});
   operations.forEach(op=>validateProfileOperation(op,members));
   for(const op of operations){
    const marker='PROFILEOP#'+profileKey+'#'+op.id,digest=createHash('sha256').update(JSON.stringify(op)).digest('hex');
    for(let attempt=0;attempt<6;attempt++){
     const applied=await db.get(marker);if(applied){if(applied.digest!==digest)throw Object.assign(Error('This save ID was already used.'),{status:409});break;}
     const keys=profileTargets(op),previous=await Promise.all(keys.map(key=>db.profileGet(profileKey,key)));
     const writes=keys.map((key,i)=>({Put:{Item:{pk:profileKey,sk:key,revision:(previous[i]?.revision??0)+1,data:mutateProfileItem(previous[i]?.data,op,key)},ConditionExpression:previous[i]?'revision = :r':'attribute_not_exists(pk)',...(previous[i]?{ExpressionAttributeValues:{':r':previous[i].revision}}:{})}}));
     try{await db.transact([{Put:{Item:{pk:marker,sk:'META',digest},ConditionExpression:'attribute_not_exists(pk)'}},...writes]);break;}
     catch(e){if(!db.conditional(e))throw e;if(attempt===5)throw Object.assign(Error('Another save is finishing. Try again shortly.'),{status:409});}
    }
   }
   return{saved:operations.map(op=>op.id)};
  }
 };
}
