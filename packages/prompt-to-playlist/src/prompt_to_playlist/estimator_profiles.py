"""Conservative catalog-wide selection of uncalibrated supervised evidence."""
from .models import NumericEvidence
from .supervised import PROFILES as LEGACY_PROFILES, SampledEstimates
PROFILES = (*LEGACY_PROFILES, "quality")


def apply_profile(catalog, items, profile):
    if profile not in PROFILES:
        raise ValueError('Unknown estimator profile')
    if profile == 'quality':
        return apply_specialists(apply_profile(catalog, items, 'music2emo'), items)
    if profile == 'reference':
        return catalog
    catalog = catalog.model_copy(deep=True)
    catalog.catalog_id += '+estimators-' + profile + '-v1'
    catalog.warnings.append('Experimental estimator profile: ' + profile + '. No demonstrated listening superiority; ranking weights are unchanged.')
    by_id = {item['id']: item for item in items}
    for stage, kind in [('emotion_music2emo', 'music2emo'), ('danceability_musicnn', 'musicnn-dance')]:
        if profile not in (kind, 'supervised'):
            continue
        estimates = {}
        for track in catalog.tracks:
            result = next((a for a in by_id[track.track_id]['features']['algorithms'] if a['algorithm_id'] == stage and a['status'] in ('passed', 'warning')), None)
            try:
                value = SampledEstimates.model_validate(result['values']) if result else None
                if value and value.kind == kind:
                    estimates[track.track_id] = value
            except (KeyError, ValueError):
                pass
        identities = {v.model_id for v in estimates.values()}
        if not catalog.tracks or len(estimates) != len(catalog.tracks) or len(identities) != 1:
            catalog.warnings.append(f'{kind} coverage is {len(estimates)}/{len(catalog.tracks)} catalog candidates (one compatible model required); reference retained for everyone. Upgrade selected tracks explicitly.')
            continue
        # Each raw regression coordinate must be in its documented target scale.
        # An out-of-range value remains inspectable, never clipped into certainty.
        valid_va = {axis: all(1 <= getattr(v, axis+'_mean') <= 9 for v in estimates.values()) for axis in ('valence', 'arousal')} if kind == 'music2emo' else {}
        for track in catalog.tracks:
            value = estimates[track.track_id]
            source = value.model_id + '/' + value.sampling_policy
            def put(tag, score, meaning):
                track.preference_scores[tag] = NumericEvidence(value=float(score), authority='benchmark_estimate', source=source+'/'+meaning, status='warning')
            if kind == 'music2emo':
                for label, score in value.scores.items():
                    put('theme:'+label, score, 'jamendo-support')
                # Keep the four separate binary MTG mood targets. Jamendo's
                # "relaxing" is not silently substituted for MTG "relaxed".
                for axis, prefix, bands in [('valence', 'valence', ('positive', 'negative')), ('arousal', 'energy', ('high', 'low'))]:
                    if not valid_va[axis]:
                        continue
                    x = (getattr(value, axis+'_mean')-1)/8
                    put(prefix+':'+bands[0], x, axis+'-linear-preference-v1-unvalidated')
                    put(prefix+':'+bands[1], 1-x, axis+'-linear-preference-v1-unvalidated')
                    if axis == 'arousal':
                        put('energy:medium', 1-abs(2*x-1), 'arousal-triangular-preference-v1-unvalidated')
            else:
                put('danceability:danceable', value.scores['danceable'], 'binary-support')
        catalog.warnings.append(f'{kind} selected uniformly for {len(estimates)} catalog candidates; sampled support is not a calibrated probability.')
        for axis, valid in valid_va.items():
            if not valid:
                catalog.warnings.append(f'Music2Emo {axis} falls outside 1–9 for at least one candidate; reference {axis} retained for everyone, with raw output preserved.')
    return catalog


def apply_specialists(catalog, items):
    """Independent complete-coverage gate per target; never combine score scales."""
    from .specialists import SpecialistEstimates, LABELS, identity
    catalog.catalog_id = catalog.catalog_id.replace('+estimators-music2emo-v1', '+estimators-quality-v1')
    by_id = {item['id']: item for item in items}
    for stage in LABELS:
        estimates = {}
        for track in catalog.tracks:
            result = next((a for a in by_id[track.track_id]['features']['algorithms'] if a['algorithm_id']==stage and a['status'] in ('passed','warning')), None)
            try:
                value=SpecialistEstimates.model_validate(result['values']) if result else None
                if value and value.stage==stage and value.model_id==identity(stage):estimates[track.track_id]=value
            except (KeyError, ValueError):pass
        if not catalog.tracks or len(estimates)!=len(catalog.tracks):
            catalog.warnings.append(f'{stage} coverage is {len(estimates)}/{len(catalog.tracks)} candidates; reference retained for this feature for everyone, and unsupported new labels remain missing.')
            continue
        for track in catalog.tracks:
            value=estimates[track.track_id]
            if stage=='vocal_musicnn':mapping={'voice':'vocals:vocal','instrumental':'vocals:instrumental'}
            elif stage=='aggression_vggish':mapping={'aggressive':'mood:aggressive'}
            else:mapping={label:'openmic:'+label.replace('_','-') for label in value.labels}
            for label,tag in mapping.items():
                track.preference_scores[tag]=NumericEvidence(value=value.scores[label],authority='benchmark_estimate',source=value.model_id+'/'+value.sampling_policy,status='warning')
        catalog.warnings.append(f'{stage} selected uniformly for {len(estimates)} candidates; uncalibrated model support. Jamendo and OpenMIC targets remain separate.')
    catalog.warnings.append('Quality-selected profile retains reference EffNet happy/sad/relaxed/danceability and Beat This timing. Published ranking does not establish local listening superiority.')
    return catalog
