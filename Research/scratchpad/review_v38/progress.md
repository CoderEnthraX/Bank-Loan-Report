# review v38 progress
- Read all diffs + full Pine strategy exit/engine/news code + EA TakeSetup/OnNewBar/ManagePartials/T1Half/NewsBlock.
- Checked: skip rules (3 impls consistent), kz shift arithmetic, UK/NY switch instants, Pine dnSh formula (zoneinfo test OK for IST/UTC/London/Tokyo/Sydney/NY), news wrap/start>=1440/start==end, dPre, T1 formula derivation, t1Bar (fill bar excluded, exMine/ghost guard, double-book guard), engine-exit close-all with any exit, partials/moves ignored for T1 trades.
- Result: no high/medium defects traced. Low notes only (labels for p!=50, rest-leg costs for small p, K45 tighter than tight for p>75, t1Bar only bar 1).
