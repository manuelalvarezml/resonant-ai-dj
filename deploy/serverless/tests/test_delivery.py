"""Guard boundaries that would otherwise publish to an incorrect destination."""
import importlib.util,json
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('delivery_templates',HERE/'templates.py');templates=importlib.util.module_from_spec(spec);spec.loader.exec_module(templates)

def test_regional_runtime_does_not_proxy_media_or_grant_worker_media_access():
 r=templates.runtime['Resources'];routes=[v['Properties']['RouteKey'] for v in r.values() if v['Type']=='AWS::ApiGatewayV2::Route']
 assert all('/media' not in route and '/library' not in route for route in routes)
 worker=json.dumps(r['WorkerRole'])
 assert 'MediaBucket' not in worker and 'signing-key' not in worker and 'password-hash' not in worker
 assert r['Worker']['Properties']['ReservedConcurrentExecutions']=={'Ref':'WorkerConcurrency'}
 assert templates.runtime['Parameters']['WorkerConcurrency']['Default']==0
 assert templates.runtime['Parameters']['WorkerConcurrency']['AllowedValues']==[0,1]
 assert r['AsyncPolicy']['Properties']['MaximumRetryAttempts']==0
 assert r['WorkerVersion']['UpdateReplacePolicy']==r['ApiVersion']['UpdateReplacePolicy']=='Retain'
 assert 's3:ListBucket' in worker
 for name in ['Api','Worker']:
  assert r[name]['Properties']['Environment']['Variables']['RESONANT_RUNTIME_REVISION']=={'Ref':'RuntimeRevision'}

def test_edge_requires_free_subscription_and_authenticates_every_media_cache_hit():
 r=templates.edge['Resources'];assert r['FreeSubscription']['Properties']['PlanTier']=='FREE'
 d=r['Distribution']['Properties']['DistributionConfig'];assert len(d['CacheBehaviors'])+1==5
 assert 'TrustedKeyGroups' not in d['DefaultCacheBehavior']  # First-visit redirect must run before sign-in.
 for b in [b for b in d['CacheBehaviors'] if b['PathPattern'] in ['/media/*','/library/*']]:
  assert b['TrustedKeyGroups']==[{'Ref':'KeyGroup'}]
 api=next(b for b in d['CacheBehaviors'] if b['PathPattern']=='/api/*')
 assert api['CachePolicyId']=='4135ea2d-6df8-44a3-9df3-4b5a84be39ad'
 for rule in r['WebACL']['Properties']['Rules']:
  rate=rule['Statement']['RateBasedStatement']
  assert rate['AggregateKeyType']=='IP' and rate['EvaluationWindowSec']==300
  assert rate['Limit']>=6000 and 'ScopeDownStatement' not in rate

def test_buckets_are_private_and_state_expiry_does_not_delete_audio():
 r=templates.foundation['Resources']
 for name in ['StateBucket','MediaBucket','ArtifactBucket']:
  assert all(r[name]['Properties']['PublicAccessBlockConfiguration'].values())
  assert r[name]['DeletionPolicy']=='Retain'
 media=r['MediaBucket']['Properties']['LifecycleConfiguration']['Rules']
 assert all('ExpirationInDays' not in x for x in media)
 assert r['State']['Properties']['DeletionProtectionEnabled'] is True

def test_shared_profile_reuses_state_table_and_preserves_existing_route_ids():
 r=templates.runtime['Resources']
 assert r['Route0']['Properties']['RouteKey']=='POST /api/session/login'
 routes={v['Properties']['RouteKey'] for v in r.values() if v['Type']=='AWS::ApiGatewayV2::Route'}
 assert {'GET /api/profile','POST /api/profile'} <= routes
 assert 'dynamodb:Query' in json.dumps(r['ApiRole'])
 assert not any(v['Type']=='AWS::DynamoDB::Table' for v in r.values())


def test_custom_domain_retains_https_and_exact_origin_allowlists():
 d=templates.edge['Resources']['Distribution']['Properties']['DistributionConfig']
 assert d['Aliases']=={'Fn::If':['HasCustomDomain',[{'Ref':'CustomDomain'}],{'Ref':'AWS::NoValue'}]}
 cert=d['ViewerCertificate']['Fn::If'][1]
 assert cert['SslSupportMethod']=='sni-only' and cert['MinimumProtocolVersion']=='TLSv1.2_2021'
 assert 'us-east-1' in templates.edge['Parameters']['CertificateArn']['AllowedPattern']
 origins=templates.foundation['Resources']['StateBucket']['Properties']['CorsConfiguration']['CorsRules'][0]['AllowedOrigins']
 assert '*' not in origins and {'Ref':'WebOrigin'} in origins
 assert templates.runtime['Resources']['Api']['Properties']['Environment']['Variables']['RESONANT_ADDITIONAL_ORIGINS']=={'Ref':'AdditionalWebOrigin'}
