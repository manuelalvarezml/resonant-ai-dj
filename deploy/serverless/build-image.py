#!/usr/bin/env python3
"""Bounded local Docker image build from an existing allowlisted context."""
import argparse,hashlib,json,shutil,subprocess,time
from pathlib import Path
import psutil
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--context',type=Path,required=True);p.add_argument('--tag',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--basis-receipt',type=Path);a=p.parse_args()
context=a.context.resolve();out=a.output.resolve()
if not context.is_relative_to(ROOT/'output/serverless-build') or not out.is_relative_to(ROOT/'output/serverless-build') or out.exists():raise ValueError('Use an existing allowlisted context and new output receipt')
import re
if not re.fullmatch(r'resonant-lambda:[a-z0-9-]+',a.tag):raise ValueError('Use a task-owned image tag')
identity=json.loads((context/'identity.json').read_text())
minimum_start=20;extra=[];basis=None
if a.basis_receipt:
 basis=json.loads(a.basis_receipt.read_text())
 observed=json.loads(subprocess.check_output(['docker','image','inspect',basis['tag']],text=True))[0]
 if basis.get('exitCode')!=0 or basis.get('stopReason') or observed['Id']!=basis['imageId']:raise ValueError('Incremental basis differs from verified image')
 previous=json.loads(subprocess.check_output(['docker','run','--rm','--network','none','--read-only','--memory','128m','--entrypoint','cat',basis['tag'],'/opt/resonant/identity.json'],text=True))
 for key in ['releaseId','plannerSha256','paritySha256','modelManifestSha256','encoderId']:
  if previous[key]!=identity[key]:raise ValueError('Incremental build may not change frozen artifacts')
 for key in ['requirements.lock','requirements-cpu.lock','requirements-build.lock','requirements-aws.lock']:
  if previous['sourceFiles'][key]!=identity['sourceFiles'][key]:raise ValueError('Incremental build may not change dependencies')
 incremental=context/'Dockerfile.incremental'
 incremental.write_text('FROM '+basis['tag']+'\nCOPY runtime ./runtime\nCOPY identity.json verify.py benchmark.py Dockerfile ./\nRUN python verify.py\n')
 extra=['-f',str(incremental)];minimum_start=8
if shutil.disk_usage(ROOT).free<minimum_start*2**30:raise ValueError('Insufficient disk for bounded build')
if psutil.virtual_memory().available<2*2**30:raise ValueError('Need2GiB host available memory before build')
log=out.with_suffix('.log');start=time.monotonic();reason=None;minimum_disk=shutil.disk_usage(ROOT).free;minimum_memory=psutil.virtual_memory().available
with log.open('x') as stream:
 process=subprocess.Popen(['docker','build','--platform','linux/amd64','--provenance=false','--progress=plain',*extra,'-t',a.tag,str(context)],stdout=stream,stderr=subprocess.STDOUT)
 while process.poll() is None:
  free=shutil.disk_usage(ROOT).free;available=psutil.virtual_memory().available;minimum_disk=min(free,minimum_disk);minimum_memory=min(available,minimum_memory)
  if free<5*2**30:reason='host_disk_floor'
  elif available<768*2**20:reason='host_memory_floor'
  elif time.monotonic()-start>2400:reason='build_time_limit'
  if reason:
   process.terminate()
   try:process.wait(timeout=15)
   except subprocess.TimeoutExpired:process.kill();process.wait()
   break
  time.sleep(2)
record={'buildId':identity['buildId'],'tag':a.tag,'exitCode':process.returncode,'stopReason':reason,'wallSeconds':round(time.monotonic()-start,2),'minimumDiskGiB':round(minimum_disk/2**30,2),'minimumHostAvailableMiB':round(minimum_memory/2**20,2),'cloudWrites':0}
if basis:record.update(incrementalBasisImageId=basis['imageId'],incrementalBasisBuildId=basis['buildId'])
# Preserve measured limits even if Docker's lazy layer metadata inspector fails.
out.write_text(json.dumps({**record,'inspectionStatus':'pending'},indent=2)+'\n')
if not process.returncode and not reason:
 image=json.loads(subprocess.check_output(['docker','image','inspect',a.tag],text=True))[0]
 # Docker Desktop may defer snapshot materialization until the first container.
 materialized=json.loads(subprocess.check_output(['docker','run','--rm','--platform','linux/amd64','--network','none','--read-only','--memory','128m','--entrypoint','cat',a.tag,'/opt/resonant/identity.json'],text=True))
 if materialized['buildId']!=identity['buildId']:raise ValueError('Exported image identity mismatch')
 layers=sum(int(v) for v in subprocess.check_output(['docker','image','history','--human=false','--format','{{.Size}}',a.tag],text=True).splitlines())
 record.update(imageId=image['Id'],dockerReportedBytes=image['Size'],expandedLayerBytes=layers,architecture=image['Architecture'],os=image['Os'])
 if layers>=10*2**30 or image['Architecture']!='amd64' or image['Os']!='linux':record['stopReason']='lambda_image_constraint_failed'
out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)
if record['exitCode'] or record['stopReason']:raise SystemExit(1)
