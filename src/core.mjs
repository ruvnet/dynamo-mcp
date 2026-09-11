import { createHash } from 'node:crypto';
import * as fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = fileURLToPath(new URL('../', import.meta.url));
export const LIMITS = Object.freeze({ inputBytes: 32768, bundleBytes: 262144, fileBytes: 65536, files: 64, projects: 100 });
export const sha256 = data => createHash('sha256').update(data).digest('hex');
export function object(value, keys) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || Object.keys(value).some(k => !keys.includes(k))) throw Error('Invalid object fields');
}
export function slug(value) {
  if (typeof value !== 'string' || !/^[a-z][a-z0-9-]{0,47}$/.test(value) || /^(con|prn|aux|nul|com[0-9]|lpt[0-9])$/.test(value)) throw Error('Invalid project name');
  return value;
}
function safePath(value) {
  if (typeof value !== 'string' || value.length > 160 || value.split('/').some(p => !/^[a-zA-Z0-9_.-]+$/.test(p) || p === '.' || p === '..' || p.toLowerCase() === 'hooks') || value.includes('\\')) throw Error('Unsafe template path');
  return value;
}
async function boundedRead(file, max) {
  const handle = await fs.open(file, constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const stat = await handle.stat();
    if (!stat.isFile() || stat.size > max) throw Error('Invalid template file');
    const buffer = Buffer.alloc(max + 1);
    const { bytesRead } = await handle.read(buffer, 0, max + 1, 0);
    if (bytesRead > max) throw Error('Template too large');
    return buffer.subarray(0, bytesRead);
  } finally { await handle.close(); }
}
export async function registry() {
  const data = JSON.parse(await boundedRead(path.join(ROOT, 'templates/manifest.json'), LIMITS.inputBytes));
  object(data, ['version', 'templates']);
  if (data.version !== 1 || !Array.isArray(data.templates) || data.templates.length > 16) throw Error('Invalid manifest');
  for (const entry of data.templates) {
    object(entry, ['id', 'sha256', 'description']); slug(entry.id);
    if (!/^[a-f0-9]{64}$/.test(entry.sha256) || typeof entry.description !== 'string' || entry.description.length > 256) throw Error('Invalid manifest entry');
  }
  if (new Set(data.templates.map(e => e.id)).size !== data.templates.length) throw Error('Duplicate template');
  return data.templates;
}
export function renderBundle(buffer, expectedDigest, name) {
  slug(name);
  if (buffer.length > LIMITS.bundleBytes || sha256(buffer) !== expectedDigest) throw Error('Template digest mismatch');
  const bundle = JSON.parse(buffer);
  object(bundle, ['version', 'files']);
  if (bundle.version !== 1 || !Array.isArray(bundle.files) || !bundle.files.length || bundle.files.length > LIMITS.files) throw Error('Invalid bundle');
  const files = bundle.files.map(file => {
    object(file, ['path', 'content']); safePath(file.path);
    if (typeof file.content !== 'string' || Buffer.byteLength(file.content) > LIMITS.fileBytes) throw Error('Invalid content');
    const content = file.content.replaceAll('{{name}}', name);
    if (Buffer.byteLength(content) > LIMITS.fileBytes) throw Error('Rendered file too large');
    return { path: file.path, content, sha256: sha256(content) };
  }).sort((a, b) => a.path < b.path ? -1 : a.path > b.path ? 1 : 0);
  const names = new Set();
  for (const file of files) {
    const normalized = file.path.toLowerCase();
    if (names.has(normalized)) throw Error('Duplicate output');
    names.add(normalized);
  }
  for (const name of names) for (const other of names) if (name !== other && other.startsWith(name + '/')) throw Error('File directory collision');
  return { files, digest: sha256(JSON.stringify(files.map(({path, sha256}) => ({path, sha256})))), templateDigest: expectedDigest };
}
export async function preview(input) {
  object(input, ['template', 'name']); slug(input.template); slug(input.name);
  const entry = (await registry()).find(t => t.id === input.template);
  if (!entry) throw Error('Unknown template');
  const bytes = await boundedRead(path.join(ROOT, 'templates', entry.id + '.json'), LIMITS.bundleBytes);
  return { template: entry.id, name: input.name, ...renderBundle(bytes, entry.sha256, input.name) };
}
export async function secureRoot(root) {
  if (typeof root !== 'string' || !path.isAbsolute(root)) throw Error('Operator must configure absolute DYNAMO_OUTPUT_ROOT');
  const stat = await fs.lstat(root);
  if (!stat.isDirectory() || stat.isSymbolicLink() || (stat.mode & 0o077) || (process.getuid && stat.uid !== process.getuid())) throw Error('Output root must be owned private directory (0700)');
  if (await fs.realpath(root) !== path.resolve(root)) throw Error('Symlink output root denied');
  return root;
}
export async function generate(input, root) {
  const result = await preview(input);
  await secureRoot(root);
  // A private operator-owned root is the trust boundary. No caller paths or hooks.
  const lock = await fs.open(path.join(root, '.dynamo.lock'), 'wx', 0o600);
  const project = path.join(root, result.name);
  let reserved = false;
  try {
    if ((await fs.readdir(root)).length > LIMITS.projects) throw Error('Project quota exceeded');
    await fs.mkdir(project, { mode: 0o700 }); reserved = true;
    const stage = path.join(project, '.staging');
    await fs.mkdir(stage, { mode: 0o700 });
    for (const file of result.files) {
      const target = path.join(stage, file.path);
      await fs.mkdir(path.dirname(target), { recursive: true, mode: 0o700 });
      await fs.writeFile(target, file.content, { flag: 'wx', mode: 0o600 });
    }
    await fs.writeFile(path.join(stage, 'dynamo-receipt.json'), JSON.stringify({ version: 1, template: result.template, templateDigest: result.templateDigest, digest: result.digest, signed: false }, null, 2) + '\n', {flag:'wx',mode:0o600});
    await fs.rename(stage, path.join(project, 'source'));
    return { name: result.name, relativePath: result.name + '/source', digest: result.digest, files: result.files.length, signed: false };
  } catch (error) {
    if (reserved) await fs.rm(project, { recursive: true, force: true });
    throw error;
  } finally { await lock.close(); await fs.unlink(path.join(root, '.dynamo.lock')); }
}
