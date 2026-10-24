# EA review2 progress
- read RESULTS, diff, full EA: done
- compile pass: no errors found so far
- logic findings drafted: exSynced on caught-up fill, stale pending after caught-up resolve, gNewDay lost in catch-up, capStop reset, early-fill+opposite arm skip
- next: check Pine anchor/source/hours
- Pine anchor/src/hours checked: EA matches (newAnchor = chgD for Session; vwBars/sessN on anchor; hours a0<b0 wrap).
- compile: clean (enums between inputs OK, StructToTime/ZeroMemory/iBarShift sigs OK, no dup names).
- final findings: caught-up fill exSynced (blocker), stale pending after caught-up resolve (blocker), minD market fallback (major),
  arm on caught-up bar never placed (major), gNewDay lost (minor), capStop not reset (minor), early fill+new arm skipped (minor),
  utPrev across catch-up (minor), sh==1 guard (minor), SL inside stops at placement (minor), pDone on adoption (minor)
- status: DONE, reporting
