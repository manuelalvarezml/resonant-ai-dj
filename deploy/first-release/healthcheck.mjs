import http from 'node:http';
const origin = new URL(process.env.RESONANT_PUBLIC_ORIGIN);
const request = http.get({hostname:'127.0.0.1',port:Number(process.env.RESONANT_PORT || 4175),path:'/healthz',headers:{host:origin.host,'x-resonant-proxy-token':process.env.RESONANT_PROXY_TOKEN}}, response => {
  response.resume();
  process.exitCode=response.statusCode===200 ? 0 : 1;
});
request.setTimeout(4000,()=>request.destroy());
request.on('error',()=>{process.exitCode=1;});
