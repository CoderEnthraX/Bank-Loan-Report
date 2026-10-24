"""What are the CSV 'Long Fill/Short Fill/Event' columns? Compare with model fills/arms and with the student log."""
import sys, csv
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, S+'/hunt3/data')
from engine2 import prepare
from arp_data import SYMS
from load_xl import load
import dm
for sym in ('CRUDE', 'SENSEX', 'ETH'):
    P = prepare(sym); T = P['T']; idx = {t:i for i,t in enumerate(T)}
    rows = list(csv.DictReader(open(f"{S}/data/{SYMS[sym]}.csv")))
    lf = {i for i,r in enumerate(rows) if r['Long Fill']=='1'}; sf = {i for i,r in enumerate(rows) if r['Short Fill']=='1'}
    le = {i for i,r in enumerate(rows) if r['Long Event']=='1'}; se = {i for i,r in enumerate(rows) if r['Short Event']=='1'}
    print(sym, 'LF==LE', lf==le, 'SF==SE', sf==se)
    for inp in ({}, {"dayStopR":0}):
        tr = dm.run(sym, inp)
        mf = {t['fill'] for t in tr if t['dir']>0}; ma = {t['arm'] for t in tr if t['dir']>0}
        print('  model', inp, 'long fills', len(mf), 'csvLF', len(lf), 'common fill', len(mf&lf), 'common arm', len(ma&lf), 'csv +-1 of fill', sum(1 for i in lf if i in mf or i-1 in mf or i+1 in mf))
    X = [x for x in load() if x['sym']==sym]
    hit = sum(1 for x in X if idx.get(x['date']+' '+x['tin']) in (lf|sf))
    print('  student log fills on csv fill flags:', hit, '/', len(X))
    print('  csv flags first/last:', T[min(lf|sf)], T[max(lf|sf)])
