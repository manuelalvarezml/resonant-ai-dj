// Verified equal encoded MP3 packets, never a title/artist heuristic.
// All 187 published streams were hashed without decoding on 2026-10-03.
// One duplicate pair; originals and IDs remain intact. See WEB_REFRESH_2026-10-03.md.
const aliases=new Map([
 ['4d1b398a896faa64804dea2b7ccdc59ac416be35b23bbe84b90e9f1b42d25e24',
  'b23cf7fc573254db349ab179fdcc406c5da159186b04b1fe914ff913d83e4ae2']
]);
export const canonicalAudioHash=hash=>aliases.get(hash)??hash;
