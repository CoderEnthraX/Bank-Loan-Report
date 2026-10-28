import sys
from pynescript.ast import parse
for p in sys.argv[1:]:
    src = open(p, encoding='utf8').read()
    try:
        t = parse(src); print('parsed ok', len(t.body), p.split('/')[-1])
    except Exception as e:
        print('ERR', p.split('/')[-1], type(e).__name__, str(e)[:800])
    lines = src.split('\n')
    tabs = sum(1 for l in lines if '\t' in l); trail = sum(1 for l in lines if l != l.rstrip())
    bad = [i + 1 for i, l in enumerate(lines) if l.strip() and (len(l) - len(l.lstrip(' '))) % 4 != 0 and not l.lstrip().startswith('//')]
    print('   tabs', tabs, 'trailing spaces', trail, 'indent not x4 (non-comment, may be line continuations):', bad[:20])
