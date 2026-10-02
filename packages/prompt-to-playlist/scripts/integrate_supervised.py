"""Attach only the two verified smoke outputs to existing web cache records.

No inference or corpus discovery. Historical cache snapshots are kept. Browser
reload or Check experimental estimators picks up these hash-matched records.
"""
import copy
import json
import time
from pathlib import Path
from smoke_supervised import ROOT, SOURCES
from prompt_to_playlist.analysis_models import DescriptorRun
from prompt_to_playlist.analysis_pipeline import _atomic_json
from prompt_to_playlist.model_assets import sha256_file
from prompt_to_playlist.supervised import manifest, verify_assets
from prompt_to_playlist.web_bridge import cache_path, compatible, EXPERIMENTAL_STAGES


def verified_results(run_root, digest):
    results = []
    expected = {'supervised_'+a['path'].replace('/', '_'): a['sha256'] for a in manifest()['assets']}
    for stage in EXPERIMENTAL_STAGES:
        run = DescriptorRun.model_validate_json((run_root/stage/'descriptor-run.json').read_text())
        if not run.source_hashes_unchanged or not run.source_inventory_unchanged or len(run.tracks) != 1:
            raise ValueError('Unverified source preservation')
        source = run.tracks[0].source
        assets = {a.asset_id: a.sha256 for a in run.model_assets}
        if source.sha256_before != digest or source.sha256_after != digest or any(assets.get(k) != v for k,v in expected.items()):
            raise ValueError('Source or model manifest mismatch')
        result = next(a.model_dump(mode='json') for a in run.tracks[0].algorithms if a.algorithm_id == stage)
        if not compatible(result):
            raise ValueError('Failed, stale or malformed estimator output')
        results.append(result)
    return results


def main():
    verify_assets()
    evidence = []
    for filename, slug, digest in SOURCES:
        source = ROOT.parents[1]/'test_music'/'test_folder_37_tracks_diff_genres'/filename
        if sha256_file(source) != digest:
            raise ValueError('Authorized source identity mismatch')
        path = cache_path(digest)
        before = json.loads(path.read_text())
        if before['sha256'] != digest or before['status'] != 'complete':
            raise ValueError('Complete existing reference cache required')
        extra = verified_results(ROOT/'output/supervised-estimators/matched-v2'/slug, digest)
        result = copy.deepcopy(before)
        base = [a for a in before['algorithms'] if a['algorithm_id'] not in EXPERIMENTAL_STAGES]
        result['algorithms'] = copy.deepcopy(base)+extra
        result['supervised_status'] = 'complete'
        if result != before:
            history = path.parent/'history'/digest
            history.mkdir(parents=True,exist_ok=True)
            _atomic_json(history/(str(time.time_ns())+'-before-supervised.json'), before)
            _atomic_json(path, result)
        after = json.loads(path.read_text())
        assert [a for a in after['algorithms'] if a['algorithm_id'] not in EXPERIMENTAL_STAGES] == base
        assert sha256_file(source) == digest
        evidence.append({'source':slug,'sha256':digest,'reference_and_muq_unchanged':True,'optional_stages':EXPERIMENTAL_STAGES})
    _atomic_json(ROOT/'output/supervised-estimators/integration.json',evidence)
    print(json.dumps(evidence,indent=2))


if __name__ == '__main__':main()
