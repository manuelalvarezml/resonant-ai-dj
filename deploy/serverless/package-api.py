#!/usr/bin/env python3
"""Deterministic ZIP of prepared API source + locked pure-JS dependencies; no AWS."""
import argparse,base64,hashlib,json
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);a=p.parse_args()
c=a.candidate.resolve();source=c/'api';deps=ROOT/'deploy/serverless/api/node_modules'
if not c.is_relative_to(ROOT/'output') or not (source/'membership.json').is_file():raise ValueError('Expected a derived static candidate')
if (source/'package-lock.json').read_bytes()!=(ROOT/'deploy/serverless/api/package-lock.json').read_bytes():raise ValueError('Dependency lock mismatch')
files={x.name:x for x in source.iterdir() if x.is_file()}
for file in sorted(deps.rglob('*')):
 if '.bin' in file.relative_to(deps).parts:continue
 if file.is_symlink():raise ValueError('Unexpected linked dependency')
 if file.is_file():
  if file.suffix=='.node':raise ValueError('Native dependency needs a Linux build')
  files['node_modules/'+file.relative_to(deps).as_posix()]=file
out=c/'api.zip'
with zipfile.ZipFile(out,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for name,file in sorted(files.items()):
  info=zipfile.ZipInfo(name,date_time=(2026,10,2,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
  z.writestr(info,file.read_bytes())
b=out.read_bytes();record={'bytes':len(b),'files':len(files),'sha256':hashlib.sha256(b).hexdigest(),'codeSha256':base64.b64encode(hashlib.sha256(b).digest()).decode()}
(c/'api-package.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
