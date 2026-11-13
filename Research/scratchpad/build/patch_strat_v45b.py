"""Strategy v4.5b: the Loss Recovery tooltip's new lines kept short (the tooltip stays well under 4,096 characters); each Crooks E - J setting
keeps its own detailed tooltip. Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/strategy_template.pine'
s = open(P, encoding='utf8').read()
old = '''\\nCrooks E - J are Crooks C with one change each (every Crooks C setting also acts for them):\\nCrooks E: while a loss is owed, every trade that is not the recovery trade is 0.01 lot (Crooks E / I lot), or the normal size if that is smaller; the recovery trade after a win goes for the loss as in Crooks C, and if it loses the trades go back to 0.01 lot until the next win.\\nCrooks F: a recovery trade risks at most K x base (default 3); the rest of the loss is won back after the next wins.\\nCrooks G: the loss to win back is never more than X x base (default 10); the rest is accepted as lost.\\nCrooks H: a recovery trade risks at most this % of the equity (default 1%).\\nCrooks I: Crooks E with the Crooks F limit.\\nCrooks J: the deeper the closed-profit drawdown, the smaller the recovery trade: x (1 - drawdown / (X x base)), never below the base (default X 20).'''
new = '''\\nCrooks E - J = Crooks C with one change (all Crooks C settings apply):\\nE: while waiting for a win, 0.01 lot (or the normal size if smaller).\\nF: a recovery trade risks at most K x base.\\nG: the loss to win back is at most X x base; the rest is accepted.\\nH: a recovery trade risks at most a % of the equity.\\nI: E + the F limit.\\nJ: the recovery trade shrinks with the drawdown.'''
assert s.count(old) == 1
s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s); print('1 edit')
