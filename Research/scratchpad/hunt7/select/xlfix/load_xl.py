"""Load the student's Excel trade log -> list of dicts (sym in engine names)."""
import openpyxl, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trades.xlsx')
MAP = {'NIFTY': 'NIFTY', 'SENSEX': 'SENSEX', 'CRUDEOIL': 'CRUDE', 'NATURAL GAS': 'NATGAS'}
def load():
    ws = openpyxl.load_workbook(P, data_only=True).worksheets[0]
    out = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None or r[1] is None: continue
        e, s = float(r[7]), float(r[8])
        out.append(dict(n=r[0], date=r[1], tin=r[2], tout=r[3], sym=MAP[r[5]], entry=e, stop=s, d=1 if s < e else -1,
                        risk=float(r[10]), maxtp=r[16], netrr=r[17], peak=r[19]))
    return out
