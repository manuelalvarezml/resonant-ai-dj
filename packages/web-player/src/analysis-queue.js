export const isStorageFailure=error=>error?.code==='LIBRARY_STORAGE_UNAVAILABLE';
// Storage failure affects every later item; do not misreport the entire queue as model failures.
export async function runAnalysisQueue(items,process){
 const errors=[];let paused=false,completed=0;
 for(const [index,item] of items.entries()){
  try{await process(item,index);completed++;}
  catch(error){errors.push({item,error});if(isStorageFailure(error)){paused=true;break;}}
 }
 return {errors,paused,completed};
}
