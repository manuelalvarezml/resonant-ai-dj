"""Export a frozen, private-library artwork sidecar and an explicit app allowlist.

No network or cloud writes. Base must be a separately verified live candidate;
app_source contains only reviewed artwork edits applied to that live app.
"""
import argparse
import hashlib
import json
from pathlib import Path
from artwork import Store

ALLOWED = {'index.html', 'src/app.js', 'src/adapters.js', 'src/artwork.js',
           'src/artwork.css', 'src/playlistiq.js', 'src/profile-views.js',
           'src/web-presentation.js'}
def digest(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def export(base, app_source, cache, output):
    base, app_source, cache, output = map(Path, (base, app_source, cache, output))
    if output.exists(): raise ValueError('Choose a new candidate directory')
    plan = json.loads((base / 'upload-plan.json').read_text())
    prefix = 'app/releases/' + plan['appId'] + '/'
    source = {}
    by_key = {r['key']: r for r in plan['uploads']}
    def checked(row):
        p = Path(row['localPath'])
        if p.is_symlink(): raise ValueError('Symlink in candidate')
        raw = p.read_bytes()
        if digest(raw) != row['sha256'] or len(raw) != row['bytes']: raise ValueError('Base candidate changed')
        return raw
    for key, row in by_key.items():
        if key.startswith(prefix): source[key[len(prefix):]] = checked(row)
    if not source: raise ValueError('Missing base app')
    if {p.relative_to(app_source).as_posix() for p in app_source.rglob('*') if p.is_file()} != ALLOWED:
        raise ValueError('The complete reviewed artwork overlay is required')
    changes = []
    for p in sorted(app_source.rglob('*')):
        if p.is_symlink(): raise ValueError('Symlink in artwork app overlay')
        if not p.is_file(): continue
        name = p.relative_to(app_source).as_posix()
        if name not in ALLOWED: raise ValueError('Unrelated app change: ' + name)
        raw = p.read_bytes()
        if source.get(name) != raw: changes.append(name)
        source[name] = raw
    library = json.loads(checked(by_key['library/current.json']))
    tracks = [t for page in library['pages'] for t in json.loads(checked(by_key[page.lstrip('/')]))['tracks']]
    if len(tracks) != library['trackCount']: raise ValueError('Incomplete published catalog')
    manifest = Store(cache).manifest('default')
    selected, images = {}, {}
    for track in tracks:
        record = manifest['tracks'].get(track['id'])
        if not record or record['source_version'] != track['sourceVersion'] or record['source_hash'] != track['fileHash']:
            raise ValueError('Backfill identity differs from published track: ' + track['id'])
        if record['status'] == 'ready':
            for label in ('cover', 'thumbnail'):
                item = record[label]
                if item['file'] != item['sha256'] + '.jpg' or len(item['sha256']) != 64: raise ValueError('Invalid image identity')
                raw = (cache / 'images' / item['file']).read_bytes()
                if digest(raw) != item['sha256']: raise ValueError('Artwork checksum mismatch')
                images['library/artwork/images/' + item['file']] = raw
        selected[track['id']] = record
    manifest['tracks'] = selected
    raw_manifest = encoded(manifest)
    artwork_id = digest(raw_manifest)
    manifest_key = 'library/artwork/releases/' + artwork_id + '/manifest.json'
    config = json.loads(source['config.json'])
    if not config.get('serverless'): raise ValueError('Expected hosted configuration')
    config['artwork'] = {'manifestURL': '/' + manifest_key, 'imageBase': '/library/artwork/images/'}
    source['config.json'] = encoded(config)
    app_id = digest(encoded(sorted((name, digest(raw)) for name, raw in source.items())))
    new_prefix = 'app/releases/' + app_id + '/'
    output.mkdir(parents=True, mode=0o700)
    uploads = []
    def put(key, raw, mutable=False):
        target = output / 'static' / key; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        uploads.append({'key':key,'localPath':str(target.resolve()),'bytes':len(raw),'sha256':digest(raw),
                        'cacheControl':'no-cache,max-age=0,must-revalidate' if mutable else 'private,max-age=31536000,immutable' if key.startswith('library/artwork/') else 'public,max-age=31536000,immutable'})
    for name, raw in source.items(): put(new_prefix + name, raw)
    for key, raw in images.items(): put(key, raw)
    put(manifest_key, raw_manifest)
    library['appId'] = app_id
    put('library/current.json', encoded(library), True)
    html = source['index.html'].decode().replace('href="./', 'href="/' + new_prefix).replace('src="./', 'src="/' + new_prefix)
    put('index.html', html.encode(), True)
    publish_keys = [r['key'] for r in uploads]
    retained = [r for r in plan['uploads'] if not r['key'].startswith(prefix) and r['key'] not in publish_keys]
    result = {**{k:plan[k] for k in ('schema','releaseId','stateBucket','trackCount')},'appId':app_id,'publishKeys':publish_keys,'uploads':retained+uploads}
    (output/'upload-plan.json').write_bytes(encoded(result))
    receipt = {'baseAppId':plan['appId'],'appId':app_id,'artworkId':artwork_id,'changedAppFiles':changes+['config.json'],
               'tracks':len(tracks),'ready':sum(r['status']=='ready' for r in selected.values()),'imageObjects':len(images),
               'bytes':sum(r['bytes'] for r in uploads),'audioOrAnalysisUploads':0}
    (output/'artwork-export.json').write_bytes(encoded(receipt))
    return receipt

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('base','app-source','cache','output'): p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args(); print(json.dumps(export(a.base,a.app_source,a.cache,a.output)))
