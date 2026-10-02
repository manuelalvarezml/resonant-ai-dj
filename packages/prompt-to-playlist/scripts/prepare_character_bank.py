"""Prepare and validate all character text embeddings, without opening audio."""
import json
from pathlib import Path
from prompt_to_playlist.analysis_pipeline import run_worker, _atomic_json
from prompt_to_playlist.semantic_audio import ROOT, MODEL_DIR, BANK, BANK_VERSION, BANK_DIGEST, text_embeddings

out=ROOT/'output/semantic-description-banks';out.mkdir(parents=True,exist_ok=True)
source=out/'prepare-request.json';source.write_text(json.dumps({'version':BANK_VERSION,'digest':BANK_DIGEST}))
result=run_worker(algorithm='semantic_bank',source=source,model_dir=MODEL_DIR,work_dir=out,
    cpu_threads=4,max_rss_mb=6000,min_available_ram_mb=1024,timeout_s=600,telemetry_interval_s=.2,duration_s=None)
_atomic_json(out/(BANK_VERSION+'-preparation.json'),result.model_dump(mode='json'))
if result.status=='failed':raise RuntimeError(result.error)
assert len(text_embeddings(list(BANK.values()),cached_only=True))==120
print(json.dumps(result.model_dump(mode='json'),indent=2))
