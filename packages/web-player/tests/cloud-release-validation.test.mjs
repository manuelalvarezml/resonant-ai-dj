import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, rm, symlink} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import os from 'node:os';
import path from 'node:path';
import {finalizeRelease} from '../scripts/export-release.mjs';
import {loadCloudRelease} from '../scripts/cloud-server.mjs';
import {RELEASE_STAGES} from '../src/release-policy.js';

const digest = value => createHash('sha256').update(value).digest('hex');
const json = value => JSON.stringify(value);
async function fixture(t) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'resonant-runtime-release-'));
  t.after(() => rm(root, {recursive: true, force: true}));
  const audio = 'fixture-song-original', hash = digest(audio);
  const tracks = [{id: hash, fileHash: hash, sourceVersion: hash, title: 'Fixture'}];
  const catalog = {revision: digest(json(tracks)), tracks};
  const feature = {sha256: hash, feature_version: 'selected-estimators-v3-character120', policy: 'maest-top6-v1', status: 'complete', algorithms: RELEASE_STAGES.map(algorithm_id => ({algorithm_id, status: 'passed', values: algorithm_id === 'metadata' ? {codec: 'mp3'} : {}}))};
  const files = {'public/index.html': '<html>fixture</html>', 'public/catalog.json': json(catalog), 'public/mix.json': json({duration_s: 60}), 'public/config.json': '{}', 'private/exclusions.json': '{}', 'private/planner.json': '{}', [`private/features/${hash}.json`]: json(feature), [`media/${hash}.mp3`]: audio, 'media/mix.m4a': 'fixture-mix'};
  for (const [relative, bytes] of Object.entries(files)) { await mkdir(path.dirname(path.join(root, relative)), {recursive: true}); await writeFile(path.join(root, relative), bytes); }
  const manifest = await finalizeRelease(root, {inputSelection: digest('fixture'), trackCount: 1, audioBytes: Buffer.byteLength(audio)});
  return {root, hash, audio, feature, catalog, manifest};
}

test('production loader accepts exporter contract, then rejects digest-consistent wrong media identity', async t => {
  const f = await fixture(t);
  assert.equal((await loadCloudRelease(f.root)).tracks.size, 1);
  await writeFile(path.join(f.root, `media/${f.hash}.mp3`), 'different-source');
  await finalizeRelease(f.root);
  await assert.rejects(loadCloudRelease(f.root), /Invalid published track/);
});

test('production loader rejects digest-consistent partial cached analysis', async t => {
  const f = await fixture(t);
  await writeFile(path.join(f.root, `private/features/${f.hash}.json`), json({...f.feature, status: 'partial'}));
  await finalizeRelease(f.root);
  await assert.rejects(loadCloudRelease(f.root), /Ineligible published analysis/);
});

test('production loader rejects catalog revision and alternate release locations even with recomputed manifest digest', async t => {
  const f = await fixture(t);
  await writeFile(path.join(f.root, 'public/catalog.json'), json({...f.catalog, revision: digest('wrong-catalog')}));
  await finalizeRelease(f.root);
  await assert.rejects(loadCloudRelease(f.root), /Catalog revision mismatch/);
  const {releaseId, ...body} = f.manifest;
  body.catalogPath = 'private/planner.json';
  await writeFile(path.join(f.root, 'release.json'), json({...body, releaseId: digest(json(body))}));
  await assert.rejects(loadCloudRelease(f.root), /Unsupported release locations/);
});

test('production loader refuses symlinked private evidence', async t => {
  const f = await fixture(t), feature = path.join(f.root, `private/features/${f.hash}.json`);
  await rm(feature); await symlink(path.join(f.root, 'private/planner.json'), feature);
  await assert.rejects(loadCloudRelease(f.root), /symlinks/);
});
