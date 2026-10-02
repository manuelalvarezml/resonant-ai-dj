"""Selectable supervised challengers. No downloads and no implicit promotion."""
from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from .models import StrictModel
from .model_assets import sha256_file

POLICY = 'supervised-3x30s-v1'
IMPLEMENTATION = 'music2emo-j-all-modefix-v1'
STAGES = ('emotion_music2emo', 'danceability_musicnn', 'estimator_reference')
PROFILES = ('reference', 'music2emo', 'musicnn-dance', 'supervised')
MOOD_LABELS = json.loads(Path(__file__).with_name('extended_labels.json').read_text())['moodtheme']


def model_dir():
    return Path(os.environ.get('PLAYLISTIQ_SUPERVISED_MODELS', Path(__file__).resolve().parents[2] / 'output/supervised-models')).expanduser().resolve()


def manifest():
    return json.loads(Path(__file__).with_name('supervised_assets.json').read_text())


def identity():
    # Adapter and package dependency lock are part of the cache, not only weights.
    files = [Path(__file__), *sorted(Path(__file__).with_name('_music2emo').glob('*.py'))]
    data = {'assets': manifest(), 'policy': POLICY,
            'code': {p.name: sha256_file(p) for p in files}}
    return IMPLEMENTATION + ':' + hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def verify_assets():
    root = model_dir()
    for item in manifest()['assets']:
        path = root / item['path']
        if not path.is_file() or path.stat().st_size != item['size_bytes'] or sha256_file(path) != item['sha256']:
            raise ValueError('Supervised model asset missing or changed: ' + item['path'] + '. Run scripts/setup_supervised.py.')
    return root


def windows(duration):
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Audio duration must be positive and finite')
    if duration < 1:
        raise ValueError('Supervised estimators require at least one second of audio')
    count = min(3, max(1, int(duration // 30)))
    length = min(30.0, duration)
    if count == 1:
        return [((duration-length)/2, (duration+length)/2)]
    return [(i*(duration-length)/(count-1), i*(duration-length)/(count-1)+length) for i in range(count)]


class EstimateWindow(StrictModel):
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    scores: dict[str, float]
    valence: float | None = None
    arousal: float | None = None
    detected_key: str | None = None
    detected_mode: str | None = None
    encoded_mode: int | None = Field(default=None, ge=0, le=1)
    chord_events: int | None = Field(default=None, ge=0)

    @model_validator(mode='after')
    def valid(self):
        if self.end_s <= self.start_s or any(not 0 <= x <= 1 for x in self.scores.values()):
            raise ValueError('Invalid excerpt or classifier support')
        return self


class SampledEstimates(StrictModel):
    schema_version: Literal['supervised-estimates-v1'] = 'supervised-estimates-v1'
    model_id: str
    sampling_policy: Literal['supervised-3x30s-v1'] = POLICY
    kind: Literal['music2emo', 'musicnn-dance']
    duration_s: float = Field(gt=0)
    sampled_seconds: float = Field(gt=0)
    coverage_fraction: float = Field(gt=0, le=1)
    labels: list[str]
    scores: dict[str, float]
    valence_mean: float | None = None
    arousal_mean: float | None = None
    segments: list[EstimateWindow] = Field(min_length=1, max_length=3)
    score_kind: Literal['uncalibrated_classifier_support'] = 'uncalibrated_classifier_support'
    regression_units: Literal['raw_1_to_9_unclipped'] = 'raw_1_to_9_unclipped'
    aggregation: Literal['duration_weighted_mean_of_excerpt_outputs'] = 'duration_weighted_mean_of_excerpt_outputs'

    @model_validator(mode='after')
    def valid(self):
        expected = MOOD_LABELS if self.kind == 'music2emo' else ['danceable', 'not_danceable']
        if self.labels != expected or set(self.scores) != set(expected):
            raise ValueError('Exact supervised label order/set required')
        previous = 0.0
        for s in self.segments:
            if s.start_s < previous - 1e-6 or s.end_s > self.duration_s + 1e-6 or set(s.scores) != set(expected):
                raise ValueError('Invalid supervised coverage or labels')
            previous = s.end_s
            if self.kind == 'music2emo' and (s.valence is None or s.arousal is None):
                raise ValueError('Music2Emo requires both raw regression values')
        seconds = sum(s.end_s-s.start_s for s in self.segments)
        if abs(seconds-self.sampled_seconds) > 1e-5 or abs(seconds/self.duration_s-self.coverage_fraction) > 1e-6:
            raise ValueError('Supervised sampled coverage mismatch')
        for label, score in self.scores.items():
            mean = sum(s.scores[label]*(s.end_s-s.start_s) for s in self.segments)/seconds
            if not 0 <= score <= 1 or abs(mean-score) > 1e-6:
                raise ValueError('Supervised score aggregation mismatch')
        for field in ('valence', 'arousal'):
            mean = getattr(self, field+'_mean')
            if self.kind == 'music2emo':
                expected_mean = sum(getattr(s, field)*(s.end_s-s.start_s) for s in self.segments)/seconds
                if mean is None or abs(mean-expected_mean) > 1e-6:
                    raise ValueError('Regression aggregation mismatch')
            elif mean is not None or any(getattr(s, field) is not None for s in self.segments):
                raise ValueError('Danceability must not supply emotion regression')
        return self


def aggregate(kind, duration, segments):
    seconds = sum(s['end_s']-s['start_s'] for s in segments)
    labels = MOOD_LABELS if kind == 'music2emo' else ['danceable', 'not_danceable']
    def mean(key, label=None):
        return sum((s[key][label] if label else s[key])*(s['end_s']-s['start_s']) for s in segments)/seconds
    return SampledEstimates.model_validate(dict(
        kind=kind, model_id=identity(), duration_s=duration, sampled_seconds=seconds,
        coverage_fraction=seconds/duration, labels=labels,
        scores={label: mean('scores', label) for label in labels},
        valence_mean=mean('valence') if kind == 'music2emo' else None,
        arousal_mean=mean('arousal') if kind == 'music2emo' else None, segments=segments,
    )).model_dump(mode='json')


def duration_of(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(path)], capture_output=True, check=True, timeout=20)
    return float(json.loads(result.stdout)['format']['duration'])


def decode_excerpt(source, target, start, end):
    subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-i', str(source), '-ss', str(start), '-t', str(end-start), '-ac', '1', '-ar', '24000', '-c:a', 'pcm_f32le', str(target)], check=True, capture_output=True, timeout=60)


def analyze_music2emo(path, _):
    import torch
    from ._music2emo.runtime import create_runtime
    assets = verify_assets()
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '4')))
    torch.manual_seed(0)
    runtime = create_runtime(assets)
    duration = duration_of(path)
    segments = []
    with tempfile.TemporaryDirectory(prefix='playlistiq-music2emo-') as temp:
        root = Path(temp)
        for i, (start, end) in enumerate(windows(duration)):
            clip = root / f'{i}.wav'
            decode_excerpt(path, clip, start, end)
            with torch.inference_mode():
                result = runtime._predict(str(clip), root / str(i))
            segments.append(dict(start_s=start, end_s=end, **result))
    return dict(algorithm_id='emotion_music2emo', implementation=IMPLEMENTATION, implementation_version='1.0.0',
                authority='benchmark_estimate', status='warning', values=aggregate('music2emo', duration, segments),
                warnings=['Experimental supervised model; listening superiority and calibration are unproven.',
                          'Sampled expressed musical emotion, not listener-induced emotion. Raw regression may exceed 1–9; invalid-scale values are not projected.',
                          'Uses J_all released checkpoint, corrected key mode, and sampled excerpt aggregation; not the published benchmark protocol.'])


def analyze_danceability(path, _):
    import essentia.standard as es
    from .analysis_worker import _head_predictions
    from .model_assets import default_model_dir
    assets = verify_assets()
    # Reuse the already pinned backbone; setup copies it into the experiment assets.
    backbone = assets / 'msd-musicnn-1.pb'
    if not backbone.exists():
        raise ValueError('Run scripts/setup_supervised.py for the MusiCNN backbone')
    duration = duration_of(path)
    segments = []
    predictor = es.TensorflowPredictMusiCNN(graphFilename=str(backbone), output='model/dense/BiasAdd')
    with tempfile.TemporaryDirectory(prefix='playlistiq-danceability-') as temp:
        for i, (start, end) in enumerate(windows(duration)):
            clip = Path(temp) / f'{i}.wav'
            decode_excerpt(path, clip, start, end)
            audio = es.MonoLoader(filename=str(clip), sampleRate=16000, resampleQuality=4)()
            scores = _head_predictions(predictor(audio), assets, 'danceability-msd-musicnn-1')['scores']
            segments.append(dict(start_s=start, end_s=end, scores=scores))
    return dict(algorithm_id='danceability_musicnn', implementation='musicnn-danceability-3x30s-v1', implementation_version='1.0.0',
                authority='benchmark_estimate', status='warning', values=aggregate('musicnn-dance', duration, segments),
                warnings=['Experimental binary danceability support, not a continuous human groove rating, tempo, or calibrated probability.'])


def analyze_reference(path, assets):
    from .analysis_worker import analyze_semantic, analyze_energy
    duration = duration_of(path)
    segments = []
    with tempfile.TemporaryDirectory(prefix='playlistiq-reference-') as temp:
        for i, (start, end) in enumerate(windows(duration)):
            clip = Path(temp) / f'{i}.wav'
            decode_excerpt(path, clip, start, end)
            segments.append(dict(start_s=start, end_s=end, semantic=analyze_semantic(clip, assets)['values'], energy=analyze_energy(clip, assets)['values']))
    return dict(algorithm_id='estimator_reference', implementation='effnet-deam-matched-3x30s-v1', implementation_version='1.0.0',
                authority='benchmark_estimate', status='warning', values=dict(sampling_policy=POLICY, duration_s=duration, segments=segments),
                warnings=['Matched excerpt reference for comparisons only; production reference is preserved.'])
