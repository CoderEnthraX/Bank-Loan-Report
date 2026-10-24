import sys
sys.path.insert(0,'./pylib')
from pynescript.ast import parse
src=open('../../../final.pine',encoding='utf8').read()
try:
    t=parse(src)
    print('parsed ok', len(t.body))
except Exception as e:
    print('ERR', type(e).__name__, str(e)[:500])
