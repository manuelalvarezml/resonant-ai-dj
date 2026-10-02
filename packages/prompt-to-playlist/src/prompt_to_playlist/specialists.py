"""Quality-selected direct estimators. Explicit setup, offline sequential inference."""
from __future__ import annotations
import hashlib
import importlib.metadata
import json
import math
import os
import re
from pathlib import Path
import subprocess
import tempfile
from typing import Literal
from pydantic import Field, model_validator
from .models import StrictModel
from .model_assets import sha256_file
from .supervised import duration_of, windows

STAGES = ('vocal_musicnn', 'aggression_vggish', 'instrument_passt', 'key_sheetsage2')
OPENMIC_LABELS = ['accordion', 'banjo', 'bass', 'cello', 'clarinet', 'cymbals', 'drums', 'flute', 'guitar', 'mallet_percussion', 'mandolin', 'organ', 'piano', 'saxophone', 'synthesizer', 'trombone', 'trumpet', 'ukulele', 'violin', 'voice']
LABELS = {'vocal_musicnn':['instrumental','voice'], 'aggression_vggish':['aggressive','not_aggressive'], 'instrument_passt':OPENMIC_LABELS}
POLICY = 'specialists-three-excerpts-v1'


def model_dir():
    return Path(os.environ.get('PLAYLISTIQ_SPECIALIST_MODELS', Path(__file__).resolve().parents[2]/'output/top-estimators/models')).expanduser().resolve()


def manifest():
    return json.loads(Path(__file__).with_name('specialist_assets.json').read_text())


def stage_assets(stage):
    if stage not in STAGES: raise ValueError('Unknown specialist stage')
    return [x for x in manifest()['assets'] if stage in x['stages']]


def identity(stage):
    versions = {}
    for package in ('essentia-tensorflow','hear21passt','timm','torch','torchaudio','transformers','numpy'):
        try: versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError: versions[package] = 'not-installed'
    value = {'stage':stage,'assets':stage_assets(stage),'adapter':sha256_file(Path(__file__)), 'versions':versions}
    return stage+'-v1:'+hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def verify_assets(stage):
    root=model_dir()
    for item in stage_assets(stage):
        path=root/item['path']
        if not path.is_file() or path.stat().st_size!=item['size_bytes'] or sha256_file(path)!=item['sha256']:
            raise ValueError('Missing or changed specialist asset '+item['path']+'; run scripts/setup_specialists.py')
    return root


class SpecialistWindow(StrictModel):
    start_s: float = Field(ge=0,allow_inf_nan=False)
    end_s: float = Field(gt=0,allow_inf_nan=False)
    scores: dict[str,float]


class SpecialistEstimates(StrictModel):
    schema_version: Literal['specialist-estimates-v1']='specialist-estimates-v1'
    stage: Literal['vocal_musicnn','aggression_vggish','instrument_passt']
    model_id: str
    sampling_policy: Literal['specialists-three-excerpts-v1']=POLICY
    duration_s: float = Field(gt=0,allow_inf_nan=False)
    sampled_seconds: float = Field(gt=0,allow_inf_nan=False)
    coverage_fraction: float = Field(gt=0,le=1,allow_inf_nan=False)
    labels: list[str]
    scores: dict[str,float]
    segments: list[SpecialistWindow]=Field(min_length=1,max_length=9)
    score_kind: Literal['uncalibrated_classifier_support']='uncalibrated_classifier_support'

    @model_validator(mode='after')
    def valid(self):
        expected=LABELS[self.stage]
        if self.labels!=expected or set(self.scores)!=set(expected):raise ValueError('Specialist label mismatch')
        previous=0.
        for s in self.segments:
            if not previous<=s.start_s<s.end_s<=self.duration_s+1e-6 or set(s.scores)!=set(expected):raise ValueError('Invalid specialist coverage')
            if any(not math.isfinite(x) or not 0<=x<=1 for x in s.scores.values()):raise ValueError('Invalid specialist support')
            previous=s.end_s
        total=sum(s.end_s-s.start_s for s in self.segments)
        if abs(total-self.sampled_seconds)>1e-5 or abs(total/self.duration_s-self.coverage_fraction)>1e-6:raise ValueError('Specialist coverage mismatch')
        for k,x in self.scores.items():
            mean=sum(s.scores[k]*(s.end_s-s.start_s) for s in self.segments)/total
            if not math.isfinite(x) or not 0<=x<=1 or abs(x-mean)>1e-6:raise ValueError('Specialist aggregation mismatch')
        return self


def aggregate(stage,duration,segments):
    seconds=sum(s['end_s']-s['start_s'] for s in segments)
    return SpecialistEstimates(stage=stage,model_id=identity(stage),duration_s=duration,sampled_seconds=seconds,
        coverage_fraction=seconds/duration,labels=LABELS[stage],segments=segments,
        scores={k:sum(s['scores'][k]*(s['end_s']-s['start_s']) for s in segments)/seconds for k in LABELS[stage]}).model_dump(mode='json')


def result(stage,values,warnings=None):
    return dict(algorithm_id=stage,implementation=stage+'-v1',implementation_version='1.0.0',authority='benchmark_estimate',status='warning',values=values,
        warnings=warnings or ['Selected from published benchmarks; local listening superiority and probability calibration are unproven.'])


def waveform(path,start,end,sr):
    import numpy as np
    proc=subprocess.run(['ffmpeg','-v','error','-nostdin','-ss',str(start),'-i',str(path),'-t',str(end-start),'-ac','1','-ar',str(sr),'-f','f32le','pipe:1'],capture_output=True,check=True,timeout=120)
    x=np.frombuffer(proc.stdout,dtype='<f4').copy()
    if x.size<sr//2 or not np.isfinite(x).all():raise ValueError('Invalid decoded waveform')
    return x


def analyze_binary(path,stage):
    import essentia.standard as es
    import numpy as np
    root=verify_assets(stage);duration=duration_of(path)
    if stage=='vocal_musicnn':
        stem='voice_instrumental-msd-musicnn-1'
        encoder=es.TensorflowPredictMusiCNN(graphFilename=str(root/'msd-musicnn-1.pb'),output='model/dense/BiasAdd')
    else:
        stem='mood_aggressive-audioset-vggish-1'
        encoder=es.TensorflowPredictVGGish(graphFilename=str(root/'audioset-vggish-3.pb'),output='model/vggish/embeddings')
    meta=json.loads((root/(stem+'.json')).read_text())
    if meta['classes']!=LABELS[stage]:raise ValueError('Unexpected binary label order')
    head=es.TensorflowPredict2D(graphFilename=str(root/(stem+'.pb')),output=meta['schema']['outputs'][0]['name'])
    segments=[]
    for start,end in windows(duration):
        pred=np.asarray(head(encoder(waveform(path,start,end,16000))))
        if pred.ndim!=2 or pred.shape[1]!=2 or not len(pred):raise ValueError('Unexpected binary output shape')
        segments.append(dict(start_s=start,end_s=end,scores=dict(zip(LABELS[stage],map(float,pred.mean(axis=0))))))
    return result(stage,aggregate(stage,duration,segments))


def analyze_vocal(path,_):return analyze_binary(path,'vocal_musicnn')
def analyze_aggression(path,_):return analyze_binary(path,'aggression_vggish')


def analyze_instruments(path,_):
    import contextlib
    import io
    import torch
    from hear21passt.models.passt import get_model
    from hear21passt.models.preprocess import AugmentMelSTFT
    stage='instrument_passt';root=verify_assets(stage);duration=duration_of(path)
    # The upstream convenience wrapper uses an obsolete architecture alias and
    # downloads weights. Construct the released 20-class network explicitly.
    with contextlib.redirect_stdout(io.StringIO()):
        net=get_model(arch='openmic',pretrained=False,n_classes=20).eval()
        mel=AugmentMelSTFT(n_mels=128,sr=32000,win_length=800,hopsize=320,n_fft=1024,
                          freqm=0,timem=0,htk=False,fmin=0.,fmax=None,norm=1,fmin_aug_range=10,fmax_aug_range=2000).eval()
    state=torch.load(root/'openmic-passt.pt',map_location='cpu',weights_only=True)
    net.load_state_dict(state,strict=True)
    segments=[]
    with torch.inference_mode():
        for start,end in windows(duration):
            # Released OpenMIC model consumes ten-second clips. Average nine
            # real clip probabilities, never truncate a 30-second spectrogram.
            cursor=start
            while cursor<end-1e-6:
                stop=min(end,cursor+10)
                audio=torch.from_numpy(waveform(path,cursor,stop,32000))[None]
                if audio.shape[-1]<320000:audio=torch.nn.functional.pad(audio,(0,320000-audio.shape[-1]))
                logits,_=net(mel(audio)[:,None])
                scores=torch.sigmoid(logits)[0].tolist()
                segments.append(dict(start_s=cursor,end_s=stop,scores=dict(zip(OPENMIC_LABELS,scores))))
                cursor=stop
    return result(stage,aggregate(stage,duration,segments))


def analyze_key(path,_):
    import torch
    import sys
    stage='key_sheetsage2';root=verify_assets(stage)
    # The verified local source is the only remote-code source; no hub requests.
    sys.path.insert(0,str(root))
    from sheetsage.modeling_sheetsage2 import SheetSage2Model
    model=SheetSage2Model.from_pretrained(str(root/'sheetsage'),base_model_path=str(root/'mert-parent'),
          local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').eval()
    import soundfile as sf
    audio,rate=sf.read(str(path),dtype='float32',always_2d=True)
    # Preserve upstream channel averaging and Torchaudio resampling; SoundFile
    # replaces the removed torchaudio.info/load FFmpeg decoder API.
    with torch.inference_mode():
        output=model.transcribe(audio.T,sampling_rate=rate,prompts=['timestamp','key'],dtype='fp32',preset='paper')
    rows=[(float(a),float(b),key) for line in output.get('labs',{}).get('key','').splitlines() if line.strip() for a,b,key in [line.split(maxsplit=2)]]
    duration=duration_of(path)
    values=key_summary(rows,duration,identity(stage),output.get('warnings',[]))
    return result(stage,values,['Global key summarizes timed estimates and may hide modulation; benchmark performance is not local ground truth. SoundFile decoding replaces the removed upstream Torchaudio decoder.'])


def key_summary(rows,duration,model_id,warnings=None):
    if not rows:raise ValueError('SheetSage2 returned no valid key intervals')
    totals={}
    for start,end,key in rows:
        totals[key]=totals.get(key,0.)+end-start
    key=max(totals,key=totals.get)
    tonic,mode=key.split(':')
    sharp={'Db':'C#','Eb':'D#','Gb':'F#','Ab':'G#','Bb':'A#'}.get(tonic,tonic)
    circle=['C','G','D','A','E','B','F#','C#','G#','D#','A#','F'] if mode=='major' else ['A','E','B','F#','C#','G#','D#','A#','F','C','G','D']
    camelot=str((circle.index(sharp)+7)%12+1)+('B' if mode=='major' else 'A') if sharp in circle and mode in ('major','minor') else None
    return KeyEstimates(model_id=model_id,standard_key=tonic+' '+mode,tonic=tonic,mode=mode,camelot=camelot,
                        key_intervals=rows,duration_s=duration,runtime_warnings=warnings or []).model_dump(mode='json')


class KeyEstimates(StrictModel):
    model_id: str
    sampling_policy: Literal['sheetsage2-paper-whole-song-v1']='sheetsage2-paper-whole-song-v1'
    standard_key: str
    tonic: str
    mode: Literal['major','minor']
    camelot: str | None
    key_intervals: list[tuple[float,float,str]]=Field(min_length=1)
    duration_s: float=Field(gt=0,allow_inf_nan=False)
    aggregation: Literal['longest_total_key_duration']='longest_total_key_duration'
    runtime_warnings: list[str]=Field(default_factory=list)

    @model_validator(mode='after')
    def valid(self):
        previous=0.;totals={}
        for start,end,key in self.key_intervals:
            if not math.isfinite(start) or not math.isfinite(end) or not previous<=start<end<=self.duration_s+1e-3:raise ValueError('Invalid key intervals')
            if not re.fullmatch(r'[A-G](?:#|b)?:(major|minor)',key):raise ValueError('Invalid musical key')
            totals[key]=totals.get(key,0.)+end-start;previous=end
        chosen=max(totals,key=totals.get)
        if self.standard_key!=chosen.replace(':',' ') or chosen!=self.tonic+':'+self.mode:raise ValueError('Key aggregation mismatch')
        return self
