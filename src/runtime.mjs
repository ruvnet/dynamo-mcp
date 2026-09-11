import { spawn } from 'node:child_process';
import { performance } from 'node:perf_hooks';
import { ROOT, LIMITS, object, registry, preview, generate, sha256 } from './core.mjs';

export const policy = Object.freeze({ version: 2, hooks: false, network: false, callerPaths: false, automaticPromotion: false, receiptsSigned: false, limits: LIMITS });
let running = false;
export async function validation() {
  if (process.env.DYNAMO_ALLOW_VALIDATION !== '1') throw Error('Operator validation opt-in required');
  if (running) throw Error('Validation busy');
  running = true;
  try {
    return await new Promise((resolve, reject) => {
      const child = spawn(process.execPath, ['--test', 'test/core.test.mjs'], { cwd: ROOT, detached: process.platform !== 'win32', env: { PATH: process.env.PATH || '' }, stdio: ['ignore', 'pipe', 'pipe'] });
      let size = 0, chunks = [], stopped = false;
      const kill = () => { try { process.platform === 'win32' ? child.kill('SIGKILL') : process.kill(-child.pid, 'SIGKILL'); } catch {} };
      const fail = message => { stopped = true; kill(); reject(Error(message)); };
      const timer = setTimeout(() => fail('Validation deadline exceeded'), 30000);
      for (const stream of [child.stdout, child.stderr]) stream.on('data', chunk => { size += chunk.length; if(size > 65536) fail('Validation output limit'); else chunks.push(chunk); });
      child.on('error', error => { clearTimeout(timer); reject(error); });
      child.on('close', code => { clearTimeout(timer); if (!stopped) { const output = Buffer.concat(chunks).toString(); resolve({ passed: code === 0, exitCode: code, output, digest: sha256(output), signed: false }); } });
    });
  } finally { running = false; }
}
export async function benchmark() {
  const samples = [];
  for (let i = 0; i < 100; i++) { const start = performance.now(); await preview({template:'node-cli',name:'benchmark'}); samples.push(performance.now()-start); }
  samples.sort((a,b)=>a-b);
  return { samples:100, workload:'local digest verification and deterministic render, no filesystem writes', medianMs:samples[50],p95Ms:samples[95], superiorityClaim:false };
}
export async function dispatch(name, input = {}) {
  if (Buffer.byteLength(JSON.stringify(input)) > LIMITS.inputBytes) throw Error('Input limit');
  if (name === 'template_preview') return preview(input);
  if (name === 'project_generate') {
    if (process.env.DYNAMO_ALLOW_GENERATE !== '1') throw Error('Operator generation opt-in required');
    return generate(input, process.env.DYNAMO_OUTPUT_ROOT);
  }
  object(input, []);
  if (name === 'templates_list') return registry();
  if (name === 'project_status') return { project:'dynamo-mcp', version:'2.0.0-alpha.1', policy };
  if (name === 'project_validate') return validation();
  if (name === 'project_benchmark') return benchmark();
  throw Error('Unknown operation');
}
