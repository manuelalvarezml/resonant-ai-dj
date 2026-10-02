import {promptConnectionHTML} from './prompt-connection.js';
import {escapeHTML as esc} from './model.js';

const percent=value=>(value*100).toFixed(2);
const names={
 'semantic:scene':'the planned musical character',
 'mood:happy':'a happy mood','mood:sad':'a sad mood','mood:relaxed':'a relaxed mood','mood:aggressive':'an aggressive sound',
 'energy:low':'a lower-energy sound','energy:medium':'moderate energy','energy:high':'high energy',
 'danceability:danceable':'a danceable feel','vocals:vocal':'vocals','vocals:instrumental':'an instrumental sound',
};
export function descriptorName(tag){
 if(names[tag])return names[tag];
 const [axis,...rest]=String(tag).split(':');
 const label=rest.join(':').replaceAll('-',' ')||axis;
 return axis==='genre'?`${label} style`:label;
}
const lowerNames={'mood:happy':'less cheerfulness','mood:sad':'less sadness','mood:relaxed':'less relaxation','mood:aggressive':'less aggression','vocals:vocal':'fewer vocals','vocals:instrumental':'less instrumental character','danceability:danceable':'less emphasis on danceability'};
const target=c=>c.tags.map(tag=>c.direction==='decrease'?(lowerNames[tag]??`less emphasis on ${descriptorName(tag)}`):descriptorName(tag)).join(' or ');
const valid=c=>Array.isArray(c.tags)&&c.tags.length&&['increase','decrease'].includes(c.direction)&&[c.utility,c.weight,c.contribution].every(Number.isFinite)&&(c.evidence_value===null||Number.isFinite(c.evidence_value));
function sourceDescription(c){
 const source=c.source??'';
 if(source.includes('maest')){
  const label=source.match(/\[([^\]]+)\]/)?.[1]?.replaceAll('---',' / ');
  return `MAEST genre support${label?` for ${label}`:''}. This is an independent style estimate; genre values do not have to add up to 100%.`;
 }
 if(source.includes('deam-arousal'))return 'Energy fit derived from the arousal estimate on a 1–9 scale. Its conversion into low, medium and high energy is provisional.';
 if(source.includes('discogs-effnet'))return 'Audio-model estimate of mood, danceability or vocal character.';
 return source?`Evidence source: ${source}.`:'No usable audio evidence for this preference.';
}
function objectiveContext(c,query){
 const required=c.tags.some(t=>t.startsWith('genre:')&&query.required_tags?.includes(t))||query.any_tag_groups?.some(g=>g.length===c.tags.length&&g.every(t=>c.tags.includes(t)));
 if(required)return 'Required genre match';
 const pref=query.preferences?.find(p=>c.tags.includes(p.tag)&&p.direction===c.direction);
 return `${c.origin==='inferred'?'Inferred from your request':'Explicit preference'}${pref?.importance?` · ${pref.importance} priority`:''}`;
}
function contributionHTML(c,query){
 if(c.score_kind==='relative_similarity')return `<li class="iq-contribution"><div class="iq-contribution-heading"><strong>Musical character similarity</strong><b>+${percent(c.contribution)} points</b></div><p>The audio was compared with “${esc(query.semantic?.description??'the saved musical description')}”.</p><p>${esc(c.detail??'')}</p><p>${percent(c.utility)} / 100 relative rank × ${percent(c.weight)}% score weight = ${percent(c.contribution)} points.</p><p>A relative rank compares this library’s candidates. It does not mean the track has that mood with this probability, or that you will like it.</p></li>`;
 const fit=percent(c.utility),points=percent(c.contribution),weight=percent(c.weight);
 const explanation=c.evidence_value===null
  ? 'The analysis has no usable value for this preference. It earns zero points, including when the request asks for less of that quality.'
  : `The evidence value is ${percent(c.evidence_value)}/100. ${c.direction==='decrease'?`Lower values fit this preference: 100 − ${percent(c.evidence_value)} = ${fit}/100 preference fit.`:`Higher values fit this preference, giving ${fit}/100 preference fit.`}`;
 const quote=query.preferences?.find(p=>c.tags.includes(p.tag)&&p.direction===c.direction)?.source_span;
 return `<li class="iq-contribution"><div class="iq-contribution-heading"><strong>${esc(target(c))}</strong><b>+${points} points</b></div><p class="muted">${esc(objectiveContext(c,query))}${quote?` · From “${esc(quote)}”`:''}</p><p>${esc(explanation)}</p><p class="iq-equation">${fit}% fit × ${weight}% weight = <strong>${points} / 100 points</strong></p><p>It earned ${points} of the ${weight} points available for this preference.</p><p class="muted">${esc(sourceDescription(c))}${c.tags.length>1?' The best-supported alternative supplies this value; alternatives are not added together.':''}${query.genre_scope==='taxonomy'&&c.tags.some(t=>t.startsWith('genre:'))?' Broad genre families use the strongest matching style among the selected top six.':''}</p></li>`;
}
function eligibility(match,query){
 const facts=[];
 if(query.required_tags?.length)facts.push(`It meets the required ${query.required_tags.map(descriptorName).join(' and ')} criteria.`);
 for(const group of query.any_tag_groups??[])facts.push(`It matches at least one of: ${group.map(descriptorName).join(' or ')}.`);
 if(query.min_bpm!=null||query.max_bpm!=null){
  const bpm=match.track.bpm?.value;
  const range=query.min_bpm!=null&&query.max_bpm!=null?`${query.min_bpm}–${query.max_bpm} BPM`:query.min_bpm!=null?`at least ${query.min_bpm} BPM`:`at most ${query.max_bpm} BPM`;
  facts.push(`Its estimated tempo${Number.isFinite(bpm)?` of ${bpm.toFixed(1)} BPM`:''} satisfies your ${range} limit. Tempo filtering adds no score points.`);
 }
 if(query.excluded_tags?.length)facts.push(`It passes your exclusions (${query.excluded_tags.map(descriptorName).join(', ')}) using the catalog’s declared complete evidence. Passing exclusions adds no score points.`);
 return facts.length?`<div class="iq-eligibility"><h4>Why it qualified</h4>${facts.map(f=>`<p>${esc(f)}</p>`).join('')}</div>`:'';
}
export function matchExplanationHTML(match,run,index){
 const query=run.result?.query??run.translation?.query??{};
 const contributions=match.score_contributions??[];
 const connection=promptConnectionHTML(match,run);
 const supported=['maest-intent-v1','hybrid-semantic-v1'].includes(run.result?.ranking_version)&&contributions.length>0&&contributions.every(valid);
 const order=query.order??'relevance';
 const rank=Number.isInteger(index)?`Shown at #${index+1}${Number.isInteger(run.result?.eligible_count)?` among ${run.result.eligible_count} eligible tracks`:''}. `:'';
 const orderText=order==='relevance'?'Tracks are ordered by musical-fit score; equal scores use a stable track ID to break ties.':`Tracks are ordered by tempo, ${order==='bpm_ascending'?'slowest first':'fastest first'}. The fit score breaks ties at the same tempo, so a higher score can appear later.`;
 const raw=`<details class="iq-raw-reasons"><summary>Original scoring notes</summary><ul>${(match.reasons??[]).map(r=>`<li>${esc(r)}</li>`).join('')}</ul></details>`;
 if(!supported)return `<div class="iq-explanation">${connection}<p>This track passed the request’s eligibility checks. ${contributions.length?'A complete contribution breakdown is unavailable for this result.':'No weighted contribution breakdown was recorded for this result.'}</p>${eligibility(match,query)}<p>Recorded score: ${Number.isFinite(match.score)?match.score.toFixed(3):'unavailable'}. ${run.result?.ranking_version==='maest-intent-v1'&&!contributions.length&&match.score===0?'Without usable scoring objectives, eligible tracks tie and use stable track ID order unless tempo ordering was requested.':'The recorded result is preserved without inventing weighted points.'}</p><p>${esc(rank+orderText)}</p>${raw}</div>`;
 const sorted=[...contributions].sort((a,b)=>b.contribution-a.contribution);
 const positive=sorted.filter(c=>c.contribution>0);
 const strongest=positive.slice(0,2);
 let overview=strongest.length?`The score is driven mainly by the track’s match with ${strongest.map(target).join(' and ')}. ${strongest.length===1?'That preference adds':'Together, these preferences add'} ${percent(strongest.reduce((sum,c)=>sum+c.contribution,0))} points to this track’s score.`:'None of the scored preferences earned points for this track. It remains eligible because it passed the required filters.';
 const missing=contributions.filter(c=>c.evidence_value===null);
 if(missing.length)overview+=` Evidence is missing for ${missing.map(c=>c.tags.map(descriptorName).join(' or ')).join(', ')}, so those preferences add no points.`;
 const shortfall=[...contributions].filter(c=>c.evidence_value!==null&&c.weight-c.contribution>0.00005).sort((a,b)=>(b.weight-b.contribution)-(a.weight-a.contribution))[0];
 if(shortfall)overview+=` The largest unused share of the score is ${target(shortfall)}: it earns ${percent(shortfall.contribution)} of ${percent(shortfall.weight)} available points.`;
 const groups=['genre','preference','semantic'].map(group=>({group,weight:contributions.filter(c=>c.group===group).reduce((s,c)=>s+c.weight,0),points:contributions.filter(c=>c.group===group).reduce((s,c)=>s+c.contribution,0)})).filter(g=>g.weight>0);
 const allQueryTags=[...(query.required_tags??[]).filter(t=>t.startsWith('genre:')),...(query.any_tag_groups??[]).flat(),...(query.preferences??[]).map(p=>p.tag),...(query.preferred_tags??[])];
 const unscored=[...new Set(allQueryTags)].filter(t=>!contributions.some(c=>c.tags.includes(t)));
 const displayedSum=contributions.reduce((sum,c)=>sum+Number(percent(c.contribution)),0);
 const totalSign=Math.abs(displayedSum-Number(percent(match.score)))>0.005?'≈':'=';
 const weights=groups.map(g=>`${g.group==='genre'?'Requested genres':g.group==='semantic'?'Musical character similarity':'Other musical preferences'} have ${percent(g.weight)}% of the total weight and contribute ${percent(g.points)} points.`).join(' ');
 return `<div class="iq-explanation">${connection}<h4>What drove its score</h4><p class="iq-match-story">${esc(overview)}</p><p class="iq-score-total"><strong>Musical fit: ${percent(match.score)} / 100</strong></p><p>This score combines the audio evidence with the request’s priorities. It is not a ${percent(match.score)}% chance that you will like the track.</p><p>${esc(rank+orderText)}</p>${eligibility(match,query)}<h4>How the score adds up</h4><p>${esc(weights)} ${run.result?.ranking_version==='hybrid-semantic-v1'?'When structured evidence exists, it receives 70% of the score and semantic relative rank receives 30%; semantic-only requests use the latter alone. Within the structured branch, the existing genre/preference split is preserved.':groups.length===2?'The current weighting assigns 65% to explicit genre objectives and 35% to the other musical preferences.':'Only one scoring group has usable objectives, so it receives the full weight.'} These weighting choices are provisional. Weights are the share of the final score each preference can earn. Within each group, primary, secondary and optional priorities use relative weights of 3, 2 and 1.</p><ul class="iq-contributions">${contributions.map(c=>contributionHTML(c,query)).join('')}</ul><p class="iq-equation"><strong>${contributions.map(c=>percent(c.contribution)).join(' + ')} ${totalSign} ${percent(match.score)} / 100</strong></p><p class="muted">Displayed values are rounded; the ranking uses full-precision contributions before rounding the final score. Missing track evidence earns zero without redistributing its weight. Preferences with no usable evidence anywhere in the catalog are omitted from scoring.${unscored.length?` Not scored here: ${esc(unscored.map(descriptorName).join(', '))}.`:''}</p>${raw}</div>`;
}
