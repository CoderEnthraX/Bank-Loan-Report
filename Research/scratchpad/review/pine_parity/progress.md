# pine_parity progress
- [x] read ref.py, shared_engine.pine, shared_inputs.pine, indicator_template.pine, engine.py helpers
- [x] statement-by-statement read: no logic diff found in steps 1/2/3, half stop, leg reset, filters; only warm-up start-of-chart differences
- [ ] literal Pine-semantics emulation (emu.py) vs ref.py on the 10 instruments
- NOTE: build/ref.py and shared_engine.pine changed at 11:24/11:26 (stop/target tolerance mt*0.001); snapshots saved here; emu updated
- first emu run (pre-tolerance): all cases identical except 'fast warmup' (start-of-chart warm-up only)
- [x] emu rerun with tolerance: 18/19 option cases trade-for-trade identical on 10 instruments (incl. half/ghost flags); only 'fast warmup' differs (start of chart)
- [x] DRAW / alerts / table / R stats read; minor: line cleanup uses 4*maxDrawn though each trade draws exitK lines
- DONE: report = 2 minor findings
