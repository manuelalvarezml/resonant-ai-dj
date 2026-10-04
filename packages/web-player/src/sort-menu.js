export function mountSortMenu(select){
 const old=select.closest('.sort-field'),root=document.createElement('div');root.className='sort-field custom-sort';
 old.replaceWith(root);select.hidden=true;root.append(select);
 const trigger=document.createElement('button');trigger.type='button';trigger.className='sort-trigger';trigger.textContent='Sort By';trigger.setAttribute('aria-haspopup','listbox');trigger.setAttribute('aria-expanded','false');
 const menu=document.createElement('div');menu.className='sort-options';menu.id='sort-options';menu.role='listbox';menu.setAttribute('aria-label','Sort tracks by');menu.hidden=true;trigger.setAttribute('aria-controls',menu.id);root.append(trigger,menu);
 const close=()=>{menu.hidden=true;trigger.setAttribute('aria-expanded','false');};
 const open=()=>{menu.replaceChildren();for(const option of select.options){if(option.hidden)continue;const b=document.createElement('button');b.type='button';b.role='option';b.textContent=option.textContent;b.setAttribute('aria-selected',String(select.value===option.value));b.onclick=()=>{select.value=option.value;trigger.title='Sorted by '+option.textContent;close();select.dispatchEvent(new Event('change'));trigger.focus();};menu.append(b);}menu.hidden=false;trigger.setAttribute('aria-expanded','true');};
 trigger.onclick=()=>menu.hidden?open():close();
 root.onkeydown=event=>{if(event.key==='Escape'){close();trigger.focus();}else if(['ArrowDown','ArrowUp','Home','End'].includes(event.key)){event.preventDefault();if(menu.hidden)open();const options=[...menu.children],i=options.indexOf(document.activeElement),next=event.key==='Home'?0:event.key==='End'?options.length-1:Math.max(0,Math.min(options.length-1,i+(event.key==='ArrowDown'?1:-1)));options[next]?.focus();}};
 document.addEventListener('click',event=>{if(!root.contains(event.target))close();});document.addEventListener('focusin',event=>{if(!root.contains(event.target))close();});
}
