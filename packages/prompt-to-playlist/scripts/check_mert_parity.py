"""Generated-signal parity against the pinned, locally audited official MERT source."""
import importlib.util
import json
import sys
import types
from pathlib import Path
import torch
from prompt_to_playlist._music2emo.runtime import MERTFeatures
from prompt_to_playlist.supervised import verify_assets
from prompt_to_playlist.model_assets import sha256_file

root=Path(__file__).resolve().parents[1]
research=root/'output/supervised-estimators/research'
# Explicit local source imports; never trust_remote_code or an unpinned network load.
pkg=types.ModuleType('audited_mert');pkg.__path__=[str(research)];sys.modules['audited_mert']=pkg
for name in ('configuration_MERT','modeling_MERT'):
    spec=importlib.util.spec_from_file_location('audited_mert.'+name,research/(name+'.py'))
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
config_class=sys.modules['audited_mert.configuration_MERT'].MERTConfig
model_class=sys.modules['audited_mert.modeling_MERT'].MERTModel
torch.set_num_threads(4);torch.manual_seed(0)
assets=verify_assets();adapter=MERTFeatures(assets)
config=config_class(**json.loads((assets/'mert/config.json').read_text()));config._attn_implementation='eager'
original=model_class(config).eval()
original.load_state_dict(torch.load(assets/'mert/pytorch_model.bin',map_location='cpu',weights_only=True),strict=True)
t=torch.arange(24000*2)/24000
wave=.2*torch.sin(2*torch.pi*220*t)+.1*torch.sin(2*torch.pi*440*t)
inputs=adapter.processor(wave,sampling_rate=24000,return_tensors='pt')
with torch.inference_mode():
    a=adapter.model(**inputs,output_hidden_states=True).hidden_states
    b=original(**inputs,output_hidden_states=True).hidden_states
errors=[float((x-y).abs().max()) for x,y in zip(a,b)]
assert len(a)==len(b)==13 and max(errors)<1e-6
report={'input':'generated 2-second 220+440Hz signal; no corpus audio','hidden_states':len(a),'max_abs_error_by_layer':errors,'allclose_atol':1e-6,'strict_weight_loading':True,'source_sha256':{n:sha256_file(research/n) for n in ('configuration_MERT.py','modeling_MERT.py')}}
(root/'output/supervised-estimators/mert-parity.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
