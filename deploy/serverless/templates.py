#!/usr/bin/env python3
"""Generate reviewed CloudFormation sources; performs no AWS operations."""
import json
from pathlib import Path
R=lambda x:{'Ref':x}
S=lambda x:{'Fn::Sub':x}
A=lambda x,y='Arn':{'Fn::GetAtt':[x,y]}
TAGS=[{'Key':'Project','Value':'resonant'}]
def resource(t,p,**more): return {'Type':'AWS::'+t,'Properties':p,**more}
def template(description,params,resources,outputs):
 return {'AWSTemplateFormatVersion':'2010-09-09','Description':description,'Parameters':params,'Resources':resources,'Outputs':{k:{'Value':v} for k,v in outputs.items()}}
def string(**kw):return {'Type':'String',**kw}
def statement(actions,res,**kw):return {'Effect':'Allow','Action':actions,'Resource':res,**kw}
def policy(statements):return {'Version':'2012-10-17','Statement':statements}
def tls(bucket):return {'Effect':'Deny','Principal':'*','Action':'s3:*','Resource':[A(bucket),S('${'+bucket+'.Arn}/*')],'Condition':{'Bool':{'aws:SecureTransport':'false'}}}
def bucket(versioned=False):
 p={'PublicAccessBlockConfiguration':{k:True for k in ['BlockPublicAcls','BlockPublicPolicy','IgnorePublicAcls','RestrictPublicBuckets']},'OwnershipControls':{'Rules':[{'ObjectOwnership':'BucketOwnerEnforced'}]},'BucketEncryption':{'ServerSideEncryptionConfiguration':[{'ServerSideEncryptionByDefault':{'SSEAlgorithm':'AES256'}}]},'Tags':TAGS,'LifecycleConfiguration':{'Rules':[{'Id':'abort-incomplete','Status':'Enabled','AbortIncompleteMultipartUpload':{'DaysAfterInitiation':1}}]}}
 if versioned:p['VersioningConfiguration']={'Status':'Enabled'}
 return resource('S3::Bucket',p,DeletionPolicy='Retain',UpdateReplacePolicy='Retain')
def role(statements):return resource('IAM::Role',{'AssumeRolePolicyDocument':policy([{'Effect':'Allow','Principal':{'Service':'lambda.amazonaws.com'},'Action':'sts:AssumeRole'}]),'Policies':[{'PolicyName':'MinimumRuntimeAccess','PolicyDocument':policy(statements)}],'Tags':TAGS})
# Ohio foundation first. Reapply its two edge parameters after the global stack.
f={k:bucket(k!='StateBucket') for k in ['MediaBucket','StateBucket','ArtifactBucket']}
for name, suffix in [('MediaBucket','media'),('StateBucket','state'),('ArtifactBucket','artifacts')]:
 f[name]['Properties']['BucketName']=S('resonant-${AWS::AccountId}-${AWS::Region}-${AWS::StackName}-'+suffix)
f['StateBucket']['Properties']['CorsConfiguration']={'CorsRules':[{'AllowedOrigins':[R('WebOrigin')],'AllowedMethods':['GET','HEAD'],'AllowedHeaders':['*'],'ExposedHeaders':['ETag'],'MaxAge':300}]}
f['StateBucket']['Properties']['LifecycleConfiguration']['Rules'] += [{'Id':prefix[:-1],'Prefix':prefix,'Status':'Enabled','ExpirationInDays':days} for prefix,days in [('requests/',7),('results/',7),('audits/',7),('text-cache/',30)]]
for name in ['MediaBucket','StateBucket','ArtifactBucket']:
 statements=[tls(name)]
 if name=='MediaBucket': statements.append({'Fn::If':['HasEdge',statement('s3:GetObject',S('${MediaBucket.Arn}/*'),Principal={'Service':'cloudfront.amazonaws.com'},Condition={'StringEquals':{'AWS:SourceArn':R('DistributionArn')}}),R('AWS::NoValue')]})
 f[name+'Policy']=resource('S3::BucketPolicy',{'Bucket':R(name),'PolicyDocument':policy(statements)})
f['State']=resource('DynamoDB::Table',{'BillingMode':'PAY_PER_REQUEST','OnDemandThroughput':{'MaxReadRequestUnits':50,'MaxWriteRequestUnits':25},'AttributeDefinitions':[{'AttributeName':k,'AttributeType':'S'} for k in ['pk','sk']],'KeySchema':[{'AttributeName':'pk','KeyType':'HASH'},{'AttributeName':'sk','KeyType':'RANGE'}],'TimeToLiveSpecification':{'AttributeName':'ttl','Enabled':True},'DeletionProtectionEnabled':True,'Tags':TAGS},DeletionPolicy='Retain',UpdateReplacePolicy='Retain')
f['HttpApi']=resource('ApiGatewayV2::Api',{'Name':S('${AWS::StackName}-api'),'ProtocolType':'HTTP','DisableExecuteApiEndpoint':False})
foundation=template('Resonant Ohio foundation; no public objects or compute',{'WebOrigin':string(Default='https://unpublished.invalid',AllowedPattern='https://[a-z0-9.-]+'),'DistributionArn':string(Default='',AllowedPattern='(|arn:aws:cloudfront::[0-9]{12}:distribution/[A-Z0-9]+)')},f,{**{k:R(k) for k in ['MediaBucket','StateBucket','ArtifactBucket','State','HttpApi']},'MediaDomain':A('MediaBucket','RegionalDomainName')})
foundation['Conditions']={'HasEdge':{'Fn::Not':[{'Fn::Equals':[R('DistributionArn'),'']}]}}
# Global edge stack MUST run us-east-1 because WAF CLOUDFRONT scope lives there.
e={}
e['WebACL']=resource('WAFv2::WebACL',{'Scope':'CLOUDFRONT','DefaultAction':{'Allow':{}},'VisibilityConfig':{'SampledRequestsEnabled':False,'CloudWatchMetricsEnabled':True,'MetricName':'resonant-edge'},'Rules':[{'Name':'rate-limit','Priority':0,'Action':{'Block':{}},'Statement':{'RateBasedStatement':{'Limit':300,'AggregateKeyType':'IP','EvaluationWindowSec':60}},'VisibilityConfig':{'SampledRequestsEnabled':False,'CloudWatchMetricsEnabled':True,'MetricName':'resonant-rate'}}],'Tags':TAGS})
# Free plan rejected the path-scoped rate rules during real subscription creation.
# A broad IP ceiling handles floods; API Gateway and DynamoDB keep the tighter
# control-plane/login limits, without imposing those low limits on audio ranges.
e['WebACL']['Properties']['Rules']=[]
e['WebACL']['Properties']['Rules'].append({'Name':'ip-flood-limit','Priority':0,'Action':{'Block':{}},'Statement':{'RateBasedStatement':{'Limit':6000,'AggregateKeyType':'IP','EvaluationWindowSec':300}},'VisibilityConfig':{'SampledRequestsEnabled':False,'CloudWatchMetricsEnabled':True,'MetricName':'resonant-ip-flood'}})
e['PublicKey']=resource('CloudFront::PublicKey',{'PublicKeyConfig':{'CallerReference':S('${AWS::StackName}-cookie-key'),'Name':S('${AWS::StackName}-cookie-key'),'EncodedKey':R('CookiePublicKey')}})
e['KeyGroup']=resource('CloudFront::KeyGroup',{'KeyGroupConfig':{'Name':S('${AWS::StackName}-listeners'),'Items':[R('PublicKey')]}})
e['OAC']=resource('CloudFront::OriginAccessControl',{'OriginAccessControlConfig':{'Name':S('${AWS::StackName}-s3'),'OriginAccessControlOriginType':'s3','SigningBehavior':'always','SigningProtocol':'sigv4'}})
# The app shell must be reachable before CloudFront's signed-cookie gate so a
# first-time visitor can reach login. Library/media behaviors validate signatures;
# the default origin contains only the allowlisted public HTML/JS/CSS shell.
function="""function handler(event) { var r=event.request; if(r.uri!=='/' && r.uri!=='/index.html') return r; var p=r.cookies['CloudFront-Policy']; var valid=false; try { var raw=p.value.replace(/-/g,'+').replace(/_/g,'=').replace(/~/g,'/'); var policy=JSON.parse(Buffer.from(raw,'base64').toString()); valid=policy.Statement[0].Condition.DateLessThan['AWS:EpochTime']>Date.now()/1000; } catch(e) {} if(!valid) return {statusCode:302,headers:{location:{value:'/login/index.html'},'cache-control':{value:'no-store'}}}; return r; }"""
e['Entry']=resource('CloudFront::Function',{'Name':S('${AWS::StackName}-entry'),'AutoPublish':True,'FunctionConfig':{'Comment':'Sign-in navigation for expired document sessions','Runtime':'cloudfront-js-2.0'},'FunctionCode':function})
cache='658327ea-f89d-4fab-a63d-7e88639e58f6';disabled='4135ea2d-6df8-44a3-9df3-4b5a84be39ad';security='67f7725c-6f97-4210-82d7-5512b31e9d03'
def behavior(origin='s3',protected=True):
 b={'TargetOriginId':origin,'ViewerProtocolPolicy':'redirect-to-https','AllowedMethods':['GET','HEAD'],'CachedMethods':['GET','HEAD'],'Compress':True,'CachePolicyId':cache,'ResponseHeadersPolicyId':security}
 if protected:b['TrustedKeyGroups']=[R('KeyGroup')]
 return b
base=behavior(protected=False);base['FunctionAssociations']=[{'EventType':'viewer-request','FunctionARN':A('Entry','FunctionARN')}]
api=behavior('api',False);api.update(PathPattern='/api/*',AllowedMethods=['GET','HEAD','OPTIONS','PUT','PATCH','POST','DELETE'],CachePolicyId=disabled,OriginRequestPolicyId='b689b0a8-53d0-40ab-baf2-68738e2966ac')
e['Distribution']=resource('CloudFront::Distribution',{'DistributionConfig':{'Enabled':True,'Comment':'Resonant private shared library','DefaultRootObject':'index.html','HttpVersion':'http2and3','IPV6Enabled':True,'ViewerCertificate':{'CloudFrontDefaultCertificate':True},'WebACLId':A('WebACL'),'Origins':[{'Id':'s3','DomainName':R('MediaDomain'),'S3OriginConfig':{'OriginAccessIdentity':''},'OriginAccessControlId':R('OAC')},{'Id':'api','DomainName':S('${HttpApiId}.execute-api.us-east-2.amazonaws.com'),'CustomOriginConfig':{'OriginProtocolPolicy':'https-only','OriginSSLProtocols':['TLSv1.2']},'OriginCustomHeaders':[{'HeaderName':'X-Resonant-Origin','HeaderValue':R('OriginSecret')}]}],'DefaultCacheBehavior':base,'CacheBehaviors':[api,{**behavior(protected=False),'PathPattern':'/login/*'},{**behavior(),'PathPattern':'/library/*'},{**behavior(),'PathPattern':'/media/*'}],'CustomErrorResponses':[{'ErrorCode':403,'ErrorCachingMinTTL':0},{'ErrorCode':404,'ErrorCachingMinTTL':0}]},'Tags':TAGS})
e['FreeSubscription']=resource('PricingPlanManager::Subscription',{'PlanFamily':'CloudFront','PlanTier':'FREE','UsageLevel':'DEFAULT','ResourceArns':[S('arn:${AWS::Partition}:cloudfront::${AWS::AccountId}:distribution/${Distribution}'),A('WebACL')]})
edge=template('Resonant global edge; us-east-1; explicitly FREE subscription',{'MediaDomain':string(AllowedPattern='[a-z0-9.-]+\\.s3\\.us-east-2\\.amazonaws\\.com'),'HttpApiId':string(AllowedPattern='[a-z0-9]+'),'CookiePublicKey':string(),'OriginSecret':string(NoEcho=True,MinLength=40,MaxLength=128)},e,{'Domain':A('Distribution','DomainName'),'DistributionId':R('Distribution'),'DistributionArn':S('arn:${AWS::Partition}:cloudfront::${AWS::AccountId}:distribution/${Distribution}'),'KeyPairId':R('PublicKey'),'SubscriptionStatus':A('FreeSubscription','Status'),'SubscriptionArn':R('FreeSubscription')})
# Runtime in Ohio, after foundation and edge outputs are available.
p={k:string() for k in ['StateTable','StateBucket','HttpApiId','CodeBucket','CodeKey','CodeVersion','KeyPairId']}
p.update(RuntimeRevision=string(AllowedPattern='[a-f0-9]{64}'),ReleaseId=string(AllowedPattern='[a-f0-9]{64}'),ApiCodeSha=string(AllowedPattern='[A-Za-z0-9+/]{43}='),ImageUri=string(AllowedPattern='[0-9]{12}\\.dkr\\.ecr\\.us-east-2\\.amazonaws\\.com/[a-z0-9/_-]+@sha256:[a-f0-9]{64}'),WebOrigin=string(AllowedPattern='https://[a-z0-9]+\\.cloudfront\\.net'),SecretPrefix=string(Default='/resonant/first-release',AllowedPattern='/[a-zA-Z0-9/_-]+'),MemoryMB={'Type':'Number','Default':8192,'AllowedValues':[4096,6144,8192]},AlertEmail=string(AllowedPattern='[^ @]+@[^ @]+\\.[^ @]+'))
u={}
p['MemoryMB']['AllowedValues'].insert(0,3008)
p['WorkerConcurrency']={'Type':'Number','Default':0,'AllowedValues':[0,1],'Description':'Keep zero until measured worker acceptance; one enables processing.'}
for name in ['Api','Worker']:
 u[name+'Logs']=resource('Logs::LogGroup',{'LogGroupName':S('/aws/lambda/${AWS::StackName}-'+name.lower()),'RetentionInDays':7,'Tags':TAGS})
u['Failures']=resource('SQS::Queue',{'MessageRetentionPeriod':1209600,'SqsManagedSseEnabled':True,'Tags':TAGS})
u['Alerts']=resource('SNS::Topic',{'Tags':TAGS,'Subscription':[{'Protocol':'email','Endpoint':R('AlertEmail')}]})
dbArn=S('arn:${AWS::Partition}:dynamodb:us-east-2:${AWS::AccountId}:table/${StateTable}')
stateArn=lambda suffix:S('arn:${AWS::Partition}:s3:::${StateBucket}/'+suffix)
ssmArn=lambda suffix:S('arn:${AWS::Partition}:ssm:us-east-2:${AWS::AccountId}:parameter${SecretPrefix}/'+suffix)
def logs(name):return statement(['logs:CreateLogStream','logs:PutLogEvents'],A(name+'Logs'))
def decrypt(names):return statement('kms:Decrypt',S('arn:${AWS::Partition}:kms:us-east-2:${AWS::AccountId}:key/*'),Condition={'StringEquals':{'kms:ViaService':'ssm.us-east-2.amazonaws.com','kms:EncryptionContext:PARAMETER_ARN':[ssmArn(n) for n in names]}})
auth=['origin','password-hash','signing-key']
u['ApiRole']=role([logs('Api'),statement(['dynamodb:GetItem','dynamodb:Query','dynamodb:PutItem','dynamodb:UpdateItem','dynamodb:DeleteItem'],dbArn),statement(['s3:PutObject','s3:GetObject'],stateArn('requests/*')),statement('s3:GetObject',stateArn('results/*')),statement('ssm:GetParameters',[ssmArn(n) for n in auth]),decrypt(auth),statement('lambda:InvokeFunction',R('WorkerAlias'))])
u['WorkerRole']=role([logs('Worker'),statement('dynamodb:UpdateItem',dbArn),statement('s3:GetObject',[stateArn('requests/*'),stateArn('text-cache/*')]),statement('s3:PutObject',[stateArn('results/*'),stateArn('audits/*'),stateArn('text-cache/*')]),statement('ssm:GetParameter',ssmArn('openai')),decrypt(['openai']),statement('sqs:SendMessage',A('Failures'))])
# S3 needs ListBucket to report a missing optional cache object as 404, rather
# than the indistinguishable 403 returned without that bucket permission.
u['WorkerRole']['Properties']['Policies'][0]['PolicyDocument']['Statement'].append(statement('s3:ListBucket',S('arn:${AWS::Partition}:s3:::${StateBucket}')))
env={'RESONANT_RELEASE_ID':R('ReleaseId'),'RESONANT_STATE_TABLE':R('StateTable'),'RESONANT_STATE_BUCKET':R('StateBucket'),'RESONANT_RUNTIME_REVISION':R('RuntimeRevision')}
u['Worker']=resource('Lambda::Function',{'FunctionName':S('${AWS::StackName}-worker'),'PackageType':'Image','Code':{'ImageUri':R('ImageUri')},'Role':A('WorkerRole'),'Architectures':['x86_64'],'MemorySize':R('MemoryMB'),'Timeout':360,'ReservedConcurrentExecutions':1,'EphemeralStorage':{'Size':512},'Environment':{'Variables':{**env,'RESONANT_OPENAI_PARAMETER':S('${SecretPrefix}/openai'),'PLAYLISTIQ_CPU_THREADS':'2'}},'Tags':TAGS})
u['Worker']['Properties']['ReservedConcurrentExecutions']=R('WorkerConcurrency')
u['WorkerVersion']=resource('Lambda::Version',{'FunctionName':R('Worker'),'Description':R('RuntimeRevision')})
u['WorkerAlias']=resource('Lambda::Alias',{'FunctionName':R('Worker'),'FunctionVersion':A('WorkerVersion','Version'),'Name':'live'})
u['AsyncPolicy']=resource('Lambda::EventInvokeConfig',{'FunctionName':R('Worker'),'Qualifier':'live','MaximumEventAgeInSeconds':600,'MaximumRetryAttempts':0,'DestinationConfig':{'OnFailure':{'Destination':A('Failures')}}},DependsOn=['WorkerAlias'])
u['Api']=resource('Lambda::Function',{'FunctionName':S('${AWS::StackName}-api'),'Runtime':'nodejs24.x','Handler':'aws.main','Code':{'S3Bucket':R('CodeBucket'),'S3Key':R('CodeKey'),'S3ObjectVersion':R('CodeVersion')},'Role':A('ApiRole'),'Architectures':['x86_64'],'MemorySize':512,'Timeout':10,'ReservedConcurrentExecutions':5,'Environment':{'Variables':{**env,'RESONANT_ORIGIN':R('WebOrigin'),'RESONANT_KEY_PAIR_ID':R('KeyPairId'),'RESONANT_SECRET_PREFIX':R('SecretPrefix'),'RESONANT_WORKER_ALIAS':R('WorkerAlias')}},'Tags':TAGS})
u['ApiVersion']=resource('Lambda::Version',{'FunctionName':R('Api'),'CodeSha256':R('ApiCodeSha'),'Description':R('RuntimeRevision')})
u['ApiAlias']=resource('Lambda::Alias',{'FunctionName':R('Api'),'FunctionVersion':A('ApiVersion','Version'),'Name':'live'})
u['Integration']=resource('ApiGatewayV2::Integration',{'ApiId':R('HttpApiId'),'IntegrationType':'AWS_PROXY','IntegrationUri':R('ApiAlias'),'PayloadFormatVersion':'2.0','TimeoutInMillis':10000})
u['ApiInvoke']=resource('Lambda::Permission',{'FunctionName':R('ApiAlias'),'Action':'lambda:InvokeFunction','Principal':'apigateway.amazonaws.com','SourceArn':S('arn:${AWS::Partition}:execute-api:us-east-2:${AWS::AccountId}:${HttpApiId}/*')})
routes=['POST /api/session/login','GET /api/session','POST /api/session/refresh','POST /api/session/logout','POST /api/playlist','GET /api/jobs/{id}','GET /api/profile','POST /api/profile']
for i,route in enumerate(routes):u['Route'+str(i)]=resource('ApiGatewayV2::Route',{'ApiId':R('HttpApiId'),'RouteKey':route,'Target':S('integrations/${Integration}')})
u['Stage']=resource('ApiGatewayV2::Stage',{'ApiId':R('HttpApiId'),'StageName':'$default','AutoDeploy':True,'DefaultRouteSettings':{'ThrottlingRateLimit':10,'ThrottlingBurstLimit':20},'RouteSettings':{'POST /api/session/login':{'ThrottlingRateLimit':1,'ThrottlingBurstLimit':5}}},DependsOn=['Route'+str(i) for i in range(len(routes))])
for name,namespace,metric,dims,threshold,stat in [('ApiErrors','AWS/ApiGateway','5xx',[{'Name':'ApiId','Value':R('HttpApiId')},{'Name':'Stage','Value':'$default'}],1,'Sum'),('WorkerErrors','AWS/Lambda','Errors',[{'Name':'FunctionName','Value':R('Worker')}],1,'Sum'),('AsyncAge','AWS/Lambda','AsyncEventAge',[{'Name':'FunctionName','Value':R('Worker')}],300000,'Maximum'),('FailureQueue','AWS/SQS','ApproximateNumberOfMessagesVisible',[{'Name':'QueueName','Value':A('Failures','QueueName')}],1,'Maximum')]:
 u[name]=resource('CloudWatch::Alarm',{'Namespace':namespace,'MetricName':metric,'Dimensions':dims,'Statistic':stat,'Period':300,'EvaluationPeriods':1,'Threshold':threshold,'ComparisonOperator':'GreaterThanOrEqualToThreshold','TreatMissingData':'notBreaching','AlarmActions':[R('Alerts')]})
u['Budget']=resource('Budgets::Budget',{'Budget':{'BudgetName':S('${AWS::StackName}-account-alert'),'BudgetType':'COST','TimeUnit':'MONTHLY','BudgetLimit':{'Amount':10,'Unit':'USD'}},'NotificationsWithSubscribers':[{'Notification':{'ComparisonOperator':'GREATER_THAN','NotificationType':'ACTUAL','Threshold':amount,'ThresholdType':'ABSOLUTE_VALUE'},'Subscribers':[{'SubscriptionType':'EMAIL','Address':R('AlertEmail')}]} for amount in [5,10]]})
for name in ['WorkerVersion','ApiVersion']:
 u[name].update(DeletionPolicy='Retain',UpdateReplacePolicy='Retain')
runtime=template('Resonant Ohio runtime; durable asynchronous jobs; no idle worker',p,u,{'ApiAlias':R('ApiAlias'),'WorkerAlias':R('WorkerAlias'),'FailureQueue':R('Failures'),'Alerts':R('Alerts')})
# An optional exact custom origin preserves the original CloudFront hostname.
for t in [foundation,runtime]:
 t['Parameters']['AdditionalWebOrigin']=string(Default='',AllowedPattern='(|https://[a-z0-9.-]+)')
foundation['Conditions']['HasAdditionalOrigin']={'Fn::Not':[{'Fn::Equals':[R('AdditionalWebOrigin'),'']}]}
f['StateBucket']['Properties']['CorsConfiguration']['CorsRules'][0]['AllowedOrigins'].append({'Fn::If':['HasAdditionalOrigin',R('AdditionalWebOrigin'),R('AWS::NoValue')]})
u['Api']['Properties']['Environment']['Variables']['RESONANT_ADDITIONAL_ORIGINS']=R('AdditionalWebOrigin')
edge['Parameters'].update(CustomDomain=string(Default='',AllowedPattern='(|[a-z0-9.-]+)'),CertificateArn=string(Default='',AllowedPattern='(|arn:aws:acm:us-east-1:[0-9]{12}:certificate/[a-z0-9-]+)'))
edge['Conditions']={'HasCustomDomain':{'Fn::Not':[{'Fn::Equals':[R('CustomDomain'),'']}]}}
distribution=e['Distribution']['Properties']['DistributionConfig']
distribution['Aliases']={'Fn::If':['HasCustomDomain',[R('CustomDomain')],R('AWS::NoValue')]}
distribution['ViewerCertificate']={'Fn::If':['HasCustomDomain',{'AcmCertificateArn':R('CertificateArn'),'SslSupportMethod':'sni-only','MinimumProtocolVersion':'TLSv1.2_2021'},{'CloudFrontDefaultCertificate':True}]}
if __name__=='__main__':
 for name,value in [('foundation',foundation),('edge',edge),('runtime',runtime)]:
  Path(__file__).with_name(name+'-template.json').write_text(json.dumps(value,indent=2)+'\n')
 print('Generated foundation, edge and runtime templates; no AWS calls.')
