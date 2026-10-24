# tight (max(0.9A, disp-candle extreme)) when level 'pdfav' (d*(level-entry)/ATR) lies in (0, 3.6); else 1.8 ATR
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from rulelib import make
stop_fn = make('pdfav', 0, 3.6)
