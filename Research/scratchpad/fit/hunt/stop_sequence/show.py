import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
rows, _ = table(True)
K = ['n','cumR','dd','winpct','sumR3','sumR5','sumR10','lstreak','wstreak','dayFills','dayR','gap','prevTight','prevSame','prevRes','sameRun','cancSinceExit','armsSinceExit','armsToday','cancToday','prevArmFilled','barsPrevArm','tr48','tr288']
print(' '*30, ' '.join(f'{k[:7]:>7s}' for k in K))
for t, f in rows:
    if not f: print(t['sym'], t['fill'], 'none'); continue
    print(f"{t['sym']:6s} {t['fill'][5:]} {'L' if t['d']>0 else 'S'} {'TIGHT' if t['tight'] else '     '}", ' '.join(f'{(round(f[k],2) if isinstance(f[k],float) else f[k]):>7}' for k in K))
