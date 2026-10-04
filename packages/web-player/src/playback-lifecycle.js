// pagehide/visibilitychange can mean app switching or bfcache, not user intent
// to stop. Never clear a live queue or revoke its URL on those lifecycle events.
export function bindPlaybackLifecycle(player,{page=globalThis.window,document=globalThis.document}={}){
 const reconcile=()=>{if(!document.hidden)player.reconcile();};
 page.addEventListener('pageshow',reconcile);document.addEventListener('visibilitychange',reconcile);
 return ()=>{page.removeEventListener('pageshow',reconcile);document.removeEventListener('visibilitychange',reconcile);};
}
