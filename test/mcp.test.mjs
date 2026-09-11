import test from 'node:test';
import assert from 'node:assert/strict';
import { Client } from '@modelcontextprotocol/client';
import { StdioClientTransport } from '@modelcontextprotocol/client/stdio';
import { ROOT } from '../src/core.mjs';
import { dispatch } from '../src/runtime.mjs';
test('official SDK stdio discovers tools and resource, renders project, rejects writes and shell',async()=>{
  const transport = new StdioClientTransport({command:process.execPath,args:[ROOT+'src/cli.mjs','mcp'],env:{PATH:process.env.PATH},stderr:'pipe'});
  const client = new Client({name:'dynamo-test',version:'1.0.0'});
  try{
    await client.connect(transport);
    assert.equal((await client.listTools()).tools.length,6);
    assert.equal((await client.listResources()).resources.length,1);
    assert.match((await client.readResource({uri:'ruv://dynamo-mcp/policy'})).contents[0].text,/"hooks":false/);
    const rendered = await client.callTool({name:'template_preview',arguments:{template:'node-cli',name:'example'}});
    assert.ok(JSON.parse(rendered.content[0].text).files.length>3);
    for(const args of [{name:'project_generate',arguments:{template:'node-cli',name:'example'}},{name:'project_validate',arguments:{}},{name:'exec',arguments:{command:'id'}},{name:'template_preview',arguments:{template:'node-cli',name:'../escape'}}]) assert.equal((await client.callTool(args)).isError,true);
  } finally {await client.close();}
});
test('runtime validation rejects unconfigured execution',async()=>{
  const old=process.env.DYNAMO_ALLOW_VALIDATION;delete process.env.DYNAMO_ALLOW_VALIDATION;
  try{await assert.rejects(dispatch('project_validate',{}));await assert.rejects(dispatch('project_status',{shell:'id'}));}finally{if(old!==undefined)process.env.DYNAMO_ALLOW_VALIDATION=old;}
});
test('authorized SDK generation publishes tested source and fixed validation passes',async()=>{
  const fs = await import('node:fs/promises'); const os = await import('node:os'); const path = await import('node:path');
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'dynamo-mcp-'));
  const transport = new StdioClientTransport({command:process.execPath,args:[ROOT+'src/cli.mjs','mcp'],env:{PATH:process.env.PATH,DYNAMO_OUTPUT_ROOT:root,DYNAMO_ALLOW_GENERATE:'1',DYNAMO_ALLOW_VALIDATION:'1'},stderr:'pipe'});
  const client = new Client({name:'dynamo-write-test',version:'1.0.0'});
  try {
    await client.connect(transport);
    const result=await client.callTool({name:'project_generate',arguments:{template:'node-library',name:'sdk-project'}});
    assert.equal(result.isError,false);
    const receipt=JSON.parse(result.content[0].text);
    assert.equal(receipt.relativePath,'sdk-project/source');
    const {sum}=await import(path.join(root,receipt.relativePath,'index.mjs'));
    assert.equal(sum([20,22]),42);
    const validated=await client.callTool({name:'project_validate',arguments:{}});
    assert.equal(validated.isError,false); assert.equal(JSON.parse(validated.content[0].text).passed,true);
  } finally {await client.close();await fs.rm(root,{recursive:true,force:true});}
});
