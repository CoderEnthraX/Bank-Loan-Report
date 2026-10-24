started; reading files
step: read all sources; analysing
step: engine parity reviewed (windows, vwHist, slope, ATR, half stop, ghost, loss block, moves, entry modes, filters) - parity OK except hours a0==b0, DST offset, VWAP anchor/source inputs missing
step: compile check - no errors found (CTrade signatures, StringFormat 21/21, OrderCalcMargin, HistoryDeal* OK)
step: execution - findings: reinit state (blocker), early fill orphan, SetExits rejection, stops level, skipped bars, restart pending, earn-back stop, partial min vol, warm-up bounds, INIT_FAILED text
DONE - reporting
