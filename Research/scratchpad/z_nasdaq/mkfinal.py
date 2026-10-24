import json
ck=[json.loads(l) for l in open('ckpt_nasdaq.jsonl')]
wins=[]
for c in ck:
    w=c['window']; wins.append(dict(image=c['image'],symbol=w['symbol'],first_bar=w['first_bar'],last_bar=w['last_bar'],anchor=w.get('anchor','')))
wins.insert(1,dict(image='952800b0',symbol='NASDAQ',first_bar='2026-10-07 20:35',last_bar='2026-10-08 09:20',anchor='duplicate of 33f61af2 (identical box geometry)'))
# unique orig trades: keep the most complete record per fill_bar
best={}
for c in ck:
    for t in c['orig_trades']:
        k=t['fill_bar']
        if k not in best or (t['outcome']!='open' and best[k]['outcome']=='open') : best[k]=dict(t)
        else:
            best[k]['images']=sorted(set(best[k].get('images',[]))|set(t.get('images',[])))
# fixes
b=best['2026-10-08 08:05']; b['confidence']='high'; b['notes']+='; entry 31208.1 also confirmed by the 8-9 bar breakout rule (07:55 H is the prior-8-bar high, > 08:00 body mid 31207.25); R/ATR14 1.82'
b=best['2026-10-09 12:55']; b['outcome']='stop'; b['exit_bar']='2026-10-09 16:00'; b['stop_measured']=30963.8; b['r_from_green_box']=36.4; b['entry_exact_source']='TABLE ENTRY 31000.2 (d6895f2d) = 12:35 high, the prior-8-bar high broken by the 12:50 bull impulse (O30979.9 C31001.8; body mid 30990.85 not used)'; b['table_values']='LONG ACTIVE, ADX 36, ENTRY 31000.2, STOP 30963.8, TP1 31022.1, TP2 31036.6, TP3 31054.9, TP4 31073.1, LIVE/BARS -0.20R 9, TARGETS 0/3, MODEL DAY 2W/2L 50% +2.00R, FILLS/CAP 5/5'; b['images']=['f5f38768','2022bd5c','d6895f2d','ff13bd75']
b=best['2026-10-12 11:15']; b['table_values']='SHORT ACTIVE, RANGING ADX 32, BIAS NEUTRAL, ENTRY 30984.1, STOP 31014.2, TP1 30966.0, TP2 30954.0, TP3 30938.9, TP4 30923.9, LIVE/BARS +1.11R 19, TARGETS HIT 3/3, MODEL DAY 1W/0L 100% +2.00R, FILLS/CAP 2/5'; b['stop_measured']=31014.2; b['entry_measured']=30984.1
b=best['2026-10-09 06:05']; b['notes']+='; R/ATR14(at impulse 06:00)=0.90 = HALF the usual 1.8 (all other 12 trades R=1.78-1.82 x ATR14 RMA)'
orig=[best[k] for k in sorted(best)]
mv=[]; seen=set()
for c in ck:
    for m in c['my_vs_orig']:
        k=(m['status'],m.get('my_fill_bar',m.get('orig_fill_bar')))
        if k in seen:
            for x in mv:
                if (x['status'],x.get('my_fill_bar',x.get('orig_fill_bar')))==k and m.get('notes','') and not m['notes'].startswith('see '): x['notes']=x.get('notes','')+' | '+m['notes']
            continue
        seen.add(k); mv.append(dict(m))
mv.sort(key=lambda m:m.get('my_fill_bar',m.get('orig_fill_bar')))
tables=["39f7f90d / overlay on 33f61af2,952800b0,1d1eef0a,f5f38768,2022bd5c (Mon 12, 12:45): STATE SHORT ACTIVE; REGIME RANGING ADX 32; BIAS NEUTRAL; ENTRY 30984.1; STOP 31014.2; TP1 30966.0; TP2 30954.0; TP3 30938.9; TP4 30923.9; LIVE/BARS +1.11R 19 (+1.09R in another frame); TARGETS HIT 3/3 reached; MODEL DAY 1W/0L 100% +2.00R; FILLS/CAP 2/5; LOADED BARS TP4 +2.00R 38% +51.00R",
"d6895f2d & ff13bd75 (Fri 9, 13:40): STATE LONG ACTIVE; RANGING ADX 36; BIAS NEUTRAL; ENTRY 31000.2; STOP 30963.8; TP1 31022.1; TP2 31036.6; TP3 31054.9; TP4 31073.1; LIVE/BARS -0.20R 9; TARGETS HIT 0/3 reached; MODEL DAY 2W/2L 50% +2.00R; FILLS/CAP 5/5; LOADED BARS TP4 +2.00R 38% +52.00R"]
obs=open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/z_nasdaq/obs.txt').read().strip()
out=dict(group='nasdaq',windows=wins,orig_trades=orig,my_vs_orig=mv,observations=obs,table_readings=tables)
json.dump(out,open('final/nasdaq.json','w'),indent=1)
print(len(orig),len(mv))
for t in orig: print(t['fill_bar'],t['dir'],t.get('entry_exact'),t['stop_measured'],t['outcome'],t['exit_bar'])
for m in mv: print(m['status'],m.get('my_fill_bar'),m.get('orig_fill_bar'))
