import base64
import importlib.util
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('benchmark_runner',ROOT/'run-cloud-benchmark.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)


def test_plan_does_not_create_aws_clients():
    p=runner.plan()
    assert p['maximumInvocations']==45 and p['providerCalls']==0 and not p['audioInference']
    assert p['workerComputeAtAll45Times360SecondsAnd8GiB']==pytest.approx(2.16000432)


def test_billing_report_parses_units_without_retaining_logs():
    log='REPORT RequestId: opaque\tDuration: 18.2 ms\tBilled Duration: 124 ms\tMemory Size: 8192 MB\tMax Memory Used: 4021 MB\tInit Duration: 100.2 ms'
    assert runner.report_metrics(base64.b64encode(log.encode()).decode())=={'billedMilliseconds':124,'maxMemoryMB':4021,'initMilliseconds':100.2}


def test_missing_billing_report_stops_instead_of_recording_zero():
    with pytest.raises(ValueError):runner.report_metrics(base64.b64encode(b'no report').decode())
