"""pre-specified conventional MA rules (natural thresholds, no fitting) + per-family TRAIN-best; ghost mode on the baseline list (exact)."""
import sys, pickle, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab)
def keep(x,g): return all((x['f'][nm] is None) or (x['f'][nm]>=th if op=='ge' else x['f'][nm]<=th) for nm,op,th in g)
def line(tag,g):
    a=[x for x in tn if keep(x,g)]; b=[x for x in te if keep(x,g)]; al=a+b
    print('%-34s TRAIN keep %3.0f%% dE %+.3f | TEST keep %3.0f%% dE %+.3f | ALL keep %3.0f%% tot %+4.0f syms %d/10'%(tag,100*len(a)/len(tn),ev.E(a)-ev.E(tn),100*len(b)/len(te),ev.E(b)-ev.E(te),100*len(al)/len(tab),sum(x['res'] for x in al),ev.syms_better(tab,al)[0]))
CONV=[('5m close>EMA20',[['px_E20','ge',0]]),('5m close>EMA50',[['px_E50','ge',0]]),('5m close>EMA200',[['px_E200','ge',0]]),
('5m EMA20 slope3>0',[['sl_E20_3','ge',0]]),('5m EMA50 slope5>0',[['sl_E50_5','ge',0]]),('5m EMA200 slope10>0',[['sl_E200_10','ge',0]]),
('5m stack 9>21>50',[['stk_9.21.50','ge',2]]),('5m stack 9>21',[['stk_9.21','ge',1]]),('5m stack 20>50',[['stk_20.50','ge',1]]),('5m stack 50>200',[['stk_50.200','ge',1]]),('5m full stack 9>20>50>100>200',[['stk_9.20.50.100.200','ge',4]]),
('15m close>EMA20',[['h15_px_E20','ge',0]]),('15m close>EMA50',[['h15_px_E50','ge',0]]),('15m EMA20 slope>0',[['h15_sl_E20_3','ge',0]]),('15m stack 9>21>50',[['h15_stk_9.21.50','ge',2]]),('15m EMA20>EMA50',[['h15_rs_E20_E50','ge',0]]),('15m EMA20>VWAP',[['h15_ve_E20','ge',0]]),
('1h close>EMA20',[['h60_px_E20','ge',0]]),('1h close>EMA50',[['h60_px_E50','ge',0]]),('1h EMA20 slope>0',[['h60_sl_E20_3','ge',0]]),('1h stack 9>21>50',[['h60_stk_9.21.50','ge',2]]),('1h EMA20>EMA50',[['h60_rs_E20_E50','ge',0]]),
('chop: EMA9/21 width>=0.25ATR',[['rw_E9_E21','ge',0.25]]),('chop: 9/21/50 spread>=0.5ATR',[['sp_9.21.50','ge',0.5]]),('chop: |EMA20 slope5|>=0.25ATR',[['asl_E20_5','ge',0.25]]),
('chop: closeXEMA20 in 24 bars<=4',[['xc_C_E20_24','le',4]]),('chop: EMA9xEMA21 in 48 bars<=2',[['xc_E9_E21_48','le',2]]),('chop: closeXVWAP in 48 bars<=3',[['xc_C_V_48','le',3]]),
('chop: |EMA20-VWAP|>=0.3ATR',[['ave_E20','ge',0.3]]),('chop: 15m EMA9/21 width>=0.25',[['h15_rw_E9_E21','ge',0.25]]),('chop: 15m |EMA20 slope|>=0.15',[['h15_asl_E20_3','ge',0.15]]),
('VWAP slope & EMA20 slope agree',[['sl_E20_3','ge',0]]),('EMA20 on trade side of VWAP',[['ve_E20','ge',0]]),('EMA50 on trade side of VWAP',[['ve_E50','ge',0]]),
('pullback: touched EMA20 in 6 bars',[['pb_E20_6','le',0]]),('pullback: touched EMA9 in 3 bars',[['pb_E9_3','le',0]]),('pullback: touched EMA50 in 10 bars',[['pb_E50_10','le',0]]),
('SMA: close>SMA20',[['px_S20','ge',0]]),('SMA: SMA50 slope>0',[['sl_S50_5','ge',0]]),('EMA20>SMA20',[['rs_E20_S20','ge',0]]),
('HMA20 slope>0',[['sl_HMA_3','ge',0]]),('close>HMA20',[['px_HMA','ge',0]]),('close>KAMA',[['px_KAMA','ge',0]]),('KAMA slope>0',[['sl_KAMA_5','ge',0]]),('KAMA |slope|>=0.2 (not flat)',[['asl_KAMA_5','ge',0.2]]),
('entry <=2 ATR from EMA20',[['en_E20','le',2.0]]),('entry <=3 ATR from EMA20',[['en_E20','le',3.0]]),('entry <=1.5 ATR from EMA9',[['en_E9','le',1.5]])]
print('== conventional (pre-specified thresholds), ghost mode exact on the baseline list')
for t,g in CONV: line(t,g)
