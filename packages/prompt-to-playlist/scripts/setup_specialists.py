"""Explicit, pinned asset acquisition; inference never calls this script."""
import argparse
import sys
import urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from prompt_to_playlist.specialists import STAGES, stage_assets, model_dir, verify_assets
from prompt_to_playlist.model_assets import sha256_file

def main():
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=STAGES);args=p.parse_args()
    for stage in [args.stage] if args.stage else STAGES:
        for item in stage_assets(stage):
            target=model_dir()/item['path']
            if target.is_file() and target.stat().st_size==item['size_bytes'] and sha256_file(target)==item['sha256']:continue
            target.parent.mkdir(parents=True,exist_ok=True);part=target.with_suffix(target.suffix+'.part')
            try:
                size=0
                with urllib.request.urlopen(item['url'],timeout=120) as response,part.open('wb') as out:
                    while block:=response.read(1024*1024):
                        size+=len(block)
                        if size>item['size_bytes']:raise ValueError('Oversized asset '+item['path'])
                        out.write(block)
                if size!=item['size_bytes'] or sha256_file(part)!=item['sha256']:raise ValueError('Asset identity mismatch '+item['path'])
                part.replace(target)
            finally:part.unlink(missing_ok=True)
        verify_assets(stage);print('Verified',stage,flush=True)
if __name__=='__main__':main()
