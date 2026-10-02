"""Pure, replayable fusion. Cosines never masquerade as classifier probabilities."""
from .models import ScoreContribution

VERSION='hybrid-semantic-v1'
SEMANTIC_SHARE=.30
NEGATIVE_SHARE=.25


def fuse(matches, query):
    semantic=query.semantic
    if semantic is None:return False,[]
    if len(matches)<2:return False,['Semantic comparison needs at least two eligible tracks; structured scores retained.']
    if not semantic.embeddings:return False,['Semantic query was not encoded; structured scores retained.']
    if any(m.track.semantic_audio is None or m.track.semantic_audio.encoder_id!=semantic.encoder_id or m.track.semantic_audio.sampling_policy!='muq-3x10s-v1' for m in matches):
        return False,['Semantic coverage is incomplete or incompatible among eligible tracks; upgrade their analysis to enable fair comparison. Structured scores retained.']
    values=[];details=[]
    for match in matches:
        segments=match.track.semantic_audio.segments
        per_phrase=[[sum(a*b for a,b in zip(s.embedding, vector,strict=True)) for s in segments] for vector in semantic.embeddings]
        means=[sum(scores)/len(scores) for scores in per_phrase]
        negative=sum(means[1:])/len(means[1:]) if len(means)>1 else 0
        value=means[0]-NEGATIVE_SHARE*negative
        values.append(value);details.append((means[0],negative,min(per_phrase[0]),max(per_phrase[0])))
    has_structured=any(m.score_contributions for m in matches)
    share=SEMANTIC_SHARE if has_structured else 1.0
    for match,value,(positive,negative,minimum,maximum) in zip(matches,values,details,strict=True):
        lower=sum(v<value-1e-9 for v in values);equal=sum(abs(v-value)<=1e-9 for v in values)
        utility=(lower+.5*equal)/len(values)
        for c in match.score_contributions:
            c.weight*=1-share;c.contribution*=1-share
        detail=f'Compared with: {semantic.description} | mean cosine {positive:.4f}; sampled range {minimum:.4f}–{maximum:.4f}; negative mean {negative:.4f}, contrast coefficient {NEGATIVE_SHARE:g}. Relative rank among {len(matches)} eligible tracks: {utility:.4f}. These are similarities, not probabilities.'
        match.score_contributions.append(ScoreContribution(tags=['semantic:scene'],group='semantic',direction='increase',origin='inferred',evidence_value=value,utility=utility,weight=share,contribution=share*utility,source=semantic.encoder_id,score_kind='relative_similarity',detail=detail))
        match.score=round(min(1.0,sum(c.contribution for c in match.score_contributions)),6)
        match.reasons.append(detail)
    return True,['Semantic scores use a provisional relative-rank blend: 30% semantic / 70% structured when both exist; 100% semantic without structured objectives. Negative musical descriptions subtract 0.25 of their mean cosine. Similarities and ranks are not mood probabilities or listening acceptance.']


def gate_expanded_objectives(matches):
    """New heads must not favor just the upgraded subset of an eligible library."""
    expanded=('theme:','instrument:','valence:')
    unavailable={tuple(c.tags) for m in matches for c in m.score_contributions if any(t.startswith(expanded) for t in c.tags) and c.evidence_value is None}
    if not unavailable:return []
    removed={tag for tags in unavailable for tag in tags}
    for match in matches:
        match.score_contributions=[c for c in match.score_contributions if tuple(c.tags) not in unavailable]
        totals={group:sum(c.weight for c in match.score_contributions if c.group==group) for group in ('genre','preference')}
        blend={'genre':.65,'preference':.35} if all(totals.values()) else {g:float(v>0) for g,v in totals.items()}
        for c in match.score_contributions:c.weight=c.weight/totals[c.group]*blend[c.group];c.contribution=c.weight*c.utility
        match.score=round(sum(c.contribution for c in match.score_contributions),6)
        match.matched_tags=[t for t in match.matched_tags if t not in removed]
        match.missing_preferred_tags=[t for t in match.missing_preferred_tags if t not in removed]
    return ['No usable catalog evidence for soft scoring: incomplete eligible coverage for expanded objectives '+', '.join(sorted(removed))+'. Upgrade remaining tracks; these objectives are omitted for every candidate.']
