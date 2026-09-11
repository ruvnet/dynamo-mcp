#!/usr/bin/env node
import { dispatch } from './runtime.mjs';
const aliases = {status:'project_status',list:'templates_list',preview:'template_preview',generate:'project_generate',test:'project_validate',benchmark:'project_benchmark',bench:'project_benchmark'};
try {
  const [command = 'status', input = '{}', ...rest] = process.argv.slice(2);
  if(rest.length || Buffer.byteLength(input)>32768) throw Error('Invalid arguments');
  if(command === 'mcp') { if(input !== '{}') throw Error('MCP has no arguments'); await (await import('./mcp.mjs')).mcp(); }
  else {
    if(!Object.hasOwn(aliases,command)) throw Error('Usage: status | list | preview JSON | generate JSON | test | benchmark | mcp');
    if(command === 'test') process.env.DYNAMO_ALLOW_VALIDATION='1';
    const result = await dispatch(aliases[command],JSON.parse(input));
    console.log(JSON.stringify(result,null,2));
    if(result?.passed === false) process.exitCode=1;
  }
} catch(error) { console.error(error.message); process.exitCode=1; }
