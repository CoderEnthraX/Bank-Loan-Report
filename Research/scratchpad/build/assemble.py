"""Build the indicator and the strategy from the shared blocks, then prove the shared parts are byte-identical."""
import re, sys
B = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/'
R = '/home/user/Bank-Loan-Report/TradingView/'
INP = open(B + 'shared_inputs.pine').read().rstrip('\n')
ENG = open(B + 'shared_engine.pine').read().rstrip('\n')
for tpl, out in (('indicator_template.pine', 'Auction_Retest_Model.pine'), ('strategy_template.pine', 'Auction_Retest_Strategy.pine')):
    s = open(B + tpl).read()
    assert s.count('{{INPUTS}}') == 1 and s.count('{{ENGINE}}') == 1
    s = s.replace('{{INPUTS}}', INP).replace('{{ENGINE}}', ENG)
    open(R + out, 'w').write(s)
def blocks(path):
    s = open(path).read(); out = {}
    for name in ('ENGINE INPUTS', 'ENGINE', 'STATS', 'DRAW'):
        m = re.search(r'// >>> ' + name + r' BEGIN.*?// <<< ' + name + ' END', s, re.S)
        out[name] = m.group(0) if m else None
    return out
a = blocks(R + 'Auction_Retest_Model.pine'); b = blocks(R + 'Auction_Retest_Strategy.pine')
ok = True
for k in a:
    same = a[k] is not None and a[k] == b[k]
    ok &= same
    print(f'{k:14s} indicator {len(a[k] or "")} chars, strategy {len(b[k] or "")} chars, byte-identical: {same}')
print('SHARED BLOCKS IDENTICAL' if ok else 'MISMATCH'); sys.exit(0 if ok else 1)
