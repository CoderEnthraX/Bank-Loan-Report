"""Daily bars from session starts, merging short (<24 bars) segments into the following session."""
def daily2(P):
    if 'daily2' in P: return P['daily2']
    st = [i for i, x in enumerate(P['daystart']) if x]; st.append(len(P['T']))
    seg = list(zip(st[:-1], st[1:])); out = []; carry = None
    for a, b in seg:
        if carry is not None: a = carry; carry = None
        if b - a < 24 and b < len(P['T']): carry = a; continue
        out.append(dict(a=a, b=b, o=P['O'][a], h=max(P['H'][a:b]), l=min(P['L'][a:b]), c=P['C'][b - 1], vw=P['V'][b - 1]))
    P['daily2'] = out; return out
def dayidx2(P, i):
    for k, x in enumerate(daily2(P)):
        if x['a'] <= i < x['b']: return k
