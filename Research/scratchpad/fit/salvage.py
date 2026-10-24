"""Turn interrupted workflow-agent transcripts into progress digests so a restarted agent resumes instead of redoing work.
Usage: python3 -I salvage.py <workflow transcript dir> <out dir>
Writes <out>/progress_<group>.md for every agent that has no completed result in journal.jsonl, and <out>/done_<group>.json for completed ones."""
import json, sys, os, glob
W, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
done = {}
for l in open(os.path.join(W, 'journal.jsonl')):
    try: d = json.loads(l)
    except Exception: continue
    if d.get('type') == 'result' and d.get('result'):
        done[d.get('agentId') or d.get('label')] = d.get('result')
def short(x, n):
    x = x if isinstance(x, str) else json.dumps(x)
    return x if len(x) <= n else x[:n] + f' …[+{len(x)-n} chars]'
for meta in glob.glob(os.path.join(W, 'agent-*.meta.json')):
    m = json.load(open(meta)); lab = m.get('label') or m.get('description') or os.path.basename(meta)
    aid = os.path.basename(meta)[len('agent-'):-len('.meta.json')]
    if aid in done or lab in done: continue
    tr = meta.replace('.meta.json', '.jsonl')
    if not os.path.exists(tr): continue
    lines = []; pending = {}
    for l in open(tr):
        try: d = json.loads(l)
        except Exception: continue
        msg = d.get('message') or {}
        content = msg.get('content') if isinstance(msg, dict) else None
        if not isinstance(content, list): continue
        for c in content:
            t = c.get('type')
            if t == 'text' and msg.get('role') == 'assistant' and c.get('text', '').strip():
                lines.append('NOTE: ' + c['text'].strip())
            elif t == 'tool_use':
                inp = c.get('input', {})
                if c.get('name') == 'Read' and str(inp.get('file_path', '')).endswith('.png'):
                    pending[c['id']] = None  # image views carry no text worth keeping
                    lines.append('VIEWED ' + inp['file_path'])
                else:
                    pending[c['id']] = short(inp.get('command') or inp, 400)
            elif t == 'tool_result':
                cmd = pending.pop(c.get('tool_use_id'), None)
                if cmd is None: continue
                out = c.get('content')
                if isinstance(out, list): out = ' '.join(x.get('text', '') for x in out if isinstance(x, dict))
                lines.append('RAN: ' + cmd + '\n  -> ' + short(str(out).strip(), 900).replace('\n', '\n     '))
    g = lab.split(':')[-1]
    with open(os.path.join(OUT, f'progress_{g}.md'), 'w') as f:
        f.write(f'# Progress of the interrupted analyst "{lab}" (chronological; reuse every result here, do not redo it)\n\n' + '\n'.join(lines) + '\n')
    print(lab, 'steps', len(lines), 'bytes', os.path.getsize(os.path.join(OUT, f'progress_{g}.md')))
print('completed agents:', list(done))
