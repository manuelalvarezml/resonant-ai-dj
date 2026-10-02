import json
import pytest
from prompt_to_playlist.models import *
from prompt_to_playlist.intent import compile_plan, capabilities, plan_schema
from prompt_to_playlist.search import search_tracks
from prompt_to_playlist.service import build_playlist
from prompt_to_playlist.translators import OpenAITranslator


def vocab():
    return Vocabulary(vocabulary_id='intent-test',descriptors=[Descriptor(id=t,description=t) for t in ['genre:house','genre:rock','genre:pop','genre:indie','mood:happy','mood:sad','mood:aggressive']])

def plan(**updates):
    return IntentPlan(**(dict(disposition='ready',interpretation='A relaxed mix',occasion=None,activity=None,recipient=None,emotional_goal=None,constraints=[],bpm=None,preferences=[],count=10,count_source=None,order='relevance',order_source=None,excluded_track_ids=[],assumptions=[],evidence_gaps=[],clarification=None)|updates))

def track(id,genre='genre:house',score=.5,mood=None,parent=None):
    return CatalogTrack(track_id=id,title=id,tags=[TagEvidence(tag=genre,authority='benchmark_estimate',source='maest-top6-v1',confidence=score,parent_tags=parent or [])],preference_scores={} if mood is None else {'mood:happy':NumericEvidence(value=mood,authority='benchmark_estimate',source='happy-head')})

def catalog(*tracks):return Catalog(catalog_id='test',tracks=list(tracks))


def test_required_genre_ranks_probability_before_limit_and_preserves_legacy():
    c=catalog(track('a',score=.01),track('z',score=.9));q=PlaylistQuery(required_tags=['genre:house'],limit=1)
    r=search_tracks(c,q,vocab())
    assert r.matches[0].track.track_id=='z' and r.matches[0].score==.9
    assert r.matches[0].score_contributions[0].evidence_value==.9
    assert r.eligible_track_ids==['z','a']
    assert search_tracks(c,q,vocab(),ranking_version='legacy').matches[0].track.track_id=='a'
    assert r.result_id==search_tracks(c,q,vocab()).result_id


def test_genre_feature_blend():
    c=catalog(track('a',score=.8,mood=.2),track('b',score=.2,mood=.9))
    q=PlaylistQuery(required_tags=['genre:house'],preferences=[Preference(tag='mood:happy',importance='primary')])
    r=search_tracks(c,q,vocab())
    assert r.matches[0].score==pytest.approx(.65*.8+.35*.2)
    assert sum(x.weight for x in r.matches[0].score_contributions)==1


def test_decrease_missing_is_not_low_and_globally_missing_reported():
    c=catalog(track('unknown'),track('known',mood=.1))
    q=PlaylistQuery(preferences=[Preference(tag='mood:happy',direction='decrease'),Preference(tag='mood:sad')])
    r=search_tracks(c,q,vocab())
    assert r.matches[0].track.track_id=='known' and r.matches[0].score==.9
    assert r.matches[1].score==0 and r.matches[1].score_contributions[0].evidence_value is None
    assert any('mood:sad' in w for w in r.warnings)


def test_or_parent_max_no_sum():
    a=track('a','genre:indie',.6,parent=['genre:rock'])
    a.tags.append(TagEvidence(tag='genre:rock',authority='benchmark_estimate',source='maest-top6-v1',confidence=.4))
    c=catalog(a,track('b','genre:pop',.7),track('c'))
    r=search_tracks(c,PlaylistQuery(any_tag_groups=[['genre:rock','genre:pop']],genre_scope='taxonomy'),vocab())
    assert [m.track.track_id for m in r.matches]==['b','a'] and r.matches[1].score==.6
    assert not search_tracks(c,PlaylistQuery(required_tags=['genre:rock','genre:pop']),vocab()).matches


def test_strict_negative_and_failed_scores():
    a=track('a',mood=.9);a.preference_scores['mood:happy'].status='failed'
    r=search_tracks(catalog(a),PlaylistQuery(excluded_tags=['genre:rock'],genre_scope='taxonomy'),vocab())
    assert not r.matches and any('negative-tag' in w for w in r.warnings)
    a.complete_tag_axes=['genre']
    assert search_tracks(catalog(a),PlaylistQuery(excluded_tags=['genre:rock'],genre_scope='taxonomy'),vocab()).matches
    assert search_tracks(catalog(a),PlaylistQuery(preferences=[Preference(tag='mood:happy')]),vocab()).matches[0].score==0


def test_bpm_order_precedes_limit():
    a,b=track('a',score=.9),track('b',score=.1)
    for t,bpm in [(a,128.),(b,122.)]:t.bpm=NumericEvidence(value=bpm,authority='benchmark_estimate',source='beat-this')
    r=search_tracks(catalog(a,b),PlaylistQuery(required_tags=['genre:house'],min_bpm=120.,max_bpm=130.,order='bpm_ascending',limit=1),vocab())
    assert r.matches[0].track.track_id=='b'


def test_creative_soft_context():
    p=plan(preferences=[Preference(tag='mood:happy',origin='inferred',source_span='picnic')],assumptions=['A cheerful atmosphere.'])
    t=compile_plan('A picnic with my girlfriend',p,vocab(),model='test')
    assert not t.query.required_tags and t.query.min_bpm is None and t.compiler_version=='intent-compiler-v1.2'


@pytest.mark.parametrize('update',[
    {'constraints':[TagConstraint(mode='all',tags=['genre:house'],source_span='house')]},
    {'count':5},{'order':'bpm_ascending'},{'preferences':[Preference(tag='mood:happy',origin='explicit')]},
    {'excluded_track_ids':['invented-id']},
    {'evidence_gaps':[EvidenceGap(concept='lyrics',origin='explicit_requirement',blocking=True,explanation='No lyrics')]},
    {'evidence_gaps':[EvidenceGap(concept='lyrics',origin='explicit_requirement',blocking=False,explanation='No lyrics')]},
])
def test_reject_unanchored_or_dropped_requirements(update):
    with pytest.raises(ValueError):compile_plan('A picnic',plan(**update),vocab(),model='test')


def test_answer_source_not_question():
    p=plan(constraints=[TagConstraint(mode='all',tags=['genre:rock'],source_span='rock')])
    answer=ClarificationAnswer(question='Does she like rock?',answer='She likes pop')
    with pytest.raises(ValueError):compile_plan('Music for mom',p,vocab(),model='test',clarifications=[answer])
    answer.answer='She likes rock'
    assert compile_plan('Music for mom',p,vocab(),model='test',clarifications=[answer]).query.required_tags==['genre:rock']


def test_capabilities_aggregate_only():
    result=capabilities(catalog(track('secret-id','genre:indie',parent=['genre:rock'])))
    assert result['descriptor_track_counts']['genre:rock']==1 and 'secret-id' not in json.dumps(result)


def test_schema_strict_shared_enum():
    schema=plan_schema(vocab())
    def walk(v):
        if isinstance(v,dict):
            assert 'default' not in v
            if v.get('type')=='object':assert v['additionalProperties'] is False and set(v['required'])==set(v['properties'])
            for item in v.values():walk(item)
        if isinstance(v,list):
            for item in v:walk(item)
    walk(schema)
    assert schema['$defs']['Preference']['properties']['tag']=={'$ref':'#/$defs/AllowedTag'}


def test_preference_schema_uses_available_evidence_but_preserves_explicit_constraints():
    schema=plan_schema(vocab(),{'descriptor_track_counts':{'mood:happy':2}})
    assert schema['$defs']['AvailablePreferenceTag']['enum']==['mood:happy']
    assert schema['$defs']['Preference']['properties']['tag']=={'$ref':'#/$defs/AvailablePreferenceTag'}
    assert 'mood:sad' in schema['$defs']['AllowedTag']['enum']
    assert schema['$defs']['TagConstraint']['properties']['tags']['items']=={'$ref':'#/$defs/AllowedTag'}
    empty=plan_schema(vocab(),{'descriptor_track_counts':{}})
    assert empty['properties']['preferences']['maxItems']==0


def test_planner_rejects_unavailable_soft_evidence_locally(monkeypatch):
    from prompt_to_playlist.translators import TranslationError
    p=plan(preferences=[Preference(tag='mood:sad')])
    provider=OpenAITranslator(api_key='test',model='test')
    monkeypatch.setattr(OpenAITranslator,'_request',lambda *args:{'status':'completed','output':[{'type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':p.model_dump_json()}]}]})
    with pytest.raises(TranslationError,match='local validation'):
        provider.translate_intent('A reflective evening',vocab(),{'descriptor_track_counts':{'mood:happy':2}})


@pytest.mark.parametrize('disposition',['needs_clarification','unsupported','partial_support'])
def test_service_dispositions(disposition):
    p=plan(disposition=disposition,clarification='What mood does she enjoy?' if disposition=='needs_clarification' else None)
    class Translator:
        def translate_intent(self,prompt,vocabulary,caps,answers):return compile_plan(prompt,p,vocabulary,model='test',clarifications=answers)
    r=build_playlist('Music for mom',catalog(track('a')),vocab(),Translator())
    assert r.status==disposition and (r.result is None)==(disposition!='partial_support')


def test_openai_one_call_no_tools_answer_roundtrip(monkeypatch):
    import prompt_to_playlist.translators as module
    p=plan(constraints=[TagConstraint(mode='all',tags=['genre:rock'],source_span='rock')]);payloads=[]
    class Response:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,n):return json.dumps({'status':'completed','output':[{'type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':p.model_dump_json()}]}]}).encode()
    def call(request,timeout):payloads.append(json.loads(request.data));return Response()
    monkeypatch.setattr(module,'urlopen',call)
    r=build_playlist('Music for mom',catalog(track('private-name','genre:rock')),vocab(),OpenAITranslator(api_key='secret',model='test',intent_reasoning_effort='low'),clarifications=[ClarificationAnswer(question='Her taste?',answer='rock')])
    assert r.status=='matched' and len(payloads)==1 and 'tools' not in payloads[0]
    assert 'private-name' not in json.dumps(payloads[0]) and r.translation.request_text=='Music for mom'
    assert r.translation.clarifications[0].answer=='rock'
    assert payloads[0]['reasoning']=={'effort':'low'} and r.translation.reasoning_effort=='low'


def test_no_invented_bpm_even_with_real_context_quote():
    with pytest.raises(ValueError,match='numerically'):
        compile_plan('picnic',plan(bpm=BPMConstraint(minimum=100.,maximum=120.,source_span='picnic')),vocab(),model='test')


def test_schema_migration_reads_legacy_and_writes_new():
    assert Catalog.model_validate({'schema_version':'0.1.0','catalog_id':'old','tracks':[]}).schema_version=='0.1.0'
    assert catalog().schema_version=='0.3.0'
    assert search_tracks(catalog(track('a')),PlaylistQuery(),vocab()).schema_version=='0.3.0'


def test_priority_ratios_and_parent_exclusion():
    a=track('a','genre:indie',.6,mood=.8,parent=['genre:rock'])
    a.preference_scores['mood:sad']=NumericEvidence(value=.3,authority='benchmark_estimate',source='sad')
    q=PlaylistQuery(preferences=[Preference(tag='mood:happy',importance='primary'),Preference(tag='mood:sad',importance='optional')])
    assert search_tracks(catalog(a),q,vocab()).matches[0].score==.675
    a.complete_tag_axes=['genre']
    assert not search_tracks(catalog(a),PlaylistQuery(excluded_tags=['genre:rock'],genre_scope='taxonomy'),vocab()).matches


def test_paraphrased_inference_loses_quote_but_not_soft_intent():
    p=plan(preferences=[Preference(tag='mood:happy',origin='inferred',source_span='picnic with partner')])
    t=compile_plan('a picnic with my partner',p,vocab(),model='test')
    assert t.query.preferences[0].source_span is None
    assert t.query.preferences[0].origin=='inferred' and t.warnings


def test_blank_clarification_is_rejected():
    with pytest.raises(ValueError):ClarificationAnswer(question='?',answer=' ')


def test_duplicate_soft_preferences_do_not_multiply_score_or_promote_inference():
    p=plan(preferences=[Preference(tag='mood:happy',importance='optional',source_span='happy'),Preference(tag='mood:happy',importance='primary',origin='inferred')])
    t=compile_plan('prefer happy',p,vocab(),model='test')
    assert len(t.query.preferences)==1 and t.query.preferences[0].importance=='optional'
    assert len(t.proposed_plan.preferences)==2 and len(t.plan.preferences)==1
    assert t.warnings
    p.preferences[1].direction='decrease'
    with pytest.raises(ValueError,match='Conflicting'):
        compile_plan('prefer happy',p,vocab(),model='test')
