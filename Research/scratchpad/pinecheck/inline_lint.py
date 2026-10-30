"""TradingView warning: inputs sharing an `inline` id must have a title only on the first input of the line ("" for the others).
Usage: inline_lint.py FILE.pine ... -> prints line:col and the inline id of every input that would get the warning."""
import re, sys
def calls(src):
    """every input.*( ... ) call with its start offset, args text (balanced parentheses, strings respected)"""
    for m in re.finditer(r'\binput\.\w+\s*\(', src):
        i = m.end(); depth = 1; q = None; j = i
        while j < len(src) and depth:
            ch = src[j]
            if q:
                if ch == '\\': j += 1
                elif ch == q: q = None
            elif ch in '"\'': q = ch
            elif ch == '(': depth += 1
            elif ch == ')': depth -= 1
            j += 1
        yield m.start(), src[i:j - 1]
def split_args(a):
    out = []; depth = 0; q = None; cur = ''
    for k, ch in enumerate(a):
        if q:
            cur += ch
            if ch == '\\': continue
            if ch == q and (k == 0 or a[k - 1] != '\\'): q = None
            continue
        if ch in '"\'': q = ch; cur += ch; continue
        if ch in '([': depth += 1
        if ch in ')]': depth -= 1
        if ch == ',' and depth == 0: out.append(cur.strip()); cur = ''; continue
        cur += ch
    if cur.strip(): out.append(cur.strip())
    return out
def lint(path):
    src = open(path, encoding='utf8').read(); first = {}; bad = []
    for off, a in calls(src):
        args = split_args(a); kw = {}; pos = []
        for x in args:
            m = re.match(r'^(\w+)\s*=(?!=)\s*(.*)$', x, re.S)
            if m: kw[m.group(1)] = m.group(2).strip()
            else: pos.append(x)
        if 'inline' not in kw: continue
        title = kw.get('title', pos[1] if len(pos) > 1 else None)
        iid = kw['inline'].strip('"\'')
        line = src.count('\n', 0, off) + 1; col = off - (src.rfind('\n', 0, off) + 1) + 1
        if iid not in first: first[iid] = line; continue
        if title is not None and title not in ('""', "''"): bad.append((line, col, iid, title))
    return bad
if __name__ == '__main__':
    for p in sys.argv[1:]:
        b = lint(p); print('%s: %d inline-title warnings' % (p.split('/')[-1], len(b)))
        for line, col, iid, t in b: print('   %d:%d  inline "%s"  title %s' % (line, col, iid, t[:40]))
