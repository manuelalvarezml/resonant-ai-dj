"""Cloud-only loader: identical model construction; verify large assets at build time.

The read-only Lambda image is pinned by ECR digest. verify.py hashes every model
asset before image export. Rehashing 2.6GB on Lambda's lazy container filesystem
caused a measured 360s timeout. Startup checks manifest identity and asset sizes;
The original text classes, projection, weights, precision and evaluation are
unchanged. The unused audio tower is not instantiated; its checkpoint tensors
remain in the verified bundle but are never paged in for text-only requests.
"""
import hashlib
import json
import os
from pathlib import Path
from prompt_to_playlist.semantic_audio import model_manifest

def load_packaged_model(root):
    doc_path=Path(os.environ.get('RESONANT_IDENTITY','/opt/resonant/identity.json'))
    doc=json.loads(doc_path.read_text())
    if Path(root).resolve() != (doc_path.parent/'models').resolve() or hashlib.sha256((Path(root)/'manifest.json').read_bytes()).hexdigest()!=doc['modelManifestSha256']:
        raise ValueError('Expected the verified immutable model bundle')
    # No nested pretrained downloads: instantiate from pinned configs, then load
    # the COMPLETE official MuLan state dictionary with strict key validation.
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    os.environ['TOKENIZERS_PARALLELISM']='false'
    model_manifest(root,verify=False)
    import torch
    from muq import MuQMuLan
    from muq.muq_mulan.models.text import TextTransformerPretrained
    from muq.muq_mulan.models.mulan import MuLanModel
    from transformers import XLMRobertaConfig, XLMRobertaModel, AutoTokenizer
    torch.set_num_threads(int(os.environ.get('PLAYLISTIQ_CPU_THREADS','4')))
    class UnusedAudio(torch.nn.Module):
        def __init__(self,dim,depth):
            super().__init__();self.dim=dim;self.depth=depth
        def forward(self,*args,**kwargs):
            raise ValueError('This cloud encoder accepts text only')
    class LocalText(TextTransformerPretrained):
        def _init_pretrained_model(self):
            return XLMRobertaModel(XLMRobertaConfig.from_dict(json.loads((root/'xlm-roberta/config.json').read_text())))
        def _init_tokenizer(self):
            return AutoTokenizer.from_pretrained(str(root/'xlm-roberta'),local_files_only=True,trust_remote_code=False)
    class LocalMuLan(MuQMuLan):
        @classmethod
        def create_MuLan_from_config(cls, config, hf_hub_cache_dir=None):
            if config.mulan.hierarchical_contrastive_loss:
                raise ValueError('Unexpected model architecture')
            audio=UnusedAudio(config.audio_transformer.dim,config.audio_transformer.tf_depth)
            text=LocalText(model_name=config.text_model.name,model_dim=config.text_model.model_dim,**config.text_transformer,frozen_pretrained=False)
            return MuLanModel(audio_transformer=audio,text_transformer=text,**config.mulan)
    model=LocalMuLan(json.loads((root/'mulan/config.json').read_text()))
    state=torch.load(root/'mulan/pytorch_model.bin',map_location='cpu',weights_only=True,mmap=True)
    # Exclude only the unused audio tower. Keep the exact official MuLan text
    # forward/projection/normalization and enforce every remaining state key.
    audio_keys=[key for key in state if key.startswith('mulan.audio.')]
    if not audio_keys:raise ValueError('Expected the complete pinned MuLan checkpoint')
    for key in audio_keys:del state[key]
    model.load_state_dict(state,strict=True,assign=True)
    return model.eval().float()
