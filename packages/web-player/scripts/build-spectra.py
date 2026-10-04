#!/usr/bin/env python3
"""Read-only local display spectra. No model inference or source modification."""
import argparse,base64,hashlib,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
RATE=44100;HOP=4410;SIZE=8192;COLUMNS=96

def spectrum_file(source,target):
 window=np.blackman(SIZE).astype(np.float32);hz=np.geomspace(20,20000,COLUMNS);centers=hz*SIZE/RATE
 radii=np.maximum(0,(centers*((1000)**(.5/(COLUMNS-1))-(1000)**(-.5/(COLUMNS-1)))-1)/2)
 ranges=[(max(0,int(np.floor(c-r))),min(SIZE//2,int(np.ceil(c+r)))) for c,r in zip(centers,radii)]
 process=subprocess.Popen(['ffmpeg','-v','error','-threads','1','-i',str(source),'-vn','-ac','1','-ar',str(RATE),'-f','f32le','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 history=np.zeros(SIZE-HOP,dtype=np.float32);frames=[];tail=b''
 try:
  while True:
   raw=process.stdout.read(HOP*100*4)
   if not raw:break
   raw=tail+raw;n=(len(raw)//(HOP*4))*HOP*4;tail=raw[n:]
   if not n:continue
   samples=np.frombuffer(raw[:n],dtype='<f4');joined=np.concatenate([history,samples]);view=np.lib.stride_tricks.sliding_window_view(joined,SIZE)[::HOP]
   magnitude=np.abs(np.fft.rfft(view*window,axis=1))/SIZE
   db=np.clip(20*np.log10(np.maximum(magnitude,1e-12)),-90,0)
   bands=np.stack([np.max(db[:,a:b+1],axis=1) for a,b in ranges],axis=1)
   frames.append(np.round((bands+90)/90*255).astype(np.uint8));history=joined[-(SIZE-HOP):]
  error=process.stderr.read();assert process.wait()==0,error.decode()[:200]
 finally:
  if process.poll() is None:process.kill();process.wait()
 data=np.concatenate(frames).tobytes();source_hash=hashlib.file_digest(source.open('rb'),'sha256').hexdigest()
 payload={'schema':'resonant-spectrum/1','sourceHash':source_hash,'fps':10,'columns':COLUMNS,'sampleRate':RATE,'fftSize':SIZE,'minHz':20,'maxHz':20000,'frames':len(data)//COLUMNS,'data':base64.b64encode(data).decode()}
 target.write_text(json.dumps(payload,separators=(',',':')))

def main():
 p=argparse.ArgumentParser();p.add_argument('--limit',type=int);a=p.parse_args();release=ROOT/'output/cloud-releases/first-release';out=ROOT/'output/display-spectra/v1';out.mkdir(parents=True,exist_ok=True)
 sources=[(s.stem,s) for s in sorted((release/'media').glob('*.mp3'))]
 manifest=json.loads((release/'release.json').read_text());sources.append(('mix-house-example',release/manifest['mixAudioPath']))
 for i,(key,source) in enumerate(sources[:a.limit] if a.limit else sources):
  target=out/(key+'.json')
  if not target.exists():spectrum_file(source,target)
  if i%20==0:print(json.dumps({'ready':i+1,'total':len(sources)}),flush=True)
 print(json.dumps({'ready':len(list(out.glob('*.json'))),'bytes':sum(x.stat().st_size for x in out.glob('*.json'))}))
if __name__=='__main__':main()
