# Fractal Breakout Grid EA (MT5) - progress (resume from here)
Asked 2026-11-15: (1) "make the strategy move the stop inside the candle like the EA" -> not possible on TradingView historical bars
(answered); (2) an MT5 EA of the fractal grid strategy.
Design: core = the twin's per-bar model (pine_twin2.Strat) on M1 bars built from ticks (open = first tick of a minute; moves = later ticks),
TF candles from the broker (iTime/iHigh), pushed at the first tick of a new TF candle; virtual buy stop on bid -> market buy; broker SL/TP =
model levels; BE / salvage / trailing moved on every tick; per-strategy money (port of twin f_base/f_raw/f_crk/f_lad/mmOpen/mmBook);
booking with the real deal P&L (sim mode: model P&L); restart memory (global variables) + catch-up replay of M1 bars; warm-up replay per
strategy from its latest level's activation; hedging account required; magic = base + strategy number.
Files: build_ea.py (generator) -> FractalBreakoutGridEA.mq5
Steps: [ ] write  [ ] mq5check 0/0  [ ] harness parity vs twin2 on M1  [ ] money parity  [ ] restart test  [ ] review  [ ] docs/ship
- [x] write (build_ea.py + ea_rest.mq5 -> FractalBreakoutGridEA.mq5, 1394 lines)  [x] mq5check 0/0 (shim got the CopyRates(start, stop) overload)
- [x] harness (harness/build.py, driver.cpp, export.py, parity.py): defaults 5,551 trades identical to pine_twin2 on M1, $ risk 9e-13
- [ ] random option sets: parity.py seeds 11/12/13 x 8 sets (parity_seed*.txt)
- [x] restart test: defaults 55 restarts + 5 option sets x 70 restarts: identical
- [x] README section + CHECKPOINT item 35 drafted ({RANDOM} / {REVIEW} placeholders to fill)
- [ ] review agent (Sonnet high) running; random-set parity running (parity_seed11/12/13.txt)
