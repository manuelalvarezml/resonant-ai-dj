"""Explicit model acquisition. Inference itself never downloads assets."""
import sys
import urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from prompt_to_playlist.supervised import manifest, model_dir, verify_assets
from prompt_to_playlist.model_assets import sha256_file


def main():
    root = model_dir()
    for item in manifest()['assets']:
        target = root / item['path']
        if target.is_file() and sha256_file(target) == item['sha256']:
            print('Verified', item['path'])
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        temp = target.with_suffix(target.suffix + '.part')
        try:
            size = 0
            with urllib.request.urlopen(item['url'], timeout=120) as response, temp.open('wb') as out:
                while block := response.read(1024 * 1024):
                    size += len(block)
                    if size > item['size_bytes']:
                        raise ValueError('Asset exceeds pinned size: ' + item['path'])
                    out.write(block)
            if size != item['size_bytes'] or sha256_file(temp) != item['sha256']:
                raise ValueError('Asset identity mismatch: ' + item['path'])
            temp.replace(target)
        finally:
            temp.unlink(missing_ok=True)
        print('Downloaded and verified', item['path'])
    verify_assets()


if __name__ == '__main__':
    main()
