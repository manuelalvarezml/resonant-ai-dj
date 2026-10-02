"""Versioned MAEST top-six catalog bridge. Human reviews are never inputs."""
import json
from pathlib import Path
import math
import re
import unicodedata
from .models import Catalog, CatalogTrack, Descriptor, NumericEvidence, TagEvidence, Vocabulary, SemanticAudio
from .vocabulary import load_vocabulary
from .taxonomy import PARENTS, parent_tags, VERSION as TAXONOMY_VERSION

POLICY = 'maest-top6-v1'


def genre_tag(label):
    style = label.split('---')[-1]
    slug = re.sub('[^a-z0-9]+', '-', unicodedata.normalize('NFKD', style).encode('ascii','ignore').decode().lower()).strip('-')
    return 'genre:' + (slug if slug and slug[0].isalpha() else 'style-'+slug)


def top_genres(scores):
    if len(scores) != 519 or any(not isinstance(v,(int,float)) or not math.isfinite(v) or not 0 <= v <= 1 for v in scores.values()):
        raise ValueError('MAEST requires all 519 finite probabilities')
    return [{'genre':g,'probability':v} for g,v in sorted(scores.items(),key=lambda x:(-x[1],x[0]))[:6]]


def catalog_from_features(items, *, estimator_profile='reference'):
    vocabulary=load_vocabulary()
    descriptors={d.id:d for d in vocabulary.descriptors}
    for parent, (tag, aliases_list) in PARENTS.items():
        if tag not in descriptors:
            descriptors[tag] = Descriptor(id=tag, description=f'Discogs parent family: {parent}. Matches selected top-six descendants.', aliases=aliases_list)
    aliases={alias.casefold():d.id for d in descriptors.values() if d.id.startswith('genre:') for alias in [d.id,*d.aliases]}
    descriptors['mood:melancholic']=descriptors['mood:melancholic'].model_copy(update={'aliases':['melancholic']})
    for mood in ('happy','sad','relaxed','aggressive'):
        descriptors['mood:'+mood]=Descriptor(id='mood:'+mood,description=f'Continuous {mood} mood estimate; soft preference only.',aliases=[mood])
    descriptors['danceability:danceable']=Descriptor(id='danceability:danceable',description='Uncalibrated binary danceable-class support; not BPM or a continuous human groove rating; soft preference only.',aliases=['danceable'])
    extended=json.loads((Path(__file__).with_name('extended_labels.json')).read_text())
    for head,axis in [('moodtheme','theme'),('instrument','instrument')]:
        for label in extended[head]:
            tag=axis+':'+label
            descriptors[tag]=Descriptor(id=tag,description=f'Jamendo {axis} support for {label}; independent uncalibrated score, soft preference only.',aliases=[])
    for band in ('positive','negative'):
        descriptors['valence:'+band]=Descriptor(id='valence:'+band,description=f'{band.capitalize()} perceived musical valence from the selected estimator; provisional scale mapping, not personal feelings.',aliases=[])
    if estimator_profile == 'quality':
        from .specialists import OPENMIC_LABELS
        for label in OPENMIC_LABELS:
            tag='openmic:'+label.replace('_','-')
            descriptors[tag]=Descriptor(id=tag,description=f'PaSST OpenMIC {label.replace("_"," ")} support; independent taxonomy, uncalibrated, soft preference only. Do not interpret absent labels as negative evidence.',aliases=[])
    output=[]
    for item in items:
        feature=item['features']; indexed={a['algorithm_id']:a for a in feature['algorithms'] if a['status'] in ('passed','warning')}
        tags=[]
        maest=indexed.get('genre_maest')
        if maest:
            for g in top_genres(maest['values']['scores']):
                style=g['genre'].split('---')[-1]; tag=aliases.get(style.casefold(),genre_tag(g['genre']))
                if tag not in descriptors:
                    occupied={a.casefold() for d in descriptors.values() for a in [d.id,*d.aliases]}
                    alias=[style] if style.casefold() not in occupied else []
                    descriptors[tag]=Descriptor(id=tag,description=f'MAEST genre candidate: {style}',aliases=alias)
                    for a in alias:aliases[a.casefold()]=tag
                tags.append(TagEvidence(tag=tag,authority='benchmark_estimate',source=POLICY,status='warning',confidence=float(g['probability']),source_label=g['genre'],parent_tags=parent_tags(g['genre'])))
        rhythm=indexed.get('rhythm',{}).get('values',{})
        bpm=rhythm.get('bpm')
        scores={}
        heads=indexed.get('semantic',{}).get('values',{}).get('heads',{})
        for mood in ('happy','sad','relaxed','aggressive'):
            value=heads.get('mood_'+mood,{}).get('scores',{}).get(mood)
            tag='mood:'+mood
            if value is not None and tag in descriptors:
                scores[tag]=NumericEvidence(value=float(value),authority='benchmark_estimate',source='discogs-effnet/'+mood,status='warning')
        for head,label,tag in [('vocal_profile','voice','vocals:vocal'),('vocal_profile','instrumental','vocals:instrumental'),('danceability','danceable','danceability:danceable')]:
            value=heads.get(head,{}).get('scores',{}).get(label)
            if value is not None:scores[tag]=NumericEvidence(value=float(value),authority='benchmark_estimate',source='discogs-effnet/'+head,status='warning')
        for head,axis in [('mood_theme','theme'),('instruments','instrument')]:
            for label,value in heads.get(head,{}).get('scores',{}).items():
                tag=axis+':'+label
                if tag in descriptors and isinstance(value,(int,float)) and math.isfinite(value) and 0<=value<=1:
                    scores[tag]=NumericEvidence(value=float(value),authority='benchmark_estimate',source='discogs-effnet/jamendo-'+head,status='warning')
        energy=indexed.get('energy',{}).get('values',{})
        valence=energy.get('valence_mean',energy.get('valence_mean_deferred'))
        if valence is not None and 1<=valence<=9:
            x=(valence-1)/8
            for band,value in [('positive',x),('negative',1-x)]:
                scores['valence:'+band]=NumericEvidence(value=float(value),authority='benchmark_estimate',source='deam-valence-linear-preference-v1-unvalidated',status='warning')
        semantic_values=indexed.get('semantic_audio',{}).get('values',{})
        semantic_audio=None
        if semantic_values:
            try:semantic_audio=SemanticAudio.model_validate({k:semantic_values[k] for k in ('encoder_id','sampling_policy','segments')})
            except (KeyError,ValueError):pass
        arousal=indexed.get('energy',{}).get('values',{}).get('arousal_mean')
        if arousal is not None and 1<=arousal<=9:
            x=(arousal-1)/8
            for band,value in [('low',1-x),('medium',1-abs(2*x-1)),('high',x)]:
                scores['energy:'+band]=NumericEvidence(value=float(value),authority='benchmark_estimate',source='deam-arousal-linear-preference-v1-unvalidated',status='warning')
        output.append(CatalogTrack(track_id=item['id'],title=item['title'][:500],artist=(item.get('artist') or '')[:500] or None,
            tags=tags,preference_scores=scores,semantic_audio=semantic_audio,
            bpm=NumericEvidence(value=float(bpm),authority='benchmark_estimate',source='beat-this',status='warning') if bpm else None,
            duration_s=NumericEvidence(value=float(feature['duration_s']),authority='encoded_fact',source='ffprobe') if feature.get('duration_s') else None,
            warnings=['MAEST top-six candidates, no threshold; missing genre is not proof of absence.']))
    from .estimator_profiles import apply_profile
    catalog = apply_profile(Catalog(catalog_id=POLICY,tracks=output), items, estimator_profile)
    return catalog,Vocabulary(vocabulary_id=POLICY+"+"+TAXONOMY_VERSION+"+expanded-evidence-v1"+("+openmic-v1" if estimator_profile=="quality" else ""),descriptors=list(descriptors.values()))
