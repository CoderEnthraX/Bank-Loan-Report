"""how MA filters treat the ORIGINAL indicator's trades (screenshots S/gt/final + student log S/xl)."""
import sys, json, glob, pickle
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research/ema'); sys.path.insert(0,S+'/xl'); import feats, ref_ema, load_xl
OT={}
for f in sorted(glob.glob(S+'/gt/final/*.json')):
    for x in json.load(open(f)).get('orig_trades',[]):
        k=(x['symbol'],x['fill_bar'],x['dir'])
        if k not in OT and x.get('outcome') in ('tp4','stop'): OT[k]=dict(src='shot',sym=x['symbol'],t=x['fill_bar'],d=1 if x['dir']=='long' else -1,win=x['outcome']=='tp4',entry=x.get('entry_exact') or x.get('entry_measured'))
SM={'NATGAS':'MCX_NATURALGAS'}
for x in load_xl.load():
    if x['maxtp'] not in ('TP 4','SL'): continue
    sym=SM.get(x['sym'],x['sym']); k=(sym,'%s %s'%(x['date'],x['tin']),'long' if x['d']>0 else 'short')
    if k not in OT: OT[k]=dict(src='xl',sym=sym,t=k[1],d=x['d'],win=x['maxtp']=='TP 4',entry=x['entry'])
RUN={}; rows=[]; miss=0
for k,o in OT.items():
    try: P=feats.prepare(o['sym'])
    except Exception as e: miss+=1; continue
    if o['t'] not in P['T']: miss+=1; continue
    fi=P['T'].index(o['t'])
    if o['sym'] not in RUN: RUN[o['sym']]=ref_ema.run(o['sym'])
    m=[x for x in RUN[o['sym']] if x['fill']==fi and x['dir']==o['d']]
    arm=m[0]['arm'] if m else fi-1; o['matched']=bool(m)
    F=feats.compute(o['sym']); o['f']={nm:feats.value(F,nm,arm,o['d'],m[0]['entry'] if m else o['entry']) for nm in feats.names()}; rows.append(o)
pickle.dump(rows,open('orig.pkl','wb'))
W=sum(o['win'] for o in rows); L=len(rows)-W
print('orig trades used %d (wins %d, losses %d; engine-matched %d; unmapped %d)'%(len(rows),W,L,sum(o['matched'] for o in rows),miss))
G=[('h60 |EMA20 slope3|<=1.65',[['h60_asl_E20_3','le',1.652]]),('1h EMA9 slope3<=1.62',[['h60_sl_E9_3','le',1.622]]),('5m EMA200 slope10<=0.55',[['sl_E200_10','le',0.547]]),
   ('5MA spread<=6.2',[['sp_9.20.50.100.200','le',6.218]]),('15m EMA200 slope3<=0.20',[['h15_sl_E200_3','le',0.201]]),('15m EMA20-50 width<=2.89',[['h15_rw_E20_E50','le',2.885]]),('closeXVWAP in 24>=1',[['xc_C_V_24','ge',1]]),
   ('15m EMA20>EMA50',[['h15_rs_E20_E50','ge',0]]),('1h EMA20>EMA50',[['h60_rs_E20_E50','ge',0]]),('5m stack 9>21>50',[['stk_9.21.50','ge',2]]),('5m EMA9>EMA21',[['stk_9.21','ge',1]]),('close>EMA200',[['px_E200','ge',0]]),
   ('chop veto: EMA9/21 width>=0.25',[['rw_E9_E21','ge',0.25]]),('chop veto: |EMA20 slope5|>=0.25',[['asl_E20_5','ge',0.25]]),('chop veto: closeXEMA20/24<=4',[['xc_C_E20_24','le',4]]),('chop veto: |EMA20-VWAP|>=0.3',[['ave_E20','ge',0.3]]),
   ('pullback: touched EMA20 in 6',[['pb_E20_6','le',0]]),('entry<=2ATR from EMA20',[['en_E20','le',2.0]])]
def keep(o,g): return all(o['f'][nm] is None or (o['f'][nm]>=th if op=='ge' else o['f'][nm]<=th) for nm,op,th in g)
print('%-34s %s'%('filter','kept wins / kept losses  (removed wins, removed losses)  kept win-rate (base %.0f%%)'%(100*W/len(rows))))
for t,g in G:
    kw=sum(1 for o in rows if o['win'] and keep(o,g)); kl=sum(1 for o in rows if not o['win'] and keep(o,g))
    print('%-34s %2d/%-2d  (-%d W, -%d L)  %.0f%%'%(t,kw,kl,W-kw,L-kl,100*kw/max(1,kw+kl)))
