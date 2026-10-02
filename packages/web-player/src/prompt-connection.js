import {escapeHTML as esc} from './model.js';

// Listening roles are conditional explanations of scored objectives, not new audio labels.
const roles={
 'mood:relaxed':{increase:['a relaxed mood','make the moment feel unhurried, with the music leaving room for whatever else is happening'],decrease:['less relaxation','give the scene a more alert feel rather than encouraging people to settle down']},
 'mood:happy':{increase:['a happy mood','bring a cheerful tone to the moment'],decrease:['less cheerfulness','avoid imposing a celebratory mood on the scene']},
 'mood:sad':{increase:['a sad mood','make room for reflection or difficult feelings'],decrease:['less sadness','keep the emotional tone from becoming too heavy']},
 'mood:aggressive':{increase:['an aggressive character','add force and tension to the moment'],decrease:['less aggression','keep the atmosphere from feeling confrontational']},
 'energy:low':{increase:['lower energy','let the music accompany the moment without demanding constant attention'],decrease:['less low-energy character','put less emphasis on a subdued listening experience']},
 'energy:medium':{increase:['moderate energy','aim for some movement without making intensity the main event'],decrease:['less moderate-energy character','move away from a middle-intensity listening experience']},
 'energy:high':{increase:['high energy','give the moment more drive and a sense of momentum'],decrease:['less high-energy intensity','keep the music from pushing the moment toward sustained intensity']},
 'danceability:danceable':{increase:['danceability','give people a rhythmic reason to move'],decrease:['less emphasis on danceability','put less pressure on the music to invite dancing']},
 'vocals:vocal':{increase:['vocals','give the listener a voice to focus on, without establishing what the lyrics mean'],decrease:['fewer vocals','leave more space for attention outside the sung voice']},
 'vocals:instrumental':{increase:['instrumental character','let the music accompany the scene without relying on a lead vocal'],decrease:['less instrumental character','put less emphasis on music without a lead vocal']},
};
function role(contribution){
 if(contribution.tags?.length!==1)return null;
 return roles[contribution.tags[0]]?.[contribution.direction]??null;
}
export function promptConnectionHTML(match,run){
 const translation=run.translation??{},plan=translation.plan;
 const prompt=translation.request_text?.trim();
 if(!prompt)return '';
 const contributions=match.score_contributions??[];
 const meaningful=contributions.filter(c=>c.evidence_value!=null&&Number.isFinite(c.contribution)&&c.contribution>0).sort((a,b)=>b.contribution-a.contribution);
 const connections=meaningful.filter(c=>role(c)).slice(0,3);
 const inferred=connections.some(c=>c.origin==='inferred');
 const calmReading=meaningful.some(c=>(c.direction==='increase'&&c.tags?.some(t=>['mood:relaxed','energy:low'].includes(t)))||(c.direction==='decrease'&&c.tags?.includes('energy:high')));
 const genreOnly=meaningful.length>0&&meaningful.every(c=>c.tags?.every(t=>t.startsWith('genre:')));
 const context=[['Occasion',plan?.occasion],['Activity',plan?.activity],['For',plan?.recipient],['Emotional aim',plan?.emotional_goal]].filter(([,value])=>typeof value==='string'&&value.trim());
 const interpretation=plan?.interpretation?.trim();
 const description=interpretation?`The planner read this as “${interpretation}”.`:'This result does not retain a scene interpretation, so only its recorded musical preferences can be explained.';
 const semantic=meaningful.find(c=>c.group==='semantic');
 const semanticConnection=semantic?`<p>The sampled audio was also compared directly with “${esc(run.result?.query?.semantic?.description??plan?.musical_description??'the planned musical character')}”. Its relative position in this library contributes ${(semantic.contribution*100).toFixed(2)} points. This adds texture and atmosphere evidence, while leaving personal scene suitability open to your judgment.</p>`:'';
 const bridge=connections.length?`This track earned credit for ${connections.map(c=>role(c)[0]).join(', ')}. Here is how those qualities could serve that reading of your prompt:`:genreOnly?'This selection is supported by the requested musical style. Style evidence alone does not tell us which social setting or personal occasion the track suits.':'The saved result does not contain enough scored mood or energy evidence to explain a connection to the scene. Passing the filters alone does not establish that connection.';
 return `<section class="iq-prompt-connection"><h4>How it connects to your prompt</h4><p class="iq-original-prompt">You asked for “${esc(prompt)}”.</p><p>${esc(description)}</p>${semanticConnection}${context.length?`<p class="muted">${context.map(([label,value])=>`${label}: ${esc(value)}`).join(' · ')}</p>`:''}<p>${esc(bridge)}</p>${connections.length?`<ul class="iq-scene-roles">${connections.map(c=>{const [quality,purpose]=role(c);return `<li><strong>${esc(quality)}</strong> could ${esc(purpose)}. ${c.origin==='inferred'?'The planner inferred this preference from the scene.':'This is a preference recorded from your request.'}</li>`;}).join('')}</ul>`:''}${inferred?'<p class="iq-scene-assumption"><strong>The assumption to check:</strong> these qualities are the planner’s interpretation of the occasion. Naming a place or activity does not, by itself, tell us your preferred energy or how the music should feel there.</p>':''}${plan?.assumptions?.length?`<details><summary>Assumptions behind this scene</summary><ul>${plan.assumptions.map(a=>`<li>${esc(a)}</li>`).join('')}</ul></details>`:''}<p class="iq-scene-limit"><strong>Where the connection can fail:</strong> ${calmReading?'two tracks can both be calm and happy yet suggest very different situations. The same broad mood can accompany an outdoor gathering or an intimate moment after a date.':'matching a mood or musical style does not establish that a track belongs in a particular setting.'} ${semantic?'The score cannot establish personal association, social chemistry or your acceptance of the scene.':'The current score does not directly measure that kind of scene fit, personal association or social chemistry.'} A high score for this interpretation can still produce the wrong track for your occasion.</p></section>`;
}
