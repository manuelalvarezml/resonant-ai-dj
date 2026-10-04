import {descriptorName} from './match-explanation.js';
// Human-readable result evidence, bounded to fit one durable save operation.
export function promptSnapshot(run,matches){
 const plan=run.translation?.plan??{};
 const snapshot={interpretation:String(plan.interpretation??'These tracks match your musical request.').slice(0,2000),context:Object.fromEntries(['occasion','activity','recipient','emotional_goal'].filter(k=>typeof plan[k]==='string'&&plan[k]).map(k=>[k,plan[k].slice(0,500)])),matches:matches.slice(0,100).map(m=>({id:m.track.track_id,score:Number.isFinite(m.score)?m.score:0,reasons:(m.score_contributions??[]).filter(c=>Number.isFinite(c.contribution)).sort((a,b)=>b.contribution-a.contribution).slice(0,5).map(c=>({label:(c.tags??[]).slice(0,2).map(descriptorName).join(' or ').slice(0,180)||'Musical character',fit:Number.isFinite(c.utility)?c.utility:0,weight:Number.isFinite(c.weight)?c.weight:0,points:c.contribution}))}))};
 while(new TextEncoder().encode(JSON.stringify(snapshot)).length>44000){const longest=snapshot.matches.reduce((a,b)=>a.reasons.length>=b.reasons.length?a:b);if(!longest.reasons.length)break;longest.reasons.pop();}
 return snapshot;
}
