import sys, io, contextlib
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/halfstop3')
with contextlib.redirect_stdout(io.StringIO()):
    import tab3
R = [r for r in tab3.rows if r['m'] is not None]
for N in range(2, 13):
    for b in (0, 0.1, 0.2, 0.22, 0.3, 0.5):
        brk = []; fix = []
        for r in R:
            P = r['P']; j = r['j']; d = r['d']; A = r['A']; e = r['e']
            sw = min(P['L'][j-N+1:j+1]) if d > 0 else max(P['H'][j-N+1:j+1])
            sR = d * (e - (sw - d * b * A)) / A
            cur = 0.9 if r['m']['half'] else 1.8  # rough
            curR = r['d'] * (e - r['m']['stop']) / A
            newR = min(curR, sR) if sR > 0 else curR
            okOld = abs(curR - r['logR']) <= 0.12; okNew = abs(newR - r['logR']) <= 0.12
            if okOld and not okNew: brk.append(r['src'] + ' ' + r['sym'][:6] + ' ' + r['ft'])
            if okNew and not okOld: fix.append(r['src'] + ' ' + r['ft'])
        if len(brk) <= 3: print(N, b, 'broken', len(brk), brk, 'fixed', fix)
        else: print(N, b, 'broken', len(brk), 'fixed', fix)
