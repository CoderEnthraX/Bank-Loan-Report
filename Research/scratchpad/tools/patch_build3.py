p='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gold/build_final.py'; s=open(p).read()
a="""                put(ws, r, 2, '%s%s: net $%s, max drawdown $%s (%.0f%%) vs Off: net $%s, max drawdown $%s' % (b['mode'], ' + $500 cap' if b['cap'] else '', format(round(b['net']), ','),
                    format(round(b['maxDD']), ','), 100 * b['maxDDpct'], format(round(off['net']), ','), format(round(off['maxDD']), ',')), wrap=True)"""
b="""                if b['mode'] == 'Off':
                    txt = 'Off (fixed $50 risk) gives the best profit for the drawdown: net $%s, max drawdown $%s (%.0f%%) on $10,000 - no recovery rule beat it.' % (
                        format(round(b['net']), ','), format(round(b['maxDD']), ','), 100 * b['maxDDpct'])
                else:
                    txt = '%s%s: net $%s, max drawdown $%s (%.0f%%), largest single risk $%s - vs Off: net $%s, max drawdown $%s (%.0f%%).' % (
                        b['mode'], ' + $500 cap' if b['cap'] else '', format(round(b['net']), ','), format(round(b['maxDD']), ','), 100 * b['maxDDpct'],
                        format(round(b['maxRisk']), ','), format(round(off['net']), ','), format(round(off['maxDD']), ','), 100 * off['maxDDpct'])
                put(ws, r, 2, txt, wrap=True)"""
assert s.count(a)==1; s=s.replace(a,b)
a2="""         'SHEETS: Best settings | Summary | <TF> default / best / low-streak (year x month) | TP1-TP4 | Settings sweep | Combinations | Exits | Recovery rules | Streak math']"""
b2="""         'SHEETS: Best settings | Summary | <TF> default / best / low-streak (year x month) | TP1-TP4 | Settings sweep | Combinations | Exits | Recovery rules | Robustness | Streak math']"""
assert s.count(a2)==1; s=s.replace(a2,b2)
open(p,'w').write(s); print('ok')
