import {performance} from 'node:perf_hooks';
import * as fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {ROOT as root} from '../src/core.mjs';
const source=execFileSync('git',['show','93a4ab6414d859431e24c940559d60a1b88e5fc9:src/core.mjs'],{cwd:root,maxBuffer:65536,encoding:'utf8'}).replace("export const ROOT = fileURLToPath(new URL('../', import.meta.url));",'export const ROOT = '+JSON.stringify(root)+';');
const before=await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
const after=await import(root+'src/core.mjs');
const ids=(await after.registry()).map(x=>x.id); const results=[];
for(const template of ids){
 const input={template,name:'measured-project'}; assert.deepEqual(await before.preview(input),await after.preview(input));
 const samples={before:[],after:[]};
 for(let i=0;i<40;i++){await before.preview(input);await after.preview(input);}
 for(let i=0;i<500;i++){
  for(const version of i%2?['after','before']:['before','after']) {const start=performance.now();await ({before,after}[version]).preview(input);samples[version].push(performance.now()-start);}
 }
 const metrics={};for(const [version,values] of Object.entries(samples)){values.sort((a,b)=>a-b);metrics[version]={medianMs:values[250],p95Ms:values[475]};}
 const bytes=(await fs.stat(root+'templates/'+template+'.json')).size+(await fs.stat(root+'templates/manifest.json')).size+2;
 results.push({template,outputsIdentical:true,samplesEach:500,readBufferBytes:{before:262145+32769,after:bytes,reductionPercent:100*(1-bytes/(262145+32769))},...metrics});
}
console.log(JSON.stringify({date:'2026-09-11',node:process.version,method:'40warmups,500alternating complete fresh-file previews per implementation per template; every digest reverified; allocation from read buffer capacities',results},null,2));
