import test from 'node:test';
import assert from 'node:assert/strict';
import * as fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { registry, preview, renderBundle, sha256, generate, secureRoot, ROOT } from '../src/core.mjs';
const temporary = async fn => { const root = await fs.mkdtemp(path.join(os.tmpdir(),'dynamo-')); try {return await fn(root);} finally {await fs.rm(root,{recursive:true,force:true});} };
test('all three pinned template types generate reproducibly and pass their own tests', async () => {
  assert.equal((await registry()).length,3);
  for (const entry of await registry()) await temporary(async root => {
    const args={template:entry.id,name:'example'};
    const first=await preview(args); assert.deepEqual(first,await preview(args));
    const receipt=await generate(args,root);
    for(const file of first.files) assert.equal(await fs.readFile(path.join(root,receipt.relativePath,file.path),'utf8'),file.content);
    assert.equal(receipt.digest,first.digest);
    execFileSync('npm',['test'],{cwd:path.join(root,receipt.relativePath),timeout:15000,env:{PATH:process.env.PATH},stdio:'pipe'});
    await assert.rejects(generate(args,root));
    assert.equal(await fs.readFile(path.join(root,receipt.relativePath,'README.md'),'utf8'),first.files.find(f=>f.path==='README.md').content);
  });
});
test('caller path traversal, shell strings and unrecognized fields rejected',async()=>{
  for(const name of ['../escape','a/b','a\\b','a;touch pwned','$(id)','A','', 'con']) await assert.rejects(preview({template:'node-cli',name}));
  await assert.rejects(preview({template:'node-cli',name:'valid',output:'/tmp'}));
  await assert.rejects(preview({template:'unknown',name:'valid'}));
});
function bundle(files,extra={}){return Buffer.from(JSON.stringify({version:1,files,...extra}));}
test('digest tampering and hooks rejected without execution',()=>{
  const bytes=bundle([{path:'a.txt',content:'hello'}]);
  assert.throws(()=>renderBundle(bytes,'0'.repeat(64),'valid'));
  for(const bytes of [bundle([{path:'hooks/post_gen_project.py',content:'raise Exception()'}]),bundle([{path:'a',content:'ok'}],{hooks:['touch marker']})]) assert.throws(()=>renderBundle(bytes,sha256(bytes),'valid'));
});
test('malicious file paths, duplicates and file directory collisions rejected',()=>{
  for(const files of [[{path:'../escape',content:''}],[{path:'/absolute',content:''}],[{path:'a\\b',content:''}],[{path:'a',content:''},{path:'A',content:''}],[{path:'a',content:''},{path:'a/b',content:''}]]) {
    const bytes=bundle(files);assert.throws(()=>renderBundle(bytes,sha256(bytes),'valid'));
  }
});
test('bundle and rendered file resource limits enforced',()=>{
  for(const bytes of [bundle(Array.from({length:65},(_,i)=>({path:'f'+i,content:''}))),bundle([{path:'a',content:'x'.repeat(65537)}]),bundle([{path:'a',content:'{{name}}'.repeat(8192)}])]) assert.throws(()=>renderBundle(bytes,sha256(bytes),'x'.repeat(48)));
});
test('symlink and non-private output roots rejected',async()=>temporary(async root=>{
  await fs.mkdir(path.join(root,'target'),{mode:0o700}); await fs.symlink(path.join(root,'target'),path.join(root,'link'));
  await assert.rejects(secureRoot(path.join(root,'link')));
  await fs.chmod(path.join(root,'target'),0o755); await assert.rejects(secureRoot(path.join(root,'target')));
}));
test('existing project symlink never followed',async()=>temporary(async root=>{
  await fs.symlink('/tmp',path.join(root,'example')); await assert.rejects(generate({template:'node-cli',name:'example'},root));
  assert.equal(await fs.readlink(path.join(root,'example')),'/tmp');
}));
test('concurrent generation reserves one project and preserves contents',async()=>temporary(async root=>{
  const results=await Promise.allSettled([generate({template:'node-cli',name:'example'},root),generate({template:'node-cli',name:'example'},root)]);
  assert.equal(results.filter(r=>r.status==='fulfilled').length,1);
  assert.ok((await fs.readFile(path.join(root,'example/source/package.json'),'utf8')).includes('example'));
}));
test('quota and crash lock fail closed',async()=>temporary(async root=>{
  await fs.writeFile(path.join(root,'.dynamo.lock'),''); await assert.rejects(generate({template:'node-cli',name:'example'},root));
  await fs.unlink(path.join(root,'.dynamo.lock'));
  for(let i=0;i<100;i++) await fs.mkdir(path.join(root,'p'+i));
  await assert.rejects(generate({template:'node-cli',name:'example'},root));
}));
test('legacy Python entrypoint rejects before network or imports',()=>{
  assert.throws(()=>execFileSync('python3',['-m','dynamo_mcp.main'],{cwd:ROOT,timeout:5000,stdio:'pipe'}),error=>error.status===1 && error.stderr.toString().includes('retired'));
});
