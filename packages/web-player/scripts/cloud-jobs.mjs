import {spawn} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {mkdir,readFile,writeFile,rename,rm,stat} from 'node:fs/promises';
import path from 'node:path';

function signalTree(child,signal){
  if(!child.pid)return;
  try{process.kill(-child.pid,signal);}catch(error){if(error.code!=='ESRCH')throw error;}
}
async function reapTree(child){
  if(!child.pid)return;
  signalTree(child,'SIGKILL');
  for(let attempt=0;attempt<200;attempt++){
    try{process.kill(-child.pid,0);}catch(error){if(error.code==='ESRCH')return;throw error;}
    await new Promise(resolve=>setTimeout(resolve,25));
  }
  throw Object.assign(Error('Worker process group did not exit.'),{unsafeWorkerTree:true});
}

// One process group contains the bridge and any bounded text encoder child.
// Do not free the slot on timeout until close confirms the worker is reaped.
export function pythonJob(config,input,output){
  const child=spawn(config.python,['-m','prompt_to_playlist.cloud_bridge','prompt',
    '--release-dir',config.releaseRoot,'--state-dir',config.stateRoot,
    '--model-dir',config.modelRoot,'--input',input,'--out',output],{
    detached:true,stdio:['ignore','ignore','ignore'],
    env:{...process.env,PYTHONUNBUFFERED:'1',OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2'},
  });
  let cancelled=false,forceTimer;
  const done=new Promise((resolve,reject)=>{
    child.once('error',()=>reject(new Error('Playlist worker could not start.')));
    child.once('close',async(code)=>{
      clearTimeout(forceTimer);
      // Also remove orphan descendants if an unexpected parent exit occurred.
      try{
        await reapTree(child);
        if(cancelled||code!==0)reject(new Error(cancelled?'Playlist request timed out.':'Playlist worker failed.'));
        else resolve();
      }catch(error){reject(error);}
    });
  });
  const cancel=()=>{
    if(cancelled)return;cancelled=true;signalTree(child,'SIGTERM');
    forceTimer=setTimeout(()=>signalTree(child,'SIGKILL'),1000);forceTimer.unref();
  };
  return {done,cancel};
}

export async function createJobs(config,{runner=pythonJob,now=()=>Date.now()}={}){
  const dir=path.join(config.stateRoot,'jobs');await mkdir(dir,{recursive:true,mode:0o700});
  const quotaPath=path.join(config.stateRoot,'prompt-quota.json');
  let quota={date:'',count:0};
  try{
    quota=JSON.parse(await readFile(quotaPath,'utf8'));
    if(!/^\d{4}-\d{2}-\d{2}$/.test(quota.date)||!Number.isSafeInteger(quota.count)||quota.count<0)throw Error('Invalid quota');
  }catch(error){if(error.code!=='ENOENT')throw Error('Cannot read persisted prompt quota; repair before starting.');}
  let active=null,closed=false;const jobs=new Map();
  const cleanup=()=>{for(const [id,j]of jobs)if(j.expires<now()&&j!==active)jobs.delete(id);};
  async function start(payload,owner){
    if(closed)throw Object.assign(Error('Server is stopping.'),{status:503});
    if(active)throw Object.assign(Error('Another playlist is being prepared. Please try again shortly.'),{status:409});
    cleanup();
    const day=new Date(now()).toISOString().slice(0,10);
    if(quota.date!==day)quota={date:day,count:0};
    if(quota.count>=config.dailyLimit)throw Object.assign(Error('Today’s playlist request limit has been reached.'),{status:429});
    const id=randomUUID(),job={id,owner,status:'running',message:'Preparing your playlist…',expires:now()+3600000};
    let ready;job.ready=new Promise(resolve=>{ready=resolve;});
    active=job;jobs.set(id,job);
    const work=path.join(dir,id),input=path.join(work,'request.json'),output=path.join(work,'response.json');
    try{
      quota.count++;
      await writeFile(quotaPath+'.tmp',JSON.stringify(quota),{mode:0o600});await rename(quotaPath+'.tmp',quotaPath);
      await mkdir(work,{mode:0o700});await writeFile(input,JSON.stringify(payload),{mode:0o600});
      if(closed)throw Error('Server is stopping.');
      const worker=runner(config,input,output);job.cancel=worker.cancel;
      const timer=setTimeout(()=>{job.timedOut=true;worker.cancel();},config.jobTimeoutMs);timer.unref();
      job.finished=(async()=>{
        try{
          await worker.done;
          if(job.timedOut)throw Error('Timeout');
          const info=await stat(output);if(info.size>16*1024*1024)throw Error('Oversized response');
          const response=JSON.parse(await readFile(output,'utf8'));
          if(response.error||!response.result)throw Error('Invalid worker response');
          job.status='complete';job.result=response.result;job.message='Playlist ready.';
        }catch(error){
          if(error.unsafeWorkerTree)closed=true;
          job.status='failed';job.error=job.timedOut?'Playlist request timed out. Please retry.':'Playlist preparation failed. Please retry or contact the owner.';
        }finally{
          clearTimeout(timer);await rm(work,{recursive:true,force:true});
          job.expires=now()+3600000;active=null;
        }
      })();
      ready();return {id};
    }catch{
      jobs.delete(id);await rm(work,{recursive:true,force:true});active=null;ready();
      throw Object.assign(Error('Unable to start playlist preparation.'),{status:503});
    }
  }
  return {
    start,
    get(id,owner){cleanup();const j=jobs.get(id);if(!j||j.owner!==owner)return null;return {id:j.id,status:j.status,message:j.message,...(j.result?{result:j.result}:{}),...(j.error?{error:j.error}:{})};},
    async close(){closed=true;const job=active;if(job){await job.ready;job.cancel?.();await job.finished;}},
  };
}
