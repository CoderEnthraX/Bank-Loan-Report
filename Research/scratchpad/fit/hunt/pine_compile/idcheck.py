import re,sys
src=open(sys.argv[1],encoding='utf-8').read().split('\n')
kw=set('and or not if else for to by while switch var varip true false na int float bool string color line box table array label import export method type enum series simple const continue break in'.split())
builtins=set('open high low close volume time time_tradingday bar_index hlc3 hl2 ohlc4 nz na indicator input plot plotshape alertcondition alert dayofweek timeframe ta math str syminfo barstate color line box table array format size position location shape display alert'.split())
declared={}
used=[]
for i,l in enumerate(src,1):
    code=re.sub(r'"[^"]*"','""',l)
    code=code.split('//')[0]
    code=re.sub(r'#[0-9A-Fa-f]{6,8}','',code)
    # declarations
    m=re.match(r'^\s*(?:var\s+)?(?:(?:int|float|bool|string|color|line|box|table|array<\w+>)\s+)?([A-Za-z_]\w*)\s*=(?!=|>)',code)
    if m: declared.setdefault(m.group(1),i)
    m=re.match(r'^\s*\[([^\]]*)\]\s*=',code)
    if m:
        for n in m.group(1).split(','): declared.setdefault(n.strip(),i)
    m=re.match(r'^([A-Za-z_]\w*)\(([^)]*)\)\s*=>',code)
    if m:
        declared.setdefault(m.group(1),i)
        for p in m.group(2).split(','):
            p=p.split('=')[0].strip().split()
            if p: declared.setdefault(p[-1],i)
    m=re.match(r'^\s*for\s+(\w+)\s*=',code)
    if m: declared.setdefault(m.group(1),i)
    for t in re.finditer(r'(?<![\.\w])([A-Za-z_]\w*)\b',code):
        n=t.group(1)
        # skip named args: name =
        after=code[t.end():]
        if re.match(r'\s*=(?![=>])',after) and t.start()>0 and not re.match(r'^\s*(?:var\s+)?(?:\w+(?:<\w+>)?\s+)?$',code[:t.start()]): continue
        used.append((n,i))
for n,i in used:
    if n in kw or n in builtins: continue
    if n not in declared: print('UNDECLARED',n,i)
    elif declared[n]>i: print('USED BEFORE DECL',n,i,'decl',declared[n])
print('declared',len(declared))
