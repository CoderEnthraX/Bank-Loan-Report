step0: read EA (980 lines), clang++ present; design: no-std-header shim, UDL string literals, token preprocessor
step1: mql5shim.h + mq5check.py written; EA first run 0/0 (verifying)
step2: tests/ (17) + run_tests.sh written, stress ok; EA 0/0 pending negative-injection verification
step3: mq_dot pointer rewrite, int->enum downgrade, include handling, stress tests ok; remaining: rerun EA (being edited concurrently by parent), README
step4: README.txt done; EA run -> 0 errors, 0 warnings (file was being edited concurrently; last run 1248 lines)
run-step1: started harness in run/ (create_rt.py -> mql5rt.h, mq5rt.py, driver.cpp, parity.py)
INCIDENT: mq5rt.py CLI bug overwrote the EA with its translation (17:53); parent's commit 9de5f6f captured the corrupted file. Restored by exact inversion (round-trip verified, 0 diff lines) -> EA restored from /tmp/st/E_restored2.mq5; whitespace of C'r,g,b' literals and 'T &a[]' params may differ from the original
run-step2: harness builds (build.sh), parity.py written; running parity
run-step3: build.sh now preprocesses run/EA_copy.mq5 only; mq5rt.py CLI refuses .mq5/.mqh outputs
