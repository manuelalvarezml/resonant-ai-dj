import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const root=process.argv[2] || fileURLToPath(new URL('../',import.meta.url)).replace(/\/$/,'');
const out=root+'/economics';
const data=JSON.parse(await fs.readFile(out+'/inputs.json','utf8'));
const sources=JSON.parse(await fs.readFile(root+'/sources.json','utf8')).sources;
const wb=Workbook.create();
const model=wb.worksheets.add('Model'), inputs=wb.worksheets.add('Inputs'), source=wb.worksheets.add('Sources');
const val=(s,a,v)=>s.getRange(a).values=[[v]];
const form=(s,a,f)=>s.getRange(a).formulas=[[f]];
const hdr=(s,r,last=4)=>{const x=s.getRangeByIndexes(r-1,0,1,last);x.format.fill='#333333';x.format.font.color='#FFFFFF';x.format.font.bold=true;};
for(const s of [model,inputs,source]){
  s.showGridLines=false;
  const n=s===inputs?96:s===source?30:70;
  const all=s.getRange('A1:E'+n);
  all.format.font.name='Arial'; all.format.font.size=10; all.format.font.color='#222222';
  all.format.rowHeight=21; all.format.verticalAlignment='center';
  s.getRange('A1:A'+n).format.columnWidth=45;
  s.getRange('B1:B'+n).format.columnWidth=19;
  s.getRange('C1:C'+n).format.columnWidth=22;
  s.getRange('D1:D'+n).format.columnWidth=37;
  s.getRange('E1:E'+n).format.columnWidth=3;
}
val(inputs,'A2','Scenario inputs');inputs.getRange('A2').format.font.size=14;
val(inputs,'A4','Case selected (1–3)');val(inputs,'B4',data.selected_case);
inputs.getRange('B4').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:3}};
form(inputs,'C4','=CHOOSE(B4,"Small pilot","Medium library","Large DJ library")');
val(inputs,'A5','Blue = editable. Active rows feed one model.');
const refs={};let row=7;
for(const [id,label,unit,cases] of data.drivers){
 refs[id]=row;
 val(inputs,'A'+row,label+' — active');val(inputs,'C'+row,unit);
 form(inputs,'B'+row,'=IF(ISNUMBER(CHOOSE($B$4,B'+(row+1)+',B'+(row+2)+',B'+(row+3)+')),CHOOSE($B$4,B'+(row+1)+',B'+(row+2)+',B'+(row+3)+'),"n.a.")');
 inputs.getRange('A'+row+':C'+row).format.fill='#E8E8E8';inputs.getRange('A'+row+':C'+row).format.font.bold=true;
 cases.forEach((v,i)=>{val(inputs,'A'+(row+i+1),data.cases[i]);val(inputs,'B'+(row+i+1),v);inputs.getRange('B'+(row+i+1)).format.font.color='#0000FF';});
 row+=4;
}
row=41;inputs.getRange('A40:D40').values=[['Common driver','Value','Unit','Evidence']];hdr(inputs,40);
for(const [id,label,value,unit,evidence] of data.assumptions){
 refs[id]=row; inputs.getRange('A'+row+':D'+row).values=[[label,value,unit,evidence]];
 inputs.getRange('B'+row).format.font.color='#0000FF';
 inputs.getRange('B'+row).setNumberFormat('0.0000');
 row++;
}
inputs.getRange('B4').format.font.color='#0000FF';inputs.freezePanes.freezeRows(5);
const R=id=>"'Inputs'!B"+refs[id];
val(model,'A2','Cloud library monthly economics');model.getRange('A2').format.font.size=14;
val(model,'A4','Case selected');form(model,'B4',"='Inputs'!C4");model.getRange('B4').format.font.color='#008000';model.getRange('B4').format.columnWidth=22;
val(model,'A5','USD scenarios. Unmeasured operating inputs.');
model.getRange('A7:C7').values=[['Workload','Value','Unit']];hdr(model,7,3);
const calc=[
[8,'Paying users','='+R('users'),'users'],
[9,'Original stored bytes','='+R('users')+'*'+R('original_gb'),'decimal GB'],
 [10,'Derivatives and retained mixes','=B9*'+R('derivative_ratio')+'+B8*'+R('mixes')+'*('+R('mix_gb')+'+'+R('master_gb')+')','decimal GB'],
[11,'Total primary average storage','=SUM(B9:B10)','decimal GB'],
[12,'Playback delivery','=B8*'+R('listening_hours')+'*'+R('audio_gb_hour'),'GB/month'],
[13,'Mix downloads','=B8*'+R('mixes')+'*'+R('mix_gb'),'GB/month'],
[14,'Worker reads and original exports','=B9*('+R('worker_read_ratio')+'+'+R('export_ratio')+')','GB/month'],
[15,'Total origin outbound','=SUM(B12:B14)','GB/month'],
[16,'First upload duration per user','='+R('original_gb')+'*8000/('+R('uplink')+'*'+R('upload_efficiency')+'*3600)','hours'],
];
for(const [r,l,f,u]of calc){val(model,'A'+r,l);form(model,'B'+r,f);val(model,'C'+r,u);}
model.getRange('A18:D18').values=[['Provider alternative','Monthly USD','Estimate type','Caveat']];hdr(model,18);
form(model,'B19','=B11*'+R('r2_storage')+'+B8*('+R('class_a')+'*'+R('r2_a')+'+'+R('class_b')+'*'+R('r2_b')+')/1000000');
form(model,'B20','=B11*'+R('b2_storage')+'+MAX(B15-B11*'+R('b2_allowance')+',0)*'+R('b2_egress'));
form(model,'B21','='+R('spaces_base')+'+MAX(B11/1.073741824-'+R('spaces_storage_allow')+',0)*'+R('spaces_storage')+'+MAX(B15/1.073741824-'+R('spaces_transfer_allow')+',0)*'+R('spaces_egress'));
form(model,'B22','='+R('supabase_base')+'+MAX(B11-'+R('supabase_storage_allow')+',0)*'+R('supabase_storage')+'+MAX(B15*'+R('supabase_hit')+'-'+R('supabase_transfer_allow')+',0)*'+R('supabase_cached')+'+MAX(B15*(1-'+R('supabase_hit')+')-'+R('supabase_transfer_allow')+',0)*'+R('supabase_uncached'));
form(model,'B23','=MAX(B11/1099.511627776,1)*'+R('wasabi_base'));val(model,'B24','n.a.');
const names=[['R2 Standard','Marginal estimate','No free tier / rounding'],['B2 pay-go','Marginal estimate','No free tier / event fees'],['Spaces Standard','Bundle estimate','Account bundle used once'],['Supabase Pro Storage','Bundle estimate','Other project charges excluded'],['Wasabi pay-go','Storage base only','No early-delete charges'],['AWS S3 Standard','Quote needed','Region unresolved']];
names.forEach((x,i)=>{val(model,'A'+(19+i),x[0]);val(model,'C'+(19+i),x[1]);val(model,'D'+(19+i),x[2]);});
val(model,'A26','Wasabi recurring egress fit');form(model,'B26','=IF(B15>B11,"Outside policy fit","Within volume guide")');
model.getRange('A28:C28').values=[['Service scenario using B2','Monthly USD','Basis']];hdr(model,28,3);
const fm={
29:['Primary storage and origin delivery','=B20','Provider estimate above'],
30:['Backup original copy','=B9*'+R('backup_ratio')+'*'+R('b2_storage'),'One retained copy'],
31:['New-track analysis','=B8*'+R('new_tracks')+'*'+R('analysis_minutes')+'/60*'+R('worker_rate')+'*'+R('retry_factor'),'Unmeasured runtime'],
32:['Mix rendering','=B8*'+R('mixes')+'*'+R('render_minutes')+'/60*'+R('worker_rate')+'*'+R('retry_factor'),'Unmeasured runtime'],
33:['Worker outbound writes','=B8*('+R('new_tracks')+'*('+R('original_gb')+'/'+R('initial_tracks')+')*'+R('derivative_ratio')+'+'+R('mixes')+'*('+R('mix_gb')+'+'+R('master_gb')+'))*'+R('worker_egress_rate'),'Separate cloud transfer'],
34:['Language model requests','=B8*'+R('calls')+'*('+R('input_tokens')+'*'+R('input_rate')+'+'+R('output_tokens')+'*'+R('output_rate')+')/1000000','Token scenario'],
35:['Support','=B8*'+R('support_minutes')+'/60*'+R('support_rate'),'Unmeasured workload'],
36:['Variable subtotal','=SUM(B29:B35)',''],
37:['Contingency','=B36*'+R('contingency'),'Editable risk allowance'],
38:['Fixed operations','='+R('fixed_ops'),'Unquoted allowance'],
39:['Recurring cost before payments','=SUM(B36:B38)','Excludes legal/license/tax'],
40:['Gross subscription revenue','=B8*'+R('price'),'Hypothetical price'],
41:['Payment expense','=B40*'+R('payment_pct')+'+B8*'+R('payment_fixed'),'Unquoted merchant rate'],
42:['Recurring contribution','=B40-B39-B41','Before acquisition/setup'],
43:['Recurring contribution margin','=IF(B40=0,"n.a.",B42/B40)','Not validated'],
45:['Initial analysis cash cost','=B8*'+R('initial_tracks')+'*'+R('analysis_minutes')+'/60*'+R('worker_rate')+'*'+R('retry_factor'),'One time, not monthly'],
46:['Acquisition cash cost','=B8*'+R('acquisition'),'One time, unmeasured'],
47:['Monthly acquisition/setup allocation','=SUM(B45:B46)/'+R('retained_months'),'Amortization assumption'],
48:['Contribution after allocation','=B42-B47','Not accounting profit'],
49:['Monthly per-user cost with allocation','=IF(B8=0,"n.a.",(B39+B41+B47)/B8)','Scenario only'],
50:['Upfront acquisition + initial analysis','=SUM(B45:B46)','Cash requirement'],
};
for(const [r,[l,f,n]]of Object.entries(fm)){val(model,'A'+r,l);form(model,'B'+r,f);val(model,'C'+r,n);}
val(model,'A53','Excluded: licenses, tax, legal/security, maintenance.');
val(model,'A54','Initial full-library analysis is an optional future feature.');
val(model,'A55','Edit Inputs; reconcile accepted changes to inputs.json.');
val(model,'A56','Free users, churn and backfills need separate forecasts.');
model.getRange('B8:B50').setNumberFormat('#,##0.00;(#,##0.00);"-"');
model.getRange('B43').setNumberFormat('0.0%;(0.0%);"-"');
for(const r of [11,15,39,42,43,48,50])model.getRange('A'+r+':C'+r).format.font.bold=true;
model.getRange('B42:B43').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#9C0006'},fill:'#FCE4D6'}});
model.getRange('B48').conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#9C0006'},fill:'#FCE4D6'}});
model.getRange('A53:D56').format.font.size=10;
source.getRange('A1:A30').format.columnWidth=12;source.getRange('B1:B30').format.columnWidth=38;source.getRange('C1:C30').format.columnWidth=90;
val(source,'A2','Sources');source.getRange('A2').format.font.size=14;
source.getRange('A4:C4').values=[['ID','Publisher / source','Original URL']];hdr(source,4,3);
const used=['S001','S002','S004','S007','S009','S010','S011','S045'];
used.forEach((id,i)=>{const x=sources.find(s=>s.id===id);source.getRange('A'+(5+i)+':C'+(5+i)).values=[[id,x.publisher+' — '+x.title,x.url]];});
source.getRange('B5:C12').format.wrapText=true;source.getRange('A5:C12').format.rowHeight=40;
val(source,'B15','Accessed 2026-09-08. Recheck before procurement.');
val(source,'B17','Assumptions are not observed usage or price quotes.');
val(source,'B19','Full source inventory is in SOURCES.md and sources.json.');
source.freezePanes.freezeRows(4);
wb.recalculate();
const snapshots=[];
for(let c=1;c<=3;c++){val(inputs,'B4',c);wb.recalculate();snapshots.push({case:data.cases[c-1],model_values:model.getRange('A8:C50').values});}
val(inputs,'B4',2);wb.recalculate();
const baseline=model.getRange('B11').values[0][0];
const driverRow=refs.original_gb+2;
const old=inputs.getRange('B'+driverRow).values[0][0];
val(inputs,'B'+driverRow,old*2);wb.recalculate();
if(!(model.getRange('B11').values[0][0]>baseline))throw Error('Input edit did not update storage');
val(inputs,'B'+driverRow,old);
const priceRow=refs.price+2, oldPrice=inputs.getRange('B'+priceRow).values[0][0];
val(inputs,'B'+priceRow,0);wb.recalculate();
if(model.getRange('B43').values[0][0]!=='n.a.')throw Error('Zero revenue guard failed');
val(inputs,'B'+priceRow,oldPrice);
inputs.getRange('B'+refs.b2_storage).setNumberFormat('0.00000');
const unselectedRow=refs.original_gb+1;
const unselectedValue=inputs.getRange('B'+unselectedRow).values[0][0];
val(inputs,'B'+unselectedRow,null);wb.recalculate();
if(model.getRange('B11').values[0][0]!==baseline)throw Error('Unselected blank changed active case');
val(inputs,'B4',1);wb.recalculate();
if(inputs.getRange('B'+refs.original_gb).values[0][0]!=='n.a.')throw Error('Selected blank was treated as zero');
val(inputs,'B'+unselectedRow,unselectedValue);val(inputs,'B4',2);
wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'formula errors'});
console.log(errors.ndjson);
console.log((await wb.inspect({kind:'table',range:'Model!A39:C50',include:'values,formulas',tableMaxRows:12,tableMaxCols:3,maxChars:3500})).ndjson);
await fs.mkdir(out,{recursive:true});
await fs.writeFile(out+'/calculated.json',JSON.stringify({as_of:data.as_of,selected_case:2,snapshots,checks:{case_recalculation:true,changed_storage_driver:true,zero_revenue_guard:true,formula_error_scan:errors.ndjson},upload_hours:[25,100,500,1000].map(gb=>({gb,at_5_mbps:gb*8000/(5*.7*3600),at_20_mbps:gb*8000/(20*.7*3600),at_100_mbps:gb*8000/(100*.7*3600)}))},null,2));
await fs.mkdir(out+'/previews',{recursive:true});
for(const [name,range,label] of [['Model','A1:D27','model-storage'],['Model','A28:D56','model-service'],['Inputs','A1:D39','inputs-cases'],['Inputs','A40:D64','inputs-ops'],['Inputs','A65:D87','inputs-rates'],['Sources','A1:C20','sources']]){
 const blob=await wb.render({sheetName:name,range,scale:1.4});
 await fs.writeFile(out+'/previews/'+label+'.png',new Uint8Array(await blob.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(out+'/UNIT_ECONOMICS.xlsx');
console.log('Exported workbook and checked calculations.');
