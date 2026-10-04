import {cloudConfig,createCloudServer} from './cloud-server.mjs';

try{
  const config=cloudConfig();
  if(!process.env.AUTODJ_OPENAI_API_DEV_KEY)throw Error('Missing project OpenAI environment key.');
  const app=await createCloudServer(config);
  app.server.listen(config.port,config.listenHost,()=>console.log(`Resonant release ${app.release.manifest.releaseId}: ${app.release.tracks.size} tracks; listening on port ${config.port}.`));
  let stopping=false;
  const stop=async()=>{if(stopping)return;stopping=true;await app.close();};
  process.on('SIGTERM',()=>void stop());process.on('SIGINT',()=>void stop());
  app.server.on('error',()=>{console.error('Production listener failed.');process.exitCode=1;void stop();});
}catch(error){console.error(error.message);process.exitCode=1;}
