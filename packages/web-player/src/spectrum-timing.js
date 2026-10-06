// Keep the fractional frame budget instead of restarting it at each callback.
// Otherwise a 50 ms gate on a 30 Hz display unintentionally becomes 15 fps.
export function advanceSpectrumFrame(previous, now, interval) {
  const steps=Math.floor((now-previous+0.001)/interval);
  return steps>0?Math.min(now,previous+steps*interval):null;
}
