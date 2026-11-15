"""Every identifier the Pine file reads must be defined in the file (variable, function, method, parameter, loop / tuple variable, type)
or be a Pine built-in namespace / variable. Uses the pynescript AST."""
import sys
from pynescript.ast import parse
import pynescript.ast as A
src = open(sys.argv[1], encoding='utf8').read(); tree = parse(src)
BUILTIN = set('''open high low close time bar_index na true false math str ta array line label table color size position text input timeframe syminfo
barstate barmerge request alert format dayofweek hour year month dayofmonth timestamp extend xloc yloc display plot shape location strategy int float bool string
nz fixnan max_bars_back runtime log minute time_close currency second last_bar_index'''.split())
defined = set(); used = []; seen = set()
def walk(n, ctx=None):
    if isinstance(n, list):
        for x in n: walk(x)
        return
    if not isinstance(n, A.AST) or id(n) in seen: return
    seen.add(id(n))
    t = type(n).__name__
    if t == 'Name':
        if isinstance(getattr(n, 'ctx', None), A.Store): defined.add(n.id)
        else: used.append(n.id)
    if t in ('FunctionDef', 'MethodDef'):
        defined.add(n.name)
        for a in n.args: defined.add(a.name)
    if t == 'TypeDef': defined.add(n.name)
    for f in getattr(n, '_fields', ()):
        walk(getattr(n, f, None))
walk(tree.body)
undef = sorted(set(u for u in used if u not in defined and u not in BUILTIN))
print('identifiers read: %d distinct, defined: %d, undefined (not built-in): %s' % (len(set(used)), len(defined), undef or 'none'))
