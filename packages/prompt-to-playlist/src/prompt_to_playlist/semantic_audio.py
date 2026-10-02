"""Pinned offline MuQ-MuLan inference. Imported lazily in bounded workers only."""
from __future__ import annotations
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

MODEL_ID = 'OpenMuQ/MuQ-MuLan-large@2e01c796b71dca71b45251384c04cd7b237c9020'
POLICY = 'muq-3x10s-v1'
ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT/'output/semantic-models'
_BANK_DATA = json.loads(Path(__file__).with_name('character_bank.json').read_text())
BANK_VERSION = _BANK_DATA['version']
CONCEPTS = _BANK_DATA['concepts']
BANK = {c['id']:c['description'] for c in CONCEPTS}
BANK_DIGEST = hashlib.sha256(json.dumps(_BANK_DATA,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def bank_identity():
    return BANK_VERSION + '#' + BANK_DIGEST


def model_manifest(root=MODEL_DIR, *, verify=False):
    from .model_assets import sha256_file
    path=root/'manifest.json'
    if not path.is_file():raise ValueError('Semantic model setup is missing. Run scripts/setup_semantic.py once.')
    manifest=json.loads(path.read_text())
    if manifest.get('model_id')+'@'+manifest.get('revision','') != MODEL_ID:raise ValueError('Incompatible semantic model manifest')
    for item in manifest['assets']:
        file=root/item['path']
        if not file.is_file() or file.stat().st_size!=item['size_bytes']:raise ValueError('Missing or incomplete semantic asset: '+item['path'])
        if verify and sha256_file(file)!=item['sha256']:raise ValueError('Semantic asset hash mismatch: '+item['path'])
    return manifest


def identity():
    manifest=model_manifest()
    encoded=json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()
    return MODEL_ID+'#'+hashlib.sha256(encoded).hexdigest()


def load_model(root=MODEL_DIR):
    # No nested pretrained downloads: instantiate from pinned configs, then load
    # the COMPLETE official MuLan state dictionary with strict key validation.
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    os.environ['TOKENIZERS_PARALLELISM']='false'
    model_manifest(root,verify=True)
    import torch
    from muq import MuQ, MuQMuLan
    from muq.muq_mulan.models.audio import AudioSpectrogramTransformerPretrained
    from muq.muq_mulan.models.text import TextTransformerPretrained
    from muq.muq_mulan.models.mulan import MuLanModel
    from transformers import XLMRobertaConfig, XLMRobertaModel, AutoTokenizer
    torch.set_num_threads(int(os.environ.get('PLAYLISTIQ_CPU_THREADS','4')))
    class LocalAudio(AudioSpectrogramTransformerPretrained):
        def _init_pretrained_model(self, model_name):
            self.model=MuQ(json.loads((root/'muq/config.json').read_text()))
    class LocalText(TextTransformerPretrained):
        def _init_pretrained_model(self):
            return XLMRobertaModel(XLMRobertaConfig.from_dict(json.loads((root/'xlm-roberta/config.json').read_text())))
        def _init_tokenizer(self):
            return AutoTokenizer.from_pretrained(str(root/'xlm-roberta'),local_files_only=True,trust_remote_code=False)
    class LocalMuLan(MuQMuLan):
        @classmethod
        def create_MuLan_from_config(cls, config, hf_hub_cache_dir=None):
            audio=LocalAudio(model_name=config.audio_model.name,model_dim=config.audio_model.model_dim,use_layer_idx=config.audio_model.use_layer_idx,**config.audio_transformer,frozen_pretrained=False)
            text=LocalText(model_name=config.text_model.name,model_dim=config.text_model.model_dim,**config.text_transformer,frozen_pretrained=False)
            return MuLanModel(audio_transformer=audio,text_transformer=text,**config.mulan)
    model=LocalMuLan(json.loads((root/'mulan/config.json').read_text()))
    state=torch.load(root/'mulan/pytorch_model.bin',map_location='cpu',weights_only=True,mmap=True)
    model.load_state_dict(state,strict=True,assign=True)
    return model.eval().float()


def normalized(vector):
    values=[float(x) for x in vector]
    norm=math.sqrt(sum(x*x for x in values))
    if len(values)!=512 or not all(math.isfinite(x) for x in values) or norm<1e-8:raise ValueError('Invalid semantic embedding')
    return [x/norm for x in values]


def text_embeddings(texts,model=None,*,cached_only=False):
    """One sentence per forward pass avoids padding changing upstream mean pooling."""
    encoder=identity();cache=ROOT/'output/semantic-text-cache';cache.mkdir(parents=True,exist_ok=True)
    result=[]
    for text in texts:
        if not isinstance(text,str) or not text.strip() or len(text)>500:raise ValueError('Semantic descriptions require 1–500 characters')
        key=hashlib.sha256((encoder+'\n'+text).encode()).hexdigest();path=cache/(key+'.json')
        if path.exists():
            cached=json.loads(path.read_text())
            if cached.get('encoder')!=encoder or cached.get('text')!=text:raise ValueError('Incompatible text embedding cache')
            vector=normalized(cached['embedding'])
        else:
            if cached_only:raise ValueError("Description text cache is missing. Run scripts/prepare_character_bank.py.")
            import torch
            if model is None:model=load_model()
            with torch.inference_mode():vector=normalized(model(texts=[text])[0].tolist())
            temp=path.with_suffix(f'.{os.getpid()}.tmp');temp.write_text(json.dumps({'text':text,'encoder':encoder,'embedding':vector},allow_nan=False));temp.replace(path)
        result.append(vector)
    return result


def segment_starts(duration):
    if not math.isfinite(duration) or duration<=0:raise ValueError('Audio duration must be positive')
    return sorted(set(round(min(max(0,duration*f-5),max(0,duration-10)),3) for f in (.15,.5,.85)))


def covered_seconds(segments):
    total=0.;end=0.
    for segment in sorted(segments,key=lambda s:s['start_s']):
        total+=max(0.,segment['end_s']-max(end,segment['start_s']))
        end=max(end,segment['end_s'])
    return total


def audio_compatible(values):
    """Audio validity is independent of the description bank."""
    from .models import SemanticAudio
    try:
        if values['encoder_id'] != identity() or values['sampling_policy'] != POLICY:return False
        SemanticAudio.model_validate({k:values[k] for k in ('encoder_id','sampling_policy','segments')})
        duration=values['duration_s']
        if not math.isfinite(duration) or duration<=0:return False
        segments=values['segments']
        if [s['start_s'] for s in segments] != segment_starts(duration):return False
        for segment in segments:
            if abs(segment['end_s']-min(duration,segment['start_s']+10))>.02:return False
            if not all(math.isfinite(x) for x in segment['embedding']):return False
        return abs(values['sampled_seconds']-covered_seconds(segments))<.02
    except (KeyError,ValueError,TypeError):return False


def audio_fingerprint(values):
    data={k:values[k] for k in ('encoder_id','sampling_policy','duration_s','segments')}
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def matching_compatible(values):
    if not audio_compatible(values):return False
    if values.get('descriptor_bank_version')!=BANK_VERSION or values.get('descriptor_bank_digest')!=BANK_DIGEST:return False
    if values.get('matched_audio_sha256')!=audio_fingerprint(values):return False
    scores=values.get('descriptors',{})
    if set(scores)!=set(BANK):return False
    try:
        return all(scores[c['id']]['description']==c['description'] and scores[c['id']]['dimension']==c['dimension']
            and all(math.isfinite(scores[c['id']][k]) and -1.000001<=scores[c['id']][k]<=1.000001 for k in ('mean','min','max'))
            for c in CONCEPTS)
    except (KeyError,TypeError):return False


def save_audio_cache(digest,values):
    from .analysis_pipeline import _atomic_json
    if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Invalid audio hash')
    if not audio_compatible(values):raise ValueError('Incompatible audio embeddings')
    audio={k:values[k] for k in ('encoder_id','sampling_policy','duration_s','sampled_seconds','segments')}
    directory=ROOT/'output/semantic-audio-cache';directory.mkdir(parents=True,exist_ok=True)
    _atomic_json(directory/(digest+'.json'),{'sha256':digest,'audio_sha256':audio_fingerprint(audio),'values':audio})
    return audio


def load_audio_cache(digest,preferred=None):
    """Reuse verified audio from dedicated storage, a feature record, or an old stage checkpoint."""
    if preferred is not None and audio_compatible(preferred):return save_audio_cache(digest,preferred)
    standalone=ROOT/'output/semantic-audio-cache'/(digest+'.json')
    try:
        record=json.loads(standalone.read_text());values=record['values']
        if record['sha256']==digest and audio_compatible(values) and record['audio_sha256']==audio_fingerprint(values):return values
    except (OSError,ValueError,KeyError,TypeError):pass
    feature=ROOT/'output/web-features'/(digest+'.json')
    try:
        record=json.loads(feature.read_text())
        if record['sha256']==digest:
            for stage in record['algorithms']:
                if stage['algorithm_id']=='semantic_audio' and stage['status'] in ('passed','warning') and audio_compatible(stage['values']):return save_audio_cache(digest,stage['values'])
    except (OSError,ValueError,KeyError,TypeError):pass
    # Checkpoint filenames are content hashes; the recorded encoder and sampling policy must still match.
    for path in (ROOT/'output').rglob(digest+'.semantic_audio.json'):
        try:
            stage=json.loads(path.read_text())['result']
            if stage['status'] in ('passed','warning') and audio_compatible(stage['values']):return save_audio_cache(digest,stage['values'])
        except (OSError,ValueError,KeyError,TypeError):continue
    return None


def match_descriptions(audio,*,reused=True):
    """Only cached text vectors and arithmetic. Never loads a model or decodes audio."""
    import time
    start=time.perf_counter()
    if not audio_compatible(audio):raise ValueError('Incompatible audio embeddings')
    probes=text_embeddings(list(BANK.values()),cached_only=True);scores={}
    for concept,vector in zip(CONCEPTS,probes,strict=True):
        values=[sum(a*b for a,b in zip(segment['embedding'],vector,strict=True)) for segment in audio['segments']]
        scores[concept['id']]={'label':concept['label'],'dimension':concept['dimension'],'description':concept['description'],
                              'mean':sum(values)/len(values),'min':min(values),'max':max(values)}
    values={**audio,'model_id':MODEL_ID,'sample_rate_hz':24000,'descriptor_bank_version':BANK_VERSION,
            'descriptor_bank_digest':BANK_DIGEST,'matched_audio_sha256':audio_fingerprint(audio),'descriptors':scores,
            'score_kind':'cosine_similarity','audio_embeddings_reused':reused,'description_matching_wall_time_s':time.perf_counter()-start}
    return {'algorithm_id':'semantic_audio','implementation':POLICY,'implementation_version':'1.0.0','authority':'benchmark_estimate',
            'status':'warning','values':values,'warnings':['Cosines are similarities, not mood probabilities.',
            'Up to three sampled windows summarize only part of the track; scene suitability needs listening.',
            'These 120 character probes are not calibrated; strongest matches are relative suggestions.']}


def rematch_cached_audio(digest,preferred=None):
    audio=load_audio_cache(digest,preferred)
    return match_descriptions(audio) if audio is not None else None


def analyze_semantic_audio(path,model_dir=None):
    from .model_assets import sha256_file
    digest=sha256_file(path)
    cached=rematch_cached_audio(digest)
    if cached is not None:return cached
    # Ensure description setup is complete before doing expensive audio inference.
    text_embeddings(list(BANK.values()),cached_only=True)
    import numpy as np
    import torch
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],text=True,timeout=30).strip())
    model=load_model();segments=[]
    for start in segment_starts(duration):
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t','10','-ac','1','-ar','24000','-f','f32le','pipe:1'],timeout=60)
        wav=np.frombuffer(raw,dtype='<f4').copy();actual=len(wav)/24000
        if not len(wav) or not np.isfinite(wav).all():raise ValueError('Invalid decoded audio window')
        if len(wav)<240000:wav=np.tile(wav,math.ceil(240000/len(wav)))[:240000]
        with torch.inference_mode():vector=normalized(model(wavs=torch.from_numpy(wav[:240000]).unsqueeze(0))[0].tolist())
        segments.append({'start_s':start,'end_s':min(duration,start+actual),'embedding':vector})
    if sha256_file(path)!=digest:raise ValueError('Source changed during audio embedding extraction')
    audio=save_audio_cache(digest,{'encoder_id':identity(),'sampling_policy':POLICY,'duration_s':duration,
                          'sampled_seconds':covered_seconds(segments),'segments':segments})
    return match_descriptions(audio,reused=False)


def prepare_bank_worker(path,model_dir=None):
    from .analysis_pipeline import _atomic_json
    vectors=text_embeddings(list(BANK.values()))
    document={'version':BANK_VERSION,'bank_digest':BANK_DIGEST,'encoder_id':identity(),
              'concepts':[{**c,'embedding':v} for c,v in zip(CONCEPTS,vectors,strict=True)]}
    target=ROOT/'output/semantic-description-banks'/(BANK_VERSION+'.json');target.parent.mkdir(parents=True,exist_ok=True)
    _atomic_json(target,document)
    return {'algorithm_id':'semantic_bank','implementation':BANK_VERSION,'implementation_version':'1.0.0',
            'authority':'benchmark_estimate','status':'passed','values':{'count':len(vectors),'bank_digest':BANK_DIGEST,'path':str(target)}}


def encode_text_worker(path,model_dir=None):
    texts=json.loads(path.read_text())['texts']
    if not 1<=len(texts)<=4:raise ValueError('Expected one positive and at most three negative descriptions')
    return {'algorithm_id':'semantic_text','implementation':POLICY,'implementation_version':'1.0.0','authority':'benchmark_estimate','status':'warning','values':{'encoder_id':identity(),'embeddings':text_embeddings(texts)},'warnings':['Text embeddings are local retrieval targets.']}


def encode_query(query,catalog,vocabulary):
    """Local subprocess, bounded like acoustic workers; zero audio/provider IO."""
    from .search import search_tracks
    from .analysis_pipeline import run_worker
    from .models import SemanticQuery
    import tempfile
    candidate_query=query.model_copy(update={'semantic':None})
    candidates=set(search_tracks(catalog,candidate_query,vocabulary,ranking_version="maest-intent-v1").eligible_track_ids)
    tracks=[t for t in catalog.tracks if t.track_id in candidates]
    if len(tracks)<2:return query,[]
    try:
        encoder=identity()
        if any(t.semantic_audio is None or t.semantic_audio.encoder_id!=encoder or t.semantic_audio.sampling_policy!=POLICY for t in tracks):
            return query,['Upgrade analysis for all eligible tracks to enable semantic ranking.']
        directory=ROOT/'output/semantic-query-jobs';directory.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=directory) as temp:
            path=Path(temp);source=path/'query.json';source.write_text(json.dumps({'texts':[query.semantic.description,*query.semantic.avoid]}))
            result=run_worker(algorithm='semantic_text',source=source,model_dir=MODEL_DIR,work_dir=path,cpu_threads=4,max_rss_mb=6000,min_available_ram_mb=1024,timeout_s=300,telemetry_interval_s=.2,duration_s=None)
            if result.status not in {'passed','warning'}:raise ValueError(result.error or 'Text encoder failed')
            semantic=SemanticQuery(description=query.semantic.description,avoid=query.semantic.avoid,**result.values)
            return query.model_copy(update={'semantic':semantic}),[]
    except (ValueError,OSError) as exc:
        return query,['Local semantic encoding unavailable; structured ranking retained. '+str(exc)[:250]]
