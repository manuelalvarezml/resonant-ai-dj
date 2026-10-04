import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, readFile, writeFile, rm, symlink, readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import os from 'node:os';
import path from 'node:path';
import {exportRelease, verifyRelease, finalizeRelease, sanitizePublic, safeReleasePath, mixMetadata} from '../scripts/export-release.mjs';
import {RELEASE_STAGES} from '../src/release-policy.js';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const writeJson = (file, value) => writeFile(file, JSON.stringify(value));
async function fixture(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'resonant-export-test-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const cacheDir = path.join(root, 'cache'), staticDir = path.join(root, 'static'), mixDir = path.join(root, 'mix'), outputDir = path.join(root, 'release');
  for (const dir of [cacheDir, staticDir, mixDir]) await mkdir(dir);
  const audio = Buffer.from('mp3-fixture-original-bytes'), fileHash = hash(audio), source = path.join(root, 'original.mp3');
  await writeFile(source, audio);
  const feature = {sha256: fileHash, duration_s: 90, feature_version: 'selected-estimators-v3-character120', policy: 'maest-top6-v1', status: 'complete', algorithms: RELEASE_STAGES.map(algorithm_id => ({algorithm_id, status: 'passed', implementation: '/Users/owner/model', metrics: {work_path: '/private/tmp/job'}, values: algorithm_id === 'metadata' ? {codec: 'mp3', encoded_tags: {title: 'a song', comment: '/home/owner/private'}} : algorithm_id === 'semantic_audio' ? {encoder_id: 'preserve-me', segments: [{start_s: 0, embedding: [0.2, 0.8]}]} : {bpm: 120}}))};
  const rawFeature = `${JSON.stringify(feature, null, 3)}\n`;
  await writeFile(path.join(cacheDir, `${fileHash}.json`), rawFeature);
  const incompleteHash = hash('incomplete'), noSourceHash = hash('no-source');
  await writeJson(path.join(cacheDir, `${incompleteHash}.json`), {...feature, sha256: incompleteHash, status: 'partial'});
  await writeJson(path.join(cacheDir, `${noSourceHash}.json`), {...feature, sha256: noSourceHash});
  const catalogFile = path.join(root, 'catalog.json'), sourcesFile = path.join(root, 'sources.json');
  const track = {id: fileHash, fileHash, sourceVersion: fileHash, title: 'Song', artist: 'Artist', album: 'Album'};
  await writeJson(catalogFile, {revision: 'preview', tracks: [track]}); await writeJson(sourcesFile, {[fileHash]: source});
  const staticFiles = {'index.html': '<html>player</html>', 'config.json': JSON.stringify({edition: 'web', mode: 'http'})};
  for (const [name, value] of Object.entries(staticFiles)) await writeFile(path.join(staticDir, name), value);
  await writeJson(path.join(staticDir, 'build-manifest.json'), {files: Object.fromEntries(Object.entries(staticFiles).map(([name, bytes]) => [name, hash(bytes)]))});
  const mixBytes = Buffer.from('existing-mix-bytes');
  await writeFile(path.join(mixDir, 'stream.m4a'), mixBytes);
  const mix = {status: 'complete', duration_s: 609.1, hashes: {'stream.m4a': hash(mixBytes)}};
  await writeJson(path.join(mixDir, 'manifest.json'), mix);
  const graph = '[h0_out_prefix_source]atrim=end=203.65;[h0_in_transition_source]atrim=end=29.09;[h1_out_prefix_source]atrim=end=407.29;[h1_in_transition_source]atrim=end=29.09';
  await writeFile(path.join(mixDir, 'graph.txt'), graph);
  return {root, source, fileHash, rawFeature, audio, feature, track, mix, graph, options: {catalogFile, sourcesFile, cacheDir, staticDir, mixDir, outputDir}};
}

test('freezes exact originals/private vectors, sanitizes catalog, inventories exclusions and is repeatable', async t => {
  const f = await fixture(t), release = await exportRelease(f.options), root = f.options.outputDir;
  assert.equal(release.trackCount, 1); assert.equal(release.audioBytes, f.audio.length); assert.equal(release.reused, false);
  assert.deepEqual(await readFile(path.join(root, 'media', `${f.fileHash}.mp3`)), f.audio);
  assert.deepEqual(await readFile(f.source), f.audio);
  assert.equal(await readFile(path.join(root, 'private/features', `${f.fileHash}.json`), 'utf8'), f.rawFeature);
  const catalogText = await readFile(path.join(root, 'public/catalog.json'), 'utf8');
  for (const forbidden of ['"embedding"', '/Users/', '/private/', 'encoded_tags', 'implementation']) assert.equal(catalogText.includes(forbidden), false);
  assert.equal(catalogText.includes('preserve-me'), true);
  const excluded = JSON.parse(await readFile(path.join(root, 'private/exclusions.json')));
  assert.deepEqual(excluded.reasonCounts, {'incomplete-analysis': 1, 'eligible-but-no-published-source': 1});
  assert.equal(excluded.cacheRecords, 3);
  const mix = JSON.parse(await readFile(path.join(root, 'public/mix.json')));
  assert.deepEqual(mix.transitions, [{start_s: 203.65, end_s: 232.74}, {start_s: 407.29, end_s: 436.38}]);
  assert.equal((await verifyRelease(root)).releaseId, release.releaseId);
  await assert.rejects(verifyRelease(root, {requirePlanner: true}), /Frozen private planner/);
  assert.equal((await exportRelease(f.options)).reused, true);
  await writeJson(path.join(root, 'private/planner.json'), {ready: true});
  const finalized = await finalizeRelease(root);
  assert.equal(finalized.plannerPath, 'private/planner.json'); assert.notEqual(finalized.releaseId, release.releaseId);
  await verifyRelease(root, {requirePlanner: true});
  assert.equal((await finalizeRelease(root)).releaseId, finalized.releaseId);
});

test('fails closed for changed source bytes without leaving a partial output', async t => {
  const f = await fixture(t);
  await writeFile(f.source, 'changed bytes');
  await assert.rejects(exportRelease(f.options), /Source hash/);
  assert.equal((await readdir(f.root)).some(name => name.startsWith('release')), false);
});

test('rejects incomplete selected records and cache identity mismatches', async t => {
  const f = await fixture(t), file = path.join(f.options.cacheDir, `${f.fileHash}.json`);
  await writeJson(file, {...f.feature, status: 'partial'});
  await assert.rejects(exportRelease(f.options), /strict feature\/identity gate/);
  await writeJson(file, {...f.feature, sha256: hash('other-file')});
  await assert.rejects(exportRelease(f.options), /strict feature\/identity gate/);
});

test('verifier detects changed bytes, unlisted files and symlinks', async t => {
  const f = await fixture(t), root = f.options.outputDir;
  await exportRelease(f.options);
  const media = path.join(root, 'media', `${f.fileHash}.mp3`);
  await writeFile(media, 'changed'); await assert.rejects(verifyRelease(root), /checksum mismatch/);
  await writeFile(media, f.audio); await writeFile(path.join(root, 'private', 'unlisted.json'), '{}');
  await assert.rejects(verifyRelease(root), /Unlisted release file/);
  await rm(path.join(root, 'private', 'unlisted.json')); await symlink(f.source, path.join(root, 'private', 'outside'));
  await assert.rejects(verifyRelease(root), /Symlinks/);
});

test('source symlinks and corrupt static builds fail before publication', async t => {
  const f = await fixture(t), alias = path.join(f.root, 'alias.mp3');
  await symlink(f.source, alias); await writeJson(f.options.sourcesFile, {[f.fileHash]: alias});
  await assert.rejects(exportRelease(f.options), /regular files/);
  await writeJson(f.options.sourcesFile, {[f.fileHash]: f.source});
  await writeFile(path.join(f.options.staticDir, 'index.html'), 'changed');
  await assert.rejects(exportRelease(f.options), /Source hash/);
});

test('rejects path traversal, strips secret-like public strings and derives transition lengths', () => {
  for (const name of ['../outside', '/etc/passwd', 'public/../private/foo', 'public//x', 'C:\\x', 'public/x\0y']) assert.throws(() => safeReleasePath(name), /Unsafe/);
  assert.equal(safeReleasePath('public/src/app.js'), 'public/src/app.js');
  const value = sanitizePublic({embedding: [1, 2], note: '/srv/private/music.mp3', good: 'musical evidence', password: 'private', comment: 'sk-proj-' + 'a'.repeat(32), nested: {text_embedding: [2], preserved: true}});
  assert.deepEqual(value, {good: 'musical evidence', nested: {preserved: true}});
  assert.throws(() => mixMetadata({status: 'complete', hashes: {'stream.m4a': 'a'.repeat(64)}, duration_s: 90}, '[h0_out_prefix_source]atrim=end=20'), /two valid/);
});
