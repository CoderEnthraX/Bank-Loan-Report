"""summary table (ghost mode, exact = baseline minus vetoed): TRAIN/TEST dE2, day-paired TEST CI, syms/10, kept, totR, random-subset null pct (300 draws)."""
import sys, pickle, random
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/research'); sys.path.insert(0,S+'/research/ema'); import lib, ev
tab=pickle.load(open('tab.pkl','rb')); tn,te=lib.split(tab); _,be=lib.split(tab)
NULL={}
def null(share):
    s=round(share,2)
    if s not in NULL:
        r=random.Random(int(s*100)); v=[]
        for _ in range(300):
            k=[x for x in te if r.random()<s]; v.append(ev.E(k)-ev.E(te))
        NULL[s]=sorted(v)
    return NULL[s]
def keep(x,g): return all((x['f'][nm] is None) or (x['f'][nm]>=th if op=='ge' else x['f'][nm]<=th) for nm,op,th in g)
L=[('5m close>EMA20/50/200 (side)',[['px_E200','ge',0]]),('5m EMA50 slope5>0',[['sl_E50_5','ge',0]]),('5m stack 9>21>50',[['stk_9.21.50','ge',2]]),('5m EMA9>EMA21',[['stk_9.21','ge',1]]),
('5m full stack 9>20>50>100>200',[['stk_9.20.50.100.200','ge',4]]),('15m EMA20>EMA50',[['h15_rs_E20_E50','ge',0]]),('15m stack 9>21>50',[['h15_stk_9.21.50','ge',2]]),('1h EMA20>EMA50',[['h60_rs_E20_E50','ge',0]]),('1h close>EMA50',[['h60_px_E50','ge',0]]),
('chop veto 5m EMA9/21 width>=0.25ATR',[['rw_E9_E21','ge',0.25]]),('chop veto 9/21/50 spread>=0.5ATR',[['sp_9.21.50','ge',0.5]]),('chop veto |EMA20 slope5|>=0.25ATR',[['asl_E20_5','ge',0.25]]),
('chop veto close x EMA20 (24 bars)<=4',[['xc_C_E20_24','le',4]]),('chop veto EMA9xEMA21 (48)<=2',[['xc_E9_E21_48','le',2]]),('chop veto |EMA20-VWAP|>=0.3ATR',[['ave_E20','ge',0.3]]),('chop veto 15m EMA9/21 width>=0.25',[['h15_rw_E9_E21','ge',0.25]]),
('EMA20 on trade side of VWAP',[['ve_E20','ge',0]]),('pullback touched EMA20 in 6 bars',[['pb_E20_6','le',0]]),('SMA50 slope>0',[['sl_S50_5','ge',0]]),('EMA20>SMA20',[['rs_E20_S20','ge',0]]),
('HMA20 slope3>0',[['sl_HMA_3','ge',0]]),('KAMA |slope5|>=0.2 (not flat)',[['asl_KAMA_5','ge',0.2]]),('entry <=2 ATR from EMA20',[['en_E20','le',2.0]]),
('FIT 1h |EMA20 slope3|<=1.65',[['h60_asl_E20_3','le',1.652]]),('FIT 1h |EMA20 slope3|<=2.0',[['h60_asl_E20_3','le',2.0]]),('FIT 1h EMA9 slope3<=1.62',[['h60_sl_E9_3','le',1.622]]),('FIT 5m EMA200 slope10<=0.55',[['sl_E200_10','le',0.547]]),
('FIT 5-EMA spread<=6.2ATR',[['sp_9.20.50.100.200','le',6.218]]),('FIT 15m EMA200 slope3<=0.20',[['h15_sl_E200_3','le',0.201]]),('FIT 15m EMA20-50 width<=2.89',[['h15_rw_E20_E50','le',2.885]]),
('FIT close x VWAP in 24>=1',[['xc_C_V_24','ge',1]]),('FIT |EMA50-VWAP|<=1.37',[['ave_E50','le',1.372]]),('FIT entry<=2.94ATR from EMA50',[['en_E50','le',2.94]]),('FIT pullback EMA50 (6)<=1.23',[['pb_E50_6','le',1.226]]),('FIT TRAIN-top h15 EMA9/21 width<=0.91',[['h15_rw_E9_E21','le',0.911]])]
print('%-38s %8s %8s %18s %6s %5s %5s %5s'%('idea (ghost mode)','dTRAIN','dTEST','pairedCI TEST','syms','kept','totR','null%'))
for t,g in L:
    a=[x for x in tn if keep(x,g)]; b=[x for x in te if keep(x,g)]; al=a+b; d=ev.E(b)-ev.E(te); lo,hi=ev.paired_ci(te,b,it=1000)
    nl=null(len(b)/len(te))
    print('%-38s %+8.3f %+8.3f [%+.3f,%+.3f] %3d/10 %4.0f%% %+5.0f %5.2f'%(t,ev.E(a)-ev.E(tn),d,lo,hi,ev.syms_better(tab,al)[0],100*len(al)/len(tab),sum(x['res'] for x in al),ev.pct(nl,d)))
