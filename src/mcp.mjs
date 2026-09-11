import { Server } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
import { dispatch, policy } from './runtime.mjs';

export async function mcp() {
  const server = new Server({name:'dynamo-mcp',version:'2.0.0-alpha.1'}, { capabilities:{tools:{},resources:{}} });
  const tools = ['templates_list','template_preview','project_generate','project_status','project_validate','project_benchmark'];
  let active = 0;
  server.setRequestHandler('tools/list', async () => ({tools:tools.map(name=>({ name, description:name === 'project_generate' ? 'Generate bundled inert project under operator private root; local opt-in required.' : name.replaceAll('_',' '), inputSchema:{type:'object',properties:['template_preview','project_generate'].includes(name)?{template:{type:'string'},name:{type:'string'}}:{},required:['template_preview','project_generate'].includes(name)?['template','name']:[],additionalProperties:false}, annotations:{readOnlyHint:name!=='project_generate',destructiveHint:false,openWorldHint:false} }))}));
  server.setRequestHandler('tools/call', async request => {
    if(active >= 2) return {isError:true,content:[{type:'text',text:'Server busy'}]};
    active++;
    try { const result = await dispatch(request.params.name,request.params.arguments ?? {}); return {isError: result?.passed === false,content:[{type:'text',text:JSON.stringify(result)}]}; }
    catch { return {isError:true,content:[{type:'text',text:'Operation rejected; check input and operator policy'}]}; }
    finally { active--; }
  });
  server.setRequestHandler('resources/list', async () => ({resources:[{uri:'ruv://dynamo-mcp/policy',name:'Dynamo execution policy',mimeType:'application/json'}]}));
  server.setRequestHandler('resources/read', async request => {
    if(request.params.uri !== 'ruv://dynamo-mcp/policy') throw Error('Unknown resource');
    return {contents:[{uri:request.params.uri,mimeType:'application/json',text:JSON.stringify(policy)}]};
  });
  await server.connect(new StdioServerTransport(process.stdin,process.stdout,{maxBufferSize:65536}));
}
