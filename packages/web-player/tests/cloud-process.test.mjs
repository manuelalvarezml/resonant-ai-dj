import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, readFile, writeFile, rm} from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {pythonJob, createJobs} from '../scripts/cloud-jobs.mjs';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const exists = pid => { try { process.kill(pid, 0); return true; } catch (error) { if (error.code === 'ESRCH') return false; throw error; } };
async function waitFor(fn) { for (let n = 0; n < 300; n++) { const value = await fn(); if (value) return value; await delay(20); } throw Error('Timed out waiting for worker fixture'); }

async function workerFixture(t, {ignoreParentTerm = false, exitParent = false} = {}) {
  const root = await mkdtemp(path.join(os.tmpdir(), 'resonant-process-test-'));
  const marker = path.join(root, 'worker-pids.json'), executable = path.join(root, 'fixture-worker');
  const childSource = `require('node:process').on('SIGTERM',()=>{}); require('node:fs').writeFileSync(${JSON.stringify(marker)},JSON.stringify({child:process.pid,parent:process.ppid})); setInterval(()=>{},1000);`;
  const parentSource = `#!${process.execPath}\nconst {spawn}=require('node:child_process'); const fs=require('node:fs');
${ignoreParentTerm ? "process.on('SIGTERM',()=>{});" : ''}
spawn(process.execPath,['-e',${JSON.stringify(childSource)}],{stdio:'ignore'});
${exitParent ? `const timer=setInterval(()=>{if(fs.existsSync(${JSON.stringify(marker)})){clearInterval(timer);process.exit(0);}},5);` : 'setInterval(()=>{},1000);'}\n`;
  await writeFile(executable, parentSource, {mode: 0o700});
  let observed;
  const pids = async () => { try { observed = JSON.parse(await readFile(marker, 'utf8')); return observed; } catch (error) { if (error.code === 'ENOENT') return null; throw error; } };
  t.after(async () => {
    // Test failures must not leave the fixture's sleeping descendants behind.
    observed ??= await pids();
    for (const pid of observed ? [observed.parent, observed.child] : []) { try { process.kill(pid, 'SIGKILL'); } catch (error) { if (error.code !== 'ESRCH') throw error; } }
    await rm(root, {recursive: true, force: true});
  });
  return {root, pids, config: {python: executable, releaseRoot: root, stateRoot: root, modelRoot: root, dailyLimit: 3, jobTimeoutMs: 150}};
}

test('cancel waits for a real SIGTERM-ignoring descendant to disappear before settling', {timeout: 10000}, async t => {
  const fixture = await workerFixture(t);
  const worker = pythonJob(fixture.config, 'unused-input', 'unused-output');
  const pids = await waitFor(fixture.pids);
  worker.cancel();
  await assert.rejects(worker.done, /timed out/);
  assert.equal(exists(pids.parent), false);
  assert.equal(exists(pids.child), false);
});

test('successful parent exit cleans up orphan descendants before resolving', {timeout: 10000}, async t => {
  const fixture = await workerFixture(t, {exitParent: true});
  const worker = pythonJob(fixture.config, 'unused-input', 'unused-output');
  await worker.done;
  const pids = await waitFor(fixture.pids);
  assert.equal(exists(pids.parent), false);
  assert.equal(exists(pids.child), false);
});

test('job timeout holds the slot through forced tree termination and then permits retry', {timeout: 15000}, async t => {
  const fixture = await workerFixture(t, {ignoreParentTerm: true});
  fixture.config.jobTimeoutMs = 4000; // Allow a cold executable launch on a busy host.
  const jobs = await createJobs(fixture.config);
  t.after(() => jobs.close());
  const began = Date.now();
  const first = await jobs.start({prompt: 'fixture only'}, 'session-one');
  const pids = await waitFor(fixture.pids);
  await delay(Math.max(0, began + fixture.config.jobTimeoutMs + 100 - Date.now())); // Both ignore TERM.
  assert.equal(exists(pids.parent), true);
  await assert.rejects(jobs.start({prompt: 'must wait'}, 'session-one'), error => error.status === 409);
  const failed = await waitFor(() => { const job = jobs.get(first.id, 'session-one'); return job.status === 'failed' ? job : null; });
  assert.match(failed.error, /timed out/);
  assert.equal(exists(pids.parent), false); assert.equal(exists(pids.child), false);
  assert.equal(jobs.get(first.id, 'other-session'), null);
  // The result state can be assigned immediately before filesystem cleanup ends.
  const second = await waitFor(async () => { try { return await jobs.start({prompt: 'retry'}, 'session-one'); } catch (error) { if (error.status === 409) return null; throw error; } });
  assert.ok(second.id); await jobs.close();
});
