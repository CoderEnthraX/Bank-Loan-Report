"""hookeval wrapper (stop_author): TIGHT stop iff first impulse of the session in direction d AND prev daily close-to-close change against d by > 0.2 x daily ATR (RMA14 of session TR), TradingView daily bars (Sunday stub own day), wick-breakout first.
Implementation = r_pdx.py with RULECFG {"ev":["vsl","wick"],"merge":false,"meas":"c2c","unit":"datrr","th":0.2} (impulse event: rng>=0.8 ATR, body>=55%, close within 25% of extreme,
wick beyond prior 10-bar high/low, VWAP slope over 3 bars in d (skipped first 3 session bars); tight stop = max(0.9 ATR, impulse extreme))."""
import os, json, importlib.util
os.environ['RULECFG'] = '{"ev":["vsl","wick"],"merge":false,"meas":"c2c","unit":"datrr","th":0.2}'
_spec = importlib.util.spec_from_file_location('rpdx_candle_c2c_datr_wick', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/r_pdx.py'); _m = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_m)
stop_fn = _m.stop_fn
