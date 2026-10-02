"""Explicit model acquisition; normal inference never accesses the network."""
import hashlib
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / 'output' / 'semantic-models'
REPOS = [
    ('mulan', 'OpenMuQ/MuQ-MuLan-large', '2e01c796b71dca71b45251384c04cd7b237c9020', ['config.json', 'pytorch_model.bin']),
    ('muq', 'OpenMuQ/MuQ-large-msd-iter', '0562a57814f6f8bbd9fdea0a25921a2fce1a841a', ['config.json']),
    ('xlm-roberta', 'FacebookAI/xlm-roberta-base', 'e73636d4f797dec63c3081bb6ed5c7b0bb3f2089', ['config.json', 'tokenizer.json', 'tokenizer_config.json']),
]

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def main():
    records=[]
    for folder,repo,revision,files in REPOS:
        directory=ROOT/folder;directory.mkdir(parents=True,exist_ok=True)
        tree=json.load(urllib.request.urlopen(f'https://huggingface.co/api/models/{repo}/tree/{revision}',timeout=60))
        metadata={item['path']:item for item in tree}
        for name in files:
            path=directory/name;url=f'https://huggingface.co/{repo}/resolve/{revision}/{name}'
            expected=metadata[name].get('lfs',{}).get('oid');size=metadata[name]['size']
            if not path.exists():
                temp=path.with_name(name+'.part')
                try:
                    with urllib.request.urlopen(url,timeout=120) as response,temp.open('wb') as out:
                        while chunk:=response.read(1024*1024):out.write(chunk)
                    if temp.stat().st_size!=size or expected and sha(temp)!=expected:raise ValueError('Asset size/hash mismatch: '+name)
                    temp.replace(path)
                finally:temp.unlink(missing_ok=True)
            observed=sha(path)
            if path.stat().st_size!=size or expected and observed!=expected:raise ValueError('Cached asset mismatch: '+name)
            records.append(dict(path=str(path.relative_to(ROOT)),sha256=observed,size_bytes=size,repo=repo,revision=revision,url=url))
            print(folder,name,size,observed,flush=True)
    data={'model_id':'OpenMuQ/MuQ-MuLan-large','revision':REPOS[0][2],'license':'CC-BY-NC-4.0','assets':records}
    tmp=ROOT/'manifest.json.part';tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(ROOT/'manifest.json')
    print('Offline model assets ready:',ROOT,flush=True)

if __name__=='__main__':main()
