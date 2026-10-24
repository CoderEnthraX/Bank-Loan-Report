# tight (max(0.9A, disp-candle extreme)) when level 'vwap' (d*(level-entry)/ATR) lies in (-1.8, 0); else 1.8 ATR
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from rulelib import make
stop_fn = make('vwap', -1.8, 0)
