"""Offline composed-worker probe with frozen 187-track catalog and real text inference.

Only storage and the translator are fixtures; no provider or AWS network exists.
"""
import hashlib
import json
from pathlib import Path
import resource
import tempfile
import time
from types import SimpleNamespace
from unittest.mock import patch
import uuid

from prompt_to_playlist.cloud_catalog import FrozenPlanner
from prompt_to_playlist.models import PlaylistQuery, SemanticQuery, Translation
from prompt_to_playlist.service import build_playlist
from prompt_to_playlist.cloud_text import query_encoder as original_encoder
from runtime.encoder import WarmEncoder
from runtime.worker import Worker, browser_result
from runtime.state import canonical


class FixtureJobs:
    def __init__(self):self.rows={};self.provider_markers=0
    def claim(self, job, attempt, release):
        row=self.rows[job]
        if row['status']!='queued':return None
        row.update(status='running',attempt=attempt)
        return row.copy()
    def provider_started(self,job,attempt):
        assert self.rows[job]['status']=='running' and self.rows[job]['attempt']==attempt
        self.provider_markers+=1
    def finish(self,job,attempt,status,key=None,sha=None):
        assert self.rows[job]['status']=='running' and self.rows[job]['attempt']==attempt
        self.rows[job].update(status=status,resultKey=key)
        return True


class FixtureObjects:
    def __init__(self,root):self.root=root
    def get_json(self,key,limit):
        raw=(self.root/key).read_bytes()
        assert len(raw)<=limit
        return json.loads(raw)
    def optional_json(self,key,limit):
        return self.get_json(key,limit) if (self.root/key).exists() else None
    def put_json(self,key,value):
        file=self.root/key;file.parent.mkdir(parents=True,exist_ok=True)
        raw=canonical(value);file.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()


class FixtureTranslator:
    def translate_intent(self,prompt,vocabulary,*_):
        return Translation(request_text=prompt,query=PlaylistQuery(limit=10,semantic=SemanticQuery(description=prompt)),
                           provider='offline-fixture',model='none',prompt_version='lambda-probe',vocabulary_id=vocabulary.vocabulary_id)


def main():
    root=Path('/opt/resonant');started=time.monotonic()
    identity=json.loads((root/'identity.json').read_text())
    snapshot=FrozenPlanner.load(root/'release/private/planner.json')
    encoder=WarmEncoder(root/'models');jobs=FixtureJobs();rows=[]
    tracks=[{'id':row['id'],'sha256':row['sha256']} for row in snapshot.items.values()]
    with tempfile.TemporaryDirectory() as directory:
        objects=FixtureObjects(Path(directory))
        worker=Worker(identity['releaseId'],snapshot,encoder,jobs,objects,lambda _:FixtureTranslator(),scratch=directory)
        for index,prompt in enumerate(['Warm intimate acoustic music','Bright energetic dance music']):
            job=str(uuid.uuid4());request={'prompt':prompt,'tracks':tracks,'estimator_profile':'reference'}
            jobs.rows[job]={'status':'queued','requestSha256':objects.put_json('requests/'+job+'.json',request),'deadline':int(time.time())+360}
            event={'jobId':job,'releaseId':identity['releaseId']}
            context=SimpleNamespace(aws_request_id=str(uuid.uuid4()),get_remaining_time_in_millis=lambda:300000)
            begin=time.monotonic();result=worker.handle(event,context);seconds=time.monotonic()-begin
            actual=objects.get_json(jobs.rows[job]['resultKey'],32*1024*1024)
            assert result['status']=='succeeded' and actual['result']['ranking_version']=='hybrid-semantic-v1'
            vectors=objects.get_json('audits/'+job+'.json',32*1024*1024)['result']['translation']['query']['semantic']
            cat,voc=snapshot.select(tracks,'reference')
            with patch('prompt_to_playlist.cloud_text.bounded_encode',return_value={key:vectors[key] for key in ['encoder_id','embeddings']}):
                expected=build_playlist(prompt,cat,voc,FixtureTranslator(),query_encoder=original_encoder(root/'models',Path(directory)))
            assert actual==browser_result(expected.model_dump(mode='json',by_alias=True)),'Composed worker changed original planner result'
            assert worker.handle(event,context)['status']=='not_claimed'
            rows.append({'index':index,'seconds':seconds,'matched':len(actual['result']['matches']),
                         'exactOriginalAdapterParity':True,'duplicateIgnored':True})
    assert encoder.loads==1 and jobs.provider_markers==2
    return {'schema':'resonant/offline-worker-probe/1','tracks':len(tracks),'rows':rows,'modelLoads':encoder.loads,
            'peakRssKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'wallSeconds':time.monotonic()-started,
            'openaiCalls':0,'awsCalls':0,'audioInference':False,'awsLatencyMeasurement':False}


if __name__=='__main__':print(json.dumps(main()))
