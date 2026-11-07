# progress
- step1: read recovery.py/geng.py (monthly.py NOT read). monthly_trades.pkl not yet present at start; background 'monthly.py collect' running (uses ~6.6GB RAM; run my engine one strategy at a time).
- step2: writing /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/verify_monthly/verify.py (stages: engine -> cache in /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/verify_monthly/eng_<key>_<file>.pkl ; compare)
- step3: monthly_trades.pkl now exists; running engine stage per strategy (eng_*.pkl cache)
- DONE: all compared identical; see compare.out
