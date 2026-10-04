import {createReadStream, constants} from 'node:fs';
import {copyFile, lstat, mkdir, readFile, readdir, rename, rm, writeFile} from 'node:fs/promises';
import {createHash, randomUUID} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {fullyAnalyzed, RELEASE_STAGES} from '../src/release-policy.js';

const project = fileURLToPath(new URL('../../..', import.meta.url));
const packageRoot = fileURLToPath(new URL('..', import.meta.url));
const mixKey = '12fd88424ba311ff55d3d55d85a9a169d095e61620099f4a3ac6698971350b41';
const hashPattern = /^[a-f0-9]{64}$/;
export const RELEASE_SCHEMA = 'resonant/cloud-release/1';
const json = value => `${JSON.stringify(value, null, 2)}\n`;
const hashBytes = value => createHash('sha256').update(value).digest('hex');
const readJson = async file => JSON.parse(await readFile(file, 'utf8'));
const hasPrivatePath = value => /\/(?:Users|home|private|var|tmp|opt|etc|root|srv|mnt)\/|[A-Za-z]:[\\/]|file:\/\/|\\\\[^\\]+\\/.test(value);
const secretPattern = /\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----/;

// Keep display evidence while removing machine diagnostics, embeddings and opaque tags.
// Exact original cache bytes remain in private/features for the planner and audit.
export function sanitizePublic(value) {
  if (typeof value === 'string') return hasPrivatePath(value) || secretPattern.test(value) ? undefined : value;
  if (Array.isArray(value)) return value.map(sanitizePublic).filter(item => item !== undefined);
  if (!value || typeof value !== 'object') return value;
  const output = {};
  for (const [key, item] of Object.entries(value)) {
    if (/^(?:metrics|implementation|implementation_version|encoded_tags|error|path|source_path|source|filename|file_path|embedding|embeddings|audio_embedding|text_embedding|api_key|token|password|secret|credentials)$/i.test(key)) continue;
    const clean = sanitizePublic(item);
    if (clean !== undefined) output[key] = clean;
  }
  return output;
}

export function safeReleasePath(relative) {
  if (typeof relative !== 'string' || !relative || relative.includes('\\') || relative.includes('\0') || path.posix.isAbsolute(relative) || relative.split('/').some(part => !part || part === '.' || part === '..') || /^[A-Za-z]:/.test(relative)) throw Error('Unsafe release path');
  return relative;
}

export async function digestFile(file) {
  const stat = await lstat(file);
  if (!stat.isFile() || stat.isSymbolicLink()) throw Error('Release inputs must be regular files');
  const hash = createHash('sha256');
  let bytes = 0;
  for await (const chunk of createReadStream(file)) { hash.update(chunk); bytes += chunk.length; }
  if (bytes !== stat.size) throw Error('File changed while hashing');
  return {sha256: hash.digest('hex'), bytes};
}

async function copyVerified(source, destination, expected) {
  const before = await digestFile(source);
  if (expected && before.sha256 !== expected) throw Error('Source hash does not match its published identity');
  await mkdir(path.dirname(destination), {recursive: true});
  await copyFile(source, destination, constants.COPYFILE_EXCL);
  const after = await digestFile(destination);
  if (after.sha256 !== before.sha256 || after.bytes !== before.bytes) throw Error('Copied file failed checksum verification');
  // Re-read the source to prove that the exported original stayed unchanged.
  const sourceAfter = await digestFile(source);
  if (sourceAfter.sha256 !== before.sha256) throw Error('Original source changed during export');
  return after;
}

async function walk(root, prefix = '') {
  const files = [];
  for (const entry of (await readdir(path.join(root, prefix), {withFileTypes: true})).sort((a, b) => a.name.localeCompare(b.name))) {
    const relative = safeReleasePath(prefix ? `${prefix}/${entry.name}` : entry.name);
    if (entry.isSymbolicLink()) throw Error('Symlinks are not allowed in release bundles');
    if (entry.isDirectory()) files.push(...await walk(root, relative));
    else if (entry.isFile()) files.push(relative);
    else throw Error('Unsupported release entry');
  }
  return files;
}

export function mixMetadata(manifest, graph) {
  if (manifest.status !== 'complete' || !hashPattern.test(manifest.hashes?.['stream.m4a'] ?? '')) throw Error('The selected mix is not complete and hashed');
  const starts = [...graph.matchAll(/\[h(\d+)_out_prefix_source\]atrim=end=([0-9.]+)/g)];
  const durations = new Map([...graph.matchAll(/\[h(\d+)_in_transition_source\]atrim=end=([0-9.]+)/g)].map(match => [match[1], Number(match[2])]));
  const transitions = starts.map(match => ({start_s: Number(match[2]), end_s: Number((Number(match[2]) + durations.get(match[1])).toFixed(6))}));
  if (transitions.length !== 2 || transitions.some(t => !Number.isFinite(t.end_s) || t.start_s < 0 || t.end_s <= t.start_s || t.end_s > manifest.duration_s)) throw Error('Expected two valid graph-derived mix transitions');
  return {title: 'Three-track house mix', duration_s: manifest.duration_s, url: '/api/web/mix/audio', transitions, tracks: ['My Paradise – Edit', 'Rock the House', 'Lemon8']};
}

async function copyStatic(staticDir, destination) {
  const manifest = await readJson(path.join(staticDir, 'build-manifest.json'));
  const config = await readJson(path.join(staticDir, 'config.json'));
  if (config.edition !== 'web' || config.mode !== 'http') throw Error('Build the web edition before exporting');
  for (const [relative, sha256] of Object.entries(manifest.files)) {
    safeReleasePath(relative);
    if (['catalog.json', 'mix.json', 'prepare-web.html', 'app-status.json'].includes(relative) || !hashPattern.test(sha256)) throw Error('Unexpected static build entry');
    await copyVerified(path.join(staticDir, relative), path.join(destination, relative), sha256);
  }
  await copyVerified(path.join(staticDir, 'build-manifest.json'), path.join(destination, 'build-manifest.json'));
}

function eligibilityReason(features) {
  if (features.feature_version !== 'selected-estimators-v3-character120') return 'outdated-feature-version';
  if (features.status !== 'complete') return 'incomplete-analysis';
  if (features.policy !== 'maest-top6-v1') return 'incompatible-policy';
  if (!RELEASE_STAGES.every(id => features.algorithms?.some(a => a.algorithm_id === id && ['passed', 'warning'].includes(a.status)))) return 'missing-or-failed-required-stage';
  if (!features.algorithms?.some(a => a.algorithm_id === 'metadata' && a.values?.codec === 'mp3')) return 'not-mp3';
  return null;
}

function publicTrack(track, features, index) {
  const output = {id: track.fileHash, fileHash: track.fileHash, sourceVersion: track.fileHash,
    title: typeof track.title === 'string' ? track.title : '', artist: typeof track.artist === 'string' ? track.artist : '', album: typeof track.album === 'string' ? track.album : '',
    duration: features.duration_s, status: 'ready', kind: 'cloud', addedAt: 0, color: index % 6, evidence: [], features: sanitizePublic(features)};
  for (const key of ['title', 'artist', 'album']) if (hasPrivatePath(output[key]) || secretPattern.test(output[key])) throw Error('Public metadata contains a private value');
  if (!Number.isFinite(output.duration) || output.duration <= 0) throw Error('Track duration is invalid');
  return output;
}

export async function exportRelease({
  catalogFile = path.join(project, 'output/web-release/catalog.json'),
  sourcesFile = path.join(project, 'output/web-release/sources.json'),
  cacheDir = path.join(project, 'packages/prompt-to-playlist/output/web-features'),
  staticDir = path.join(packageRoot, 'dist-web'),
  mixDir = path.join(project, 'output/mix-delivery', mixKey),
  outputDir = path.join(project, 'output/cloud-releases/first-release'),
} = {}) {
  // Freeze the preview selection, never invoke its mutable scan or any analyzer.
  const inputCatalog = await readJson(catalogFile), sources = await readJson(sourcesFile);
  if (!Array.isArray(inputCatalog.tracks) || !inputCatalog.tracks.length) throw Error('The saved preview catalog is empty');
  const selected = new Set();
  for (const track of inputCatalog.tracks) {
    if (!hashPattern.test(track.fileHash ?? '') || track.id !== track.fileHash || track.sourceVersion !== track.fileHash) throw Error('Invalid published track identity');
    if (selected.has(track.fileHash)) throw Error('Duplicate published track identity');
    selected.add(track.fileHash);
  }
  const inputSelection = hashBytes(JSON.stringify(inputCatalog.tracks.map(t => ({id: t.id, title: t.title, artist: t.artist, album: t.album}))));
  try {
    const previous = await readJson(path.join(outputDir, 'release.json'));
    if (previous.inputSelection !== inputSelection) throw Error('Existing release has a different selection; choose a new output directory');
    return {...await verifyRelease(outputDir), reused: true, outputDir};
  } catch (error) { if (error.code !== 'ENOENT') throw error; }
  // Fail rather than overwrite a partially built or unrelated directory.
  try { await lstat(outputDir); throw Error('Output already exists without a release manifest'); } catch (error) { if (error.code !== 'ENOENT') throw error; }
  const staging = `${outputDir}.staging-${randomUUID()}`;
  await mkdir(path.join(staging, 'private/features'), {recursive: true});
  try {
    await copyStatic(staticDir, path.join(staging, 'public'));
    const tracks = [], exclusions = [], reasonCounts = {};
    let audioBytes = 0;
    for (const track of inputCatalog.tracks) {
      const hash = track.fileHash, featureFile = path.join(cacheDir, `${hash}.json`), features = await readJson(featureFile);
      if (!fullyAnalyzed(features) || features.sha256 !== hash) throw Error(`Published track ${hash} fails the strict feature/identity gate`);
      const source = sources[hash];
      if (typeof source !== 'string' || !/\.mp3$/i.test(source)) throw Error(`Published track ${hash} has no MP3 source`);
      const copied = await copyVerified(source, path.join(staging, 'media', `${hash}.mp3`), hash);
      audioBytes += copied.bytes;
      await copyVerified(featureFile, path.join(staging, 'private/features', `${hash}.json`));
      tracks.push(publicTrack(track, features, tracks.length));
    }
    for (const name of (await readdir(cacheDir)).filter(name => /^[a-f0-9]{64}\.json$/.test(name)).sort()) {
      const hash = name.slice(0, -5);
      if (selected.has(hash)) continue;
      let reason;
      try { const feature = await readJson(path.join(cacheDir, name)); reason = feature.sha256 !== hash ? 'feature-identity-mismatch' : eligibilityReason(feature) ?? 'eligible-but-no-published-source'; }
      catch { reason = 'unreadable-feature-cache'; }
      exclusions.push({sha256: hash, reason}); reasonCounts[reason] = (reasonCounts[reason] ?? 0) + 1;
    }
    const catalog = {revision: hashBytes(JSON.stringify(tracks)), tracks};
    await writeFile(path.join(staging, 'public/catalog.json'), json(catalog), {flag: 'wx'});
    const mix = await readJson(path.join(mixDir, 'manifest.json')), graph = await readFile(path.join(mixDir, 'graph.txt'), 'utf8');
    const mixInfo = mixMetadata(mix, graph);
    await copyVerified(path.join(mixDir, 'stream.m4a'), path.join(staging, 'media/mix.m4a'), mix.hashes['stream.m4a']);
    await writeFile(path.join(staging, 'public/mix.json'), json(mixInfo), {flag: 'wx'});
    await mkdir(path.join(staging, 'private/mix'));
    await copyVerified(path.join(mixDir, 'manifest.json'), path.join(staging, 'private/mix/manifest.json'));
    await copyVerified(path.join(mixDir, 'graph.txt'), path.join(staging, 'private/mix/graph.txt'));
    await writeFile(path.join(staging, 'private/exclusions.json'), json({schema: 'resonant/release-exclusions/1', cacheRecords: selected.size + exclusions.length, publishedTracks: selected.size, excludedRecords: exclusions.length, reasonCounts, exclusions}), {flag: 'wx'});
    const manifest = await finalizeRelease(staging, {inputSelection, trackCount: tracks.length, audioBytes});
    await verifyRelease(staging);
    await rename(staging, outputDir);
    return {...manifest, reused: false, outputDir};
  } catch (error) { await rm(staging, {recursive: true, force: true}); throw error; }
}

// Re-finalize after the private planner/model artifact is added. Never serve private/.
export async function finalizeRelease(root, metadata) {
  const previous = metadata ?? await readJson(path.join(root, 'release.json'));
  const files = [];
  for (const relative of await walk(root)) {
    if (relative === 'release.json') continue;
    if (!/^(?:public|private|media)\//.test(relative)) throw Error('Unexpected release top-level entry');
    files.push({path: relative, ...await digestFile(path.join(root, relative)), visibility: relative.startsWith('public/') ? 'public' : relative.startsWith('media/') ? 'media' : 'private'});
  }
  const manifest = {schema: RELEASE_SCHEMA, inputSelection: previous.inputSelection, featureVersion: 'selected-estimators-v3-character120', featurePolicy: 'maest-top6-v1', trackCount: previous.trackCount, audioBytes: previous.audioBytes,
    catalogPath: 'public/catalog.json', mixPath: 'public/mix.json', mixAudioPath: 'media/mix.m4a', featureDirectory: 'private/features', plannerPath: files.some(file => file.path === 'private/planner.json') ? 'private/planner.json' : null, files};
  manifest.releaseId = hashBytes(JSON.stringify(manifest));
  await writeFile(path.join(root, 'release.json'), json(manifest));
  return manifest;
}

export async function verifyRelease(root, {requirePlanner = false} = {}) {
  if (!(await lstat(root)).isDirectory() || (await lstat(root)).isSymbolicLink()) throw Error('Release root must be a real directory');
  // Check the whole tree before following any manifest-controlled filename.
  const actual = (await walk(root)).filter(file => file !== 'release.json');
  const manifest = await readJson(path.join(root, 'release.json'));
  if (manifest.schema !== RELEASE_SCHEMA || !Array.isArray(manifest.files)) throw Error('Unsupported release manifest');
  if (manifest.catalogPath !== 'public/catalog.json' || manifest.mixPath !== 'public/mix.json' || manifest.mixAudioPath !== 'media/mix.m4a' || manifest.featureDirectory !== 'private/features' || ![null, 'private/planner.json'].includes(manifest.plannerPath)) throw Error('Unsupported release locations');
  const {releaseId, ...body} = manifest;
  if (releaseId !== hashBytes(JSON.stringify(body))) throw Error('Release manifest digest mismatch');
  const seen = new Set();
  for (const file of manifest.files) {
    safeReleasePath(file.path);
    if (seen.has(file.path) || !/^(?:public|private|media)\//.test(file.path)) throw Error('Duplicate or invalid manifest file');
    seen.add(file.path);
    const digest = await digestFile(path.join(root, file.path));
    if (digest.sha256 !== file.sha256 || digest.bytes !== file.bytes) throw Error(`Release checksum mismatch: ${file.path}`);
  }
  if (actual.length !== seen.size || actual.some(file => !seen.has(file))) throw Error('Unlisted release file');
  if (requirePlanner && (manifest.plannerPath !== 'private/planner.json' || !seen.has('private/planner.json'))) throw Error('Frozen private planner is required for deployment');
  for (const required of ['public/index.html', 'public/config.json', 'public/mix.json', 'media/mix.m4a', 'private/exclusions.json']) if (!seen.has(required)) throw Error(`Required release artifact is missing: ${required}`);
  const catalog = await readJson(path.join(root, safeReleasePath(manifest.catalogPath)));
  if (catalog.tracks.length !== manifest.trackCount || catalog.revision !== hashBytes(JSON.stringify(catalog.tracks))) throw Error('Catalog identity mismatch');
  const ids = new Set(); let audioBytes = 0;
  for (const track of catalog.tracks) {
    if (!hashPattern.test(track.fileHash ?? '') || track.id !== track.fileHash || track.sourceVersion !== track.fileHash || ids.has(track.fileHash)) throw Error('Invalid catalog track identity');
    ids.add(track.fileHash);
    const media = manifest.files.find(file => file.path === `media/${track.fileHash}.mp3`);
    if (!media || media.sha256 !== track.fileHash) throw Error('Catalog media is missing or mismatched');
    audioBytes += media.bytes;
    const feature = await readJson(path.join(root, 'private/features', `${track.fileHash}.json`));
    if (!fullyAnalyzed(feature) || feature.sha256 !== track.fileHash) throw Error('Released feature is ineligible');
  }
  if (audioBytes !== manifest.audioBytes) throw Error('Release audio byte count mismatch');
  return manifest;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const operation = args[0] === '--verify-ready' ? 'verify-ready' : args[0] === '--verify' ? 'verify' : args[0] === '--finalize' ? 'finalize' : 'export';
  try {
    let result;
    if (operation !== 'export') {
      if (args.length !== 2) throw Error(`Usage: node scripts/export-release.mjs --${operation} RELEASE_DIRECTORY`);
      result = operation.startsWith('verify') ? await verifyRelease(path.resolve(args[1]), {requirePlanner: operation === 'verify-ready'}) : await finalizeRelease(path.resolve(args[1]));
    } else {
      if (args.length && (args.length !== 2 || args[0] !== '--output')) throw Error('Usage: node scripts/export-release.mjs [--output RELEASE_DIRECTORY]');
      const outputDir = args[1] ? path.resolve(args[1]) : path.join(project, 'output/cloud-releases/first-release');
      const allowed = path.join(project, 'output/cloud-releases');
      if (!outputDir.startsWith(`${allowed}${path.sep}`)) throw Error('Export destination must be inside ignored output/cloud-releases');
      result = await exportRelease({outputDir});
    }
    console.log(json({operation, releaseId: result.releaseId, trackCount: result.trackCount, audioBytes: result.audioBytes, files: result.files.length, plannerReady: Boolean(result.plannerPath), ...(result.outputDir ? {outputDir: result.outputDir, reused: result.reused} : {})}));
  } catch (error) { console.error(`Release ${operation} failed: ${error.message}`); process.exitCode = 1; }
}
