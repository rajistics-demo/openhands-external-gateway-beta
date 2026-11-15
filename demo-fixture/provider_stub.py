"""DETERMINISTIC MODEL PROVIDER stub (test-only) placed BEHIND real customer LiteLLM.
OpenAI-compatible /v1/chat/completions; counts provider calls; 'SLOW' streams long."""
import asyncio, json, re, uuid
from starlette.applications import Starlette
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

STATE = {'provider_calls': 0, 'models': [], 'streams_cancelled': 0, 'agent_turns': []}


async def chat(request):
    body = await request.json(); STATE['provider_calls'] += 1; STATE['models'].append(body.get('model'))
    rid = f'chatcmpl-{uuid.uuid4().hex}'  # unique per request, stable across its chunks
    model, usage = body.get('model'), {'prompt_tokens': 5, 'completion_tokens': 3, 'total_tokens': 8}
    msgs = body.get('messages') or []
    if 'PGWO_AGENT_PROOF' in json.dumps(msgs[:2]) and not body.get('stream'):
        return JSONResponse(_scripted_agent_turn(rid, model, usage, msgs, body))
    if not body.get('stream'):
        return JSONResponse({'id': rid, 'object': 'chat.completion', 'created': 0,
                             'model': model, 'usage': usage, 'choices': [{'index': 0, 'finish_reason': 'stop',
                             'message': {'role': 'assistant', 'content': f'pong from {model}'}}]})
    n, delay = (200, 0.05) if 'SLOW' in json.dumps(body.get('messages')) else (3, 0)

    async def gen():
        done = False
        try:
            for i in range(n):
                c = {'id': rid, 'object': 'chat.completion.chunk', 'created': 0, 'model': model, 'choices': [
                    {'index': 0, 'delta': {'role': 'assistant', 'content': f'pong from {model}' if i == 0 else '.'}}]}
                yield f'data: {json.dumps(c)}\n\n'; await asyncio.sleep(delay)
            c = {'id': rid, 'object': 'chat.completion.chunk', 'created': 0, 'model': model, 'usage': usage,
                 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]}
            yield f'data: {json.dumps(c)}\n\ndata: [DONE]\n\n'; done = True
        finally:
            STATE['streams_cancelled'] += 0 if done else 1
    return StreamingResponse(gen(), media_type='text/event-stream')


def _scripted_agent_turn(rid, model, usage, msgs, body):
    """SCRIPTED provider (not a model): turn 1 -> terminal tool call, after a tool result -> finish."""
    head = json.dumps(msgs[:2])
    path = re.search(r'path=(/[^\s"\\]+)', head).group(1)
    tool_results = [m for m in msgs if m.get('role') == 'tool']
    STATE['agent_turns'].append({'tools': sorted(t['function']['name'] for t in body.get('tools') or []),
                                 'tool_results': len(tool_results)})
    ws = re.search(r'ws=(/[^\s"\\]+)', head).group(1)
    script = [('file_editor', {'command': 'create', 'path': f'{ws}/pgwo_marker.txt', 'file_text': 'PGWO_' + '42'}),
              ('file_editor', {'command': 'view', 'path': f'{ws}/pgwo_marker.txt'}),
              ('file_editor', {'command': 'view', 'path': path}),
              ('finish', {'message': 'PGWO agent proof done'})]
    name, args = script[min(len(tool_results), 3)]
    if name != 'finish':
        args['security_risk'] = 'LOW'
    call = {'id': f'call_{uuid.uuid4().hex[:8]}', 'type': 'function',
            'function': {'name': name, 'arguments': json.dumps(args)}}
    return {'id': rid, 'object': 'chat.completion', 'created': 0, 'model': model, 'usage': usage,
            'choices': [{'index': 0, 'finish_reason': 'tool_calls',
                         'message': {'role': 'assistant', 'content': None, 'tool_calls': [call]}}]}


async def state(request):
    return JSONResponse(STATE)

app = Starlette(routes=[Route('/v1/chat/completions', chat, methods=['POST']), Route('/__state', state)])
