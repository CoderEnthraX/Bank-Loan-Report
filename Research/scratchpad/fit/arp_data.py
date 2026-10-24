"""Shared loader for the exported 5m CSVs (times are IST, +05:30)."""
import csv, os
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
SYMS = {'GC':'COMEX_DL_GC1','EURUSD':'FX_IDC_EURUSD','NASDAQ':'IG_NASDAQ','US30':'BLACKBULL_US30',
        'CRUDE':'MCX_CRUDEOIL1','NIFTY':'NSE_DLY_NIFTY','SENSEX':'BSE_DLY_SENSEX','ETH':'BITSTAMP_ETHUSD'}
def load(sym):
    f = SYMS.get(sym, sym)
    rows = []
    for i, r in enumerate(csv.DictReader(open(os.path.join(DATA, f + '.csv')))):
        rows.append(dict(i=i, t=r['time'][:16].replace('T', ' '), o=float(r['open']), h=float(r['high']),
                         l=float(r['low']), c=float(r['close']), vwap=float(r['VWAP']) if r['VWAP'] not in ('', 'NaN') else None,
                         lf=r['Long Fill'] == '1', sf=r['Short Fill'] == '1'))
    return rows
def find(rows, t):
    for r in rows:
        if r['t'] == t: return r['i']
    raise KeyError(t)
