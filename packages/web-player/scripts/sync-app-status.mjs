import {readFile,writeFile} from 'node:fs/promises';
const root=new URL('../',import.meta.url);
const data=JSON.parse(await readFile(new URL('public/app-status.json',root),'utf8'));
let md=`# App status\n\nMaintained snapshot: ${data.updated}.\n\n${data.summary}\n\n`;
for(const section of data.sections){md+=`## ${section.title}\n\n`+section.items.map((text,i)=>`${section.ordered?`${i+1}.`:'-'} ${text}\n`).join('')+'\n';}
md+='## Maintenance contract\n\nUpdate public/app-status.json whenever capabilities, models, prompt interpretation, matching policy, storage, known limitations or next steps change. Run npm run build to regenerate this Markdown counterpart. Record the user steer, implementation and verification in WORK_LOG.md and the corresponding project plans, takeovers and decision/experiment logs. Keep snapshot statements distinct from live browser counts.\n\nSpectrum reference: https://www.w3.org/TR/webaudio-1.0/#fft-windowing-and-smoothing\n';
await writeFile(new URL('docs/APP_STATUS.md',root),md);
