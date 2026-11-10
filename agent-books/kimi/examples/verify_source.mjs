// Compile and exercise selected unmodified upstream modules, not a copied reimplementation.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp, mkdir, readFile, rm, writeFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const [sourceArg, dependencyArg, outputArg] = process.argv.slice(2);
if (!sourceArg || !dependencyArg) {
  throw new Error('Usage: node verify_source.mjs <pinned-source> <npm-dependency-directory> [report.json]');
}
const source = path.resolve(sourceArg);
const dependencies = path.resolve(dependencyArg);
const require = createRequire(path.join(dependencies, 'package.json'));
const {buildSync} = require('esbuild');
const here = path.dirname(fileURLToPath(import.meta.url));
const plugin = path.join(here, 'review-plugin');
const files = {
  manifest: 'packages/agent-core-v2/src/app/plugin/manifest.ts',
  agent: 'packages/agent-core-v2/src/workspace/workspaceAgentProfileLoader/internal/agentFile.ts',
  hook: 'packages/agent-core-v2/src/features/externalHooks/internal/runHook.ts',
};
const baseline = JSON.parse(await readFile(path.join(here, '../facts/source-lock.json'), 'utf8'));
const hashes = {};
for (const relative of Object.values(files)) {
  hashes[relative] = createHash('sha256').update(await readFile(path.join(source, relative))).digest('hex');
  assert.equal(hashes[relative], baseline.files[relative], `unexpected upstream source: ${relative}`);
}
const temp = await mkdtemp(path.join(tmpdir(), 'kimi-source-probe-'));
const passed = [];
try {
  const modules = {};
  for (const [name, relative] of Object.entries(files)) {
    const outfile = path.join(temp, `${name}.mjs`);
    buildSync({entryPoints: [path.join(source, relative)], outfile, bundle: true,
      platform: 'node', format: 'esm', nodePaths: [path.join(dependencies, 'node_modules')],
      logLevel: 'warning'});
    modules[name] = await import(pathToFileURL(outfile).href);
  }
  const parsed = await modules.manifest.parseManifest(plugin);
  assert.equal(parsed.manifest.name, 'chengming-review');
  assert.equal(parsed.diagnostics.filter(x => x.severity === 'error').length, 0);
  assert.equal(parsed.manifest.hooks[0].event, 'PreToolUse');
  passed.push('real parser accepts the complete workshop plugin');

  const invalid = path.join(temp, 'invalid');
  await mkdir(invalid);
  await writeFile(path.join(invalid, 'kimi.plugin.json'), JSON.stringify({name: 'broken', skills: './../'}));
  const bad = await modules.manifest.parseManifest(invalid);
  assert.ok(bad.diagnostics.some(x => x.severity === 'error' && x.message.includes('outside')));
  passed.push('real parser diagnoses a skill path outside the plugin');

  await mkdir(path.join(invalid, '.kimi-plugin'));
  await writeFile(path.join(invalid, '.kimi-plugin/plugin.json'), JSON.stringify({name: 'secondary'}));
  assert.equal((await modules.manifest.parseManifest(invalid)).manifest.name, 'broken');
  passed.push('root manifest takes precedence over .kimi-plugin/plugin.json');

  const agentText = await readFile(path.join(plugin, 'agents/inventory-reviewer.md'), 'utf8');
  const agent = modules.agent.parseAgentFileText({path: 'inventory-reviewer.md', source: 'explicit', text: agentText});
  assert.deepEqual(agent.tools, ['Read', 'Grep', 'Glob']);
  assert.deepEqual(agent.disallowedTools, ['Bash', 'Write', 'Edit']);
  assert.deepEqual(agent.subagents, []);
  passed.push('real parser preserves the reviewer tool lists');
  assert.throws(() => modules.agent.parseAgentFileText({path: 'broken.md', source: 'explicit',
    text: '---\nname: broken\n---\nReview code.'}), /description/);
  passed.push('real parser rejects an agent without a description');
  const empty = modules.agent.parseAgentFileText({path: 'empty.md', source: 'explicit',
    text: '---\nname: empty\ndescription: example\ntools: []\n---\nReview code.'});
  assert.deepEqual(empty.tools, []);
  passed.push('empty tools list remains empty');

  const host = {async spawn(command, args, options) {
    const proc = spawn(command, args, {...options, windowsHide: true,
      env: {...process.env, ...options.env}, stdio: 'pipe'});
    const completed = once(proc, 'exit').then(([code]) => code ?? 1);
    return {stdin: proc.stdin, stdout: proc.stdout, stderr: proc.stderr,
      wait: () => completed, kill: async signal => { proc.kill(signal); }, dispose: () => {}};
  }};
  for (const [behavior, action] of [['allow', 'allow'], ['deny-json', 'block'],
      ['deny-exit', 'block'], ['error', 'allow'], ['timeout', 'allow']]) {
    const command = `"${process.execPath}" "${path.join(here, 'hook_fixture.cjs')}" ${behavior}`;
    const result = await modules.hook.runHook(host, command, {hook_event_name: 'PreToolUse'}, {timeout: 1});
    assert.equal(result.action, action, behavior);
    if (behavior === 'timeout') assert.equal(result.timedOut, true);
    if (behavior === 'error') assert.equal(result.exitCode, 1);
    passed.push(`real hook runner: ${behavior} -> ${action}`);
  }
  const failed = await modules.hook.runHook({async spawn() {throw new Error('fixture spawn failure');}},
    'unused', {}, {timeout: 1});
  assert.equal(failed.action, 'allow');
  assert.equal(failed.errored, true);
  passed.push('real hook runner allows after a process launch failure');

  const report = {commit: baseline.commit, node: process.version,
    esbuild: require('esbuild/package.json').version, passed, source_sha256: hashes,
    scope: 'selected upstream parsers and hook runner with local child processes; not a full Kimi session'};
  const rendered = JSON.stringify(report, null, 2) + '\n';
  if (outputArg) await writeFile(path.resolve(outputArg), rendered);
  process.stdout.write(rendered);
} finally {
  const relative = path.relative(path.resolve(tmpdir()), path.resolve(temp));
  assert.ok(relative.startsWith('kimi-source-probe-') && !relative.includes(path.sep),
    'cleanup target must be the probe directory directly under the temporary root');
  await rm(temp, {recursive: true, force: true});
}
