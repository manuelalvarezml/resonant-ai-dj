"""Behavioral checks for the twenty maintained prompts; never a listening verdict."""
def check_case(case_id, run):
    q=run.translation.query; prefs={p.tag:p for p in q.preferences};errors=[]
    def check(condition, explanation):
        if not condition:errors.append(explanation)
    def genre(tag,count):
        check(tag in q.required_tags,'Direct genre must remain required')
        check(q.limit==count,'Explicit count must be preserved')
    def soft():
        check(not q.required_tags and not q.excluded_tags and not q.any_tag_groups,'Creative context must not create hard tags')
        check(q.min_bpm is None and q.max_bpm is None,'Creative context must not invent BPM')
    def prefer(tag,direction='increase'):
        check(tag in prefs and prefs[tag].direction==direction,f'Expected {direction} {tag}')
    if case_id in {'P01','P02','P05','P07','P19'}:genre('genre:house',{'P01':10,'P02':8,'P05':8,'P07':6,'P19':5}[case_id])
    if case_id=='P03':genre('genre:rock',6)
    if case_id in {'P06','P08'}:
        genre('genre:reggaeton',6 if case_id=='P06' else 8);prefer('danceability:danceable')
    if case_id=='P06':prefer('energy:high')
    if case_id=='P08':prefer('mood:happy');prefer('mood:aggressive','decrease')
    if case_id=='P05':check(q.min_bpm==120 and q.max_bpm==128,'Preserve 120–128 BPM')
    if case_id=='P07':check('genre:techno' in q.excluded_tags,'Preserve no-techno exclusion')
    if case_id in {'P09','P10','P17'}:
        check(run.result is None and run.status in {'unsupported','needs_clarification'},'Unsupported hard requirement must stop retrieval')
    if case_id in {'P04','P11','P12','P13','P16','P18','P20'}:soft()
    if case_id in {'P04','P11','P16','P18','P20'}:prefer('mood:relaxed')
    if case_id=='P04':prefer('mood:happy')
    if case_id=='P12':prefer('danceability:danceable');prefer('energy:high')
    if case_id=='P13':prefer('mood:sad')
    if case_id=='P14':check(run.status=='needs_clarification' and run.result is None and bool(run.translation.plan.clarification),'Ask for recipient taste or mood')
    if case_id=='P15':check(['genre:rock','genre:pop'] in q.any_tag_groups or ['genre:pop','genre:rock'] in q.any_tag_groups,'Explicit rock/pop alternatives need OR');check(q.limit==8,'Preserve count 8')
    if case_id=='P16':prefer('mood:aggressive','decrease')
    if case_id=='P19':check(q.min_bpm==120 and q.max_bpm==130 and q.order=='bpm_ascending','Preserve explicit bounds and BPM order')
    if case_id=='P20':check(any(g.origin=='optional_preference' and not g.blocking for g in run.translation.plan.evidence_gaps),'Disclose unavailable optional familiarity')
    if run.result:
        matches=run.result.matches
        check(len(matches)<=q.limit,'Respect result limit')
        check(len({m.track.track_id for m in matches})==len(matches),'No duplicate track IDs')
        check(all(abs(m.score-sum(c.contribution for c in m.score_contributions))<.000001 for m in matches),'Contributions reproduce the score')
        if q.min_bpm is not None:check(all(m.track.bpm and m.track.bpm.value>=q.min_bpm for m in matches),'No tracks below BPM bound')
        if q.max_bpm is not None:check(all(m.track.bpm and m.track.bpm.value<=q.max_bpm for m in matches),'No tracks above BPM bound')
        if q.order=='relevance':check([m.score for m in matches]==sorted([m.score for m in matches],reverse=True),'Rank before truncation')
        if q.order=='bpm_ascending':check([m.track.bpm.value for m in matches]==sorted(m.track.bpm.value for m in matches),'Honor BPM ordering')
    return {'passed':not errors,'failures':errors,'scope':'contract/intent checks only; human listening pending'}
