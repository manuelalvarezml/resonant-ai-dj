"""Offline planning arithmetic; does not contact AWS or change infrastructure."""
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
inputs = json.loads((HERE / 'cost-inputs.json').read_text())
r = inputs['rates']
a = inputs['assumptions']
rows = []
for scenario in inputs['scenarios']:
    jobs, seconds = scenario['jobs'], scenario['worker_billed_seconds']
    api_calls = a['base_api_calls'] + jobs * (math.ceil(seconds / a['poll_seconds']) + a['extra_calls_per_job'])
    parts = {
        's3_storage': a['s3_total_gib'] * r['s3_storage_gib_month'],
        's3_requests': (a['base_s3_get'] + jobs * a['s3_get_per_job']) * r['s3_get'] + (a['base_s3_put'] + jobs * a['s3_put_per_job']) * r['s3_put'],
        'ecr': a['ecr_retained_unique_gib'] * r['ecr_gib_month'],
        'logs_ingest': a['logs_ingest_gib'] * r['logs_ingest_gib'],
        'alarms': a['alarms'] * r['alarm_month'],
        'ancillary_allowance': a['ancillary_allowance_usd'],
        'worker_compute': jobs * seconds * a['worker_memory_gib'] * r['lambda_gib_second'],
        'lambda_requests': (jobs + api_calls) * r['lambda_request'],
        'api_compute': api_calls * a['api_memory_gib'] * a['api_billed_seconds'] * r['lambda_gib_second'],
        'http_api': api_calls * r['http_api_request'],
        'dynamodb': jobs * a['ddb_write_units_per_job_including_transactions'] * r['ddb_write_unit'] + api_calls * a['ddb_read_units_per_api_call'] * r['ddb_read_unit'],
        'sqs': math.ceil(jobs * a['failure_fraction']) * a['sqs_requests_per_failure'] * r['sqs_request'],
    }
    gross = sum(parts.values())
    credit = min(a['s3_total_gib'], a['s3_credit_gib_if_eligible']) * r['s3_storage_gib_month']
    rows.append({**scenario, 'api_calls': api_calls, 'components_usd': parts, 'total_without_storage_credit_usd': gross, 'total_with_storage_credit_usd': gross - credit})
result = {'as_of': inputs['as_of'], 'scope': 'CloudFront Free eligible; OpenAI excluded; modeled AWS usage only', 'mp3_gib': 1910985140 / 2**30, 'scenarios': rows}
(HERE / 'cost-results.json').write_text(json.dumps(result, indent=2) + '\n')
for row in rows:
    print(f"{row['label']}: ${row['total_with_storage_credit_usd']:.2f} eligible / ${row['total_without_storage_credit_usd']:.2f} without S3 credit; worker ${row['components_usd']['worker_compute']:.2f}")
