import sys, os; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from gtscore import load_gt
from arp_data import load
tr,_ = load_gt('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/final')
for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    R = load(s)
    csvf = {(r['t'], 1 if r['lf'] else -1) for r in R if r['lf'] or r['sf']}
    gt = {(t['fill'], t['d']) for t in tr if t['sym']==s}
    win = {x for x in csvf if '2026-10-05' <= x[0] <= '2026-10-12 23:59'}
    print(s, 'csv fills total', len(csvf), 'in window', len(win), 'gt', len(gt), 'gt∩csv', len(gt & csvf))
