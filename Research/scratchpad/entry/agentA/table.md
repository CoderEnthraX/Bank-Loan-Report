| # | family | setup (variant) | TF | n/mo (train, filled) | train L | train S | valid L | valid S | placebo-adj train L/S | placebo-adj valid L/S | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 ORB / Asian range | LonORB30 mkt 1.8ATR | M15 | 24.5 | -2.5 | -0.8 | -1.7 | -0.9 | -0.3 / -0.1 | -0.3 / +0.3 | FAIL |
| 2 | 1 ORB / Asian range | LonORB30 mkt stop=ORmid | M15 | 24.5 | -2.6 | -1.6 | -3.8 | -1.6 | -1.3 / -1.1 | +0.0 / -0.7 | FAIL |
| 3 | 1 ORB / Asian range | LonORB30 mkt stop=ORopp | M15 | 24.5 | -1.4 | +1.0 | -0.1 | -0.2 | +1.0 / -0.4 | +1.4 / +0.5 | FAIL |
| 4 | 1 ORB / Asian range | LonORB30 stopentry stop=ORmid | M15 | 29.3 | -0.9 | +1.6 | -4.6 | +4.1 | +0.9 / +1.3 | -1.6 / +1.7 | FAIL |
| 5 | 1 ORB / Asian range | LonORB30 stopentry 1.8ATR | M15 | 29.3 | -0.5 | +0.9 | +0.1 | +0.2 | +0.2 / -1.2 | -0.5 / +0.3 | FAIL |
| 6 | 1 ORB / Asian range | LonORB60 mkt 1.8ATR | M15 | 20.4 | -3.3 | -3.4 | -4.3 | +4.0 | -1.3 / -4.6 | -4.1 / +3.3 | FAIL |
| 7 | 1 ORB / Asian range | LonORB60 mkt stop=ORmid | M15 | 20.4 | -4.2 | -2.8 | -7.5 | +1.1 | -3.6 / -3.1 | -7.2 / +1.1 | FAIL |
| 8 | 1 ORB / Asian range | LonORB60 mkt stop=ORopp | M15 | 20.4 | -2.9 | -2.2 | -2.7 | +4.4 | -1.2 / -6.0 | -4.6 / +3.2 | FAIL |
| 9 | 1 ORB / Asian range | LonORB60 stopentry stop=ORmid | M15 | 24.6 | -0.7 | +1.1 | -6.3 | +2.8 | +1.3 / -1.5 | -7.0 / +3.1 | FAIL |
| 10 | 1 ORB / Asian range | LonORB60 stopentry 1.8ATR | M15 | 24.6 | -1.2 | +0.4 | -1.4 | +4.6 | +1.6 / -4.5 | -3.9 / +6.7 | FAIL |
| 11 | 1 ORB / Asian range | NYORB 0820-0850 mkt 1.8ATR | M15 | 23.7 | +2.0 | +2.6 | -1.5 | -2.1 | +3.1 / +1.6 | +1.9 / -2.4 | FAIL |
| 12 | 1 ORB / Asian range | NYORB 0820-0850 mkt stop=ORmid | M15 | 23.7 | +3.2 | +2.1 | -2.2 | -1.1 | +4.1 / +0.9 | +3.7 / -2.8 | FAIL |
| 13 | 1 ORB / Asian range | NYORB 0820-0850 mkt stop=ORopp | M15 | 23.7 | +3.9 | +3.7 | +1.0 | -2.2 | +3.9 / +2.7 | +2.8 / -0.1 | FAIL |
| 14 | 1 ORB / Asian range | NYORB 0820-0850 stopentry stop=ORmid | M15 | 28.8 | -2.4 | +0.8 | -2.7 | +3.5 | +0.8 / +4.8 | +2.1 / +3.3 | FAIL |
| 15 | 1 ORB / Asian range | NYORB 0820-0850 stopentry 1.8ATR | M15 | 28.8 | -0.3 | +4.0 | -2.9 | +3.3 | +0.4 / +2.8 | +0.7 / -0.6 | FAIL |
| 16 | 1 ORB / Asian range | NYORB 0930-1000 mkt 1.8ATR | M15 | 20.0 | +1.1 | +1.5 | +3.7 | -0.7 | +2.5 / -3.4 | +1.6 / +0.5 | FAIL |
| 17 | 1 ORB / Asian range | NYORB 0930-1000 mkt stop=ORmid | M15 | 20.0 | +2.8 | +0.6 | -0.2 | -0.6 | +5.9 / -4.0 | -1.2 / +0.2 | FAIL |
| 18 | 1 ORB / Asian range | NYORB 0930-1000 mkt stop=ORopp | M15 | 20.0 | +2.0 | +3.0 | +2.5 | -2.4 | +3.6 / -0.0 | -1.0 / +0.5 | FAIL |
| 19 | 1 ORB / Asian range | NYORB 0930-1000 stopentry stop=ORmid | M15 | 25.2 | +1.0 | +2.4 | -0.8 | +1.2 | +1.7 / +2.8 | +2.9 / -0.8 | FAIL |
| 20 | 1 ORB / Asian range | NYORB 0930-1000 stopentry 1.8ATR | M15 | 25.2 | +1.8 | +4.5 | +3.9 | +3.1 | +2.2 / +3.0 | +4.9 / +1.7 | all 4 > 0, pooled z 2.4 |
| 21 | 1 ORB / Asian range | NYORB 0930-1030 mkt 1.8ATR | M15 | 14.9 | -1.5 | -0.6 | +2.8 | -1.8 | +1.0 / -2.3 | +2.7 / +0.7 | FAIL |
| 22 | 1 ORB / Asian range | NYORB 0930-1030 mkt stop=ORmid | M15 | 14.9 | -1.1 | -3.1 | -0.3 | -1.6 | +1.7 / -4.9 | -0.9 / -0.6 | FAIL |
| 23 | 1 ORB / Asian range | NYORB 0930-1030 mkt stop=ORopp | M15 | 14.9 | +2.7 | +0.8 | -1.7 | -5.3 | +3.7 / +1.1 | -5.4 / +0.1 | FAIL |
| 24 | 1 ORB / Asian range | NYORB 0930-1030 stopentry stop=ORmid | M15 | 18.6 | +2.1 | +0.6 | +0.7 | +1.7 | +1.2 / -0.4 | +1.3 / +7.1 | all 4 > 0, z 0.8 (noise level) |
| 25 | 1 ORB / Asian range | NYORB 0930-1030 stopentry 1.8ATR | M15 | 18.6 | +1.4 | +1.4 | +3.6 | +3.4 | +0.1 / +1.1 | +3.4 / +10.2 | all 4 > 0, z 1.4 (noise level) |
| 26 | 1 ORB / Asian range | Asia brk@London mkt 1.8ATR | M15 | 14.0 | -6.9 | -2.8 | +1.9 | -0.3 | -6.7 / -3.7 | +1.8 / +1.3 | FAIL |
| 27 | 1 ORB / Asian range | Asia brk@London mkt stop=mid | M15 | 14.0 | -7.4 | +0.7 | +3.6 | -2.2 | -6.3 / -2.2 | +2.1 / -2.3 | FAIL |
| 28 | 1 ORB / Asian range | Asia sweep-fade@London mkt stop=ext | M15 | 14.1 | -1.9 | -6.8 | -5.1 | +2.2 | +0.6 / -6.1 | -5.1 / -0.9 | FAIL |
| 29 | 1 ORB / Asian range | Asia sweep-fade@London mkt 1.8ATR | M15 | 14.1 | +0.5 | -3.2 | -2.7 | -2.5 | +3.0 / -4.2 | -2.7 / -1.7 | FAIL |
| 30 | 1 ORB / Asian range | LonORB30 mkt 1.8ATR | M5 | 26.4 | -0.8 | +1.9 | -2.9 | +4.5 | +0.1 / +2.1 | -2.0 / +4.9 | FAIL |
| 31 | 1 ORB / Asian range | LonORB30 mkt stop=ORmid | M5 | 26.4 | -1.8 | +1.5 | -4.1 | +3.2 | -0.8 / +1.1 | -2.0 / +3.0 | FAIL |
| 32 | 1 ORB / Asian range | LonORB30 mkt stop=ORopp | M5 | 26.4 | -0.7 | +1.3 | +1.0 | +2.4 | -0.2 / -1.3 | +0.7 / +3.1 | FAIL |
| 33 | 1 ORB / Asian range | LonORB30 stopentry stop=ORmid | M5 | 29.6 | -1.1 | +1.2 | -3.0 | +4.4 | +0.6 / -0.0 | -0.3 / +1.1 | FAIL |
| 34 | 1 ORB / Asian range | LonORB30 stopentry 1.8ATR | M5 | 29.6 | -0.6 | +2.6 | -0.7 | +2.8 | +0.7 / +0.8 | +0.1 / +0.7 | FAIL |
| 35 | 1 ORB / Asian range | LonORB60 mkt 1.8ATR | M5 | 22.1 | -2.1 | -0.2 | -3.9 | +8.7 | -2.8 / -1.0 | -1.0 / +9.8 | FAIL |
| 36 | 1 ORB / Asian range | LonORB60 mkt stop=ORmid | M5 | 22.1 | -3.5 | -0.6 | -4.6 | +5.0 | -4.2 / -1.0 | -2.1 / +6.2 | FAIL |
| 37 | 1 ORB / Asian range | LonORB60 mkt stop=ORopp | M5 | 22.1 | -2.5 | -0.3 | +0.0 | +6.0 | -1.6 / -3.4 | -1.2 / +7.5 | FAIL |
| 38 | 1 ORB / Asian range | LonORB60 stopentry stop=ORmid | M5 | 24.8 | -0.6 | +1.8 | -5.2 | +1.6 | +1.5 / +1.3 | -5.6 / +0.0 | FAIL |
| 39 | 1 ORB / Asian range | LonORB60 stopentry 1.8ATR | M5 | 24.8 | -0.3 | +3.0 | -2.1 | +5.0 | +1.6 / +2.5 | -1.3 / +4.8 | FAIL |
| 40 | 1 ORB / Asian range | NYORB 0820-0850 mkt 1.8ATR | M5 | 25.8 | -0.2 | +0.5 | -2.1 | +1.8 | +1.7 / -2.4 | +1.1 / -1.6 | FAIL |
| 41 | 1 ORB / Asian range | NYORB 0820-0850 mkt stop=ORmid | M5 | 25.8 | -2.2 | -1.0 | -0.4 | +0.6 | -1.1 / -2.4 | +3.5 / -2.9 | FAIL |
| 42 | 1 ORB / Asian range | NYORB 0820-0850 mkt stop=ORopp | M5 | 25.8 | +1.6 | +3.3 | +1.3 | -0.3 | +1.5 / +1.7 | +5.2 / -0.9 | FAIL |
| 43 | 1 ORB / Asian range | NYORB 0820-0850 stopentry stop=ORmid | M5 | 28.8 | -3.4 | -0.3 | -0.3 | +2.8 | +0.6 / +0.5 | +1.9 / +0.2 | FAIL |
| 44 | 1 ORB / Asian range | NYORB 0820-0850 stopentry 1.8ATR | M5 | 28.8 | -1.2 | +1.0 | -1.8 | +5.6 | +3.2 / +1.5 | +0.5 / +0.5 | FAIL |
| 45 | 1 ORB / Asian range | NYORB 0930-1000 mkt 1.8ATR | M5 | 22.4 | +3.5 | -0.2 | -1.5 | -0.7 | +5.0 / -0.3 | -3.4 / -0.9 | FAIL |
| 46 | 1 ORB / Asian range | NYORB 0930-1000 mkt stop=ORmid | M5 | 22.4 | +3.6 | +0.3 | +0.8 | -0.9 | +4.9 / +1.1 | -3.2 / -0.8 | FAIL |
| 47 | 1 ORB / Asian range | NYORB 0930-1000 mkt stop=ORopp | M5 | 22.4 | +1.5 | +0.9 | +4.3 | -2.6 | +2.6 / -0.2 | +3.0 / +0.9 | FAIL |
| 48 | 1 ORB / Asian range | NYORB 0930-1000 stopentry stop=ORmid | M5 | 25.4 | +0.7 | +2.5 | +0.3 | +0.8 | +1.9 / +4.3 | +2.1 / +1.7 | all 4 > 0, z 0.9 (noise level) |
| 49 | 1 ORB / Asian range | NYORB 0930-1000 stopentry 1.8ATR | M5 | 25.4 | +2.0 | +3.2 | +1.0 | +3.2 | +1.8 / +4.2 | +1.3 / +2.8 | all 4 > 0, z 1.8 (noise level) |
| 50 | 1 ORB / Asian range | NYORB 0930-1030 mkt 1.8ATR | M5 | 16.7 | +1.3 | -3.0 | -2.8 | -1.2 | +2.0 / -3.8 | -5.6 / -0.8 | FAIL ; few trades |
| 51 | 1 ORB / Asian range | NYORB 0930-1030 mkt stop=ORmid | M5 | 16.7 | -0.2 | -3.0 | +2.5 | -1.7 | +0.5 / -5.2 | -0.0 / -1.1 | FAIL ; few trades |
| 52 | 1 ORB / Asian range | NYORB 0930-1030 mkt stop=ORopp | M5 | 16.7 | +2.0 | +0.5 | +1.2 | -5.4 | +1.8 / -1.6 | -5.7 / +0.2 | FAIL ; few trades |
| 53 | 1 ORB / Asian range | NYORB 0930-1030 stopentry stop=ORmid | M5 | 18.8 | +2.1 | +0.8 | +2.4 | +1.0 | +2.2 / -0.8 | +4.0 / +6.9 | all 4 > 0, z 1.0 (noise level) ; few trades |
| 54 | 1 ORB / Asian range | NYORB 0930-1030 stopentry 1.8ATR | M5 | 18.8 | +0.6 | +1.5 | +0.5 | +2.3 | +0.2 / +1.4 | +3.2 / +7.2 | all 4 > 0, z 0.7 (noise level) ; few trades |
| 55 | 1 ORB / Asian range | Asia brk@London mkt 1.8ATR | M5 | 15.3 | -4.7 | -3.8 | +3.8 | +7.2 | -1.5 / -5.3 | +4.0 / +4.1 | FAIL ; few trades |
| 56 | 1 ORB / Asian range | Asia brk@London mkt stop=mid | M5 | 15.3 | -4.5 | +0.9 | +5.4 | -0.9 | -0.3 / -1.7 | +4.7 / -2.9 | FAIL ; few trades |
| 57 | 1 ORB / Asian range | Asia sweep-fade@London mkt stop=ext | M5 | 14.9 | -3.0 | -1.5 | -3.1 | -4.0 | -2.3 / -0.3 | +0.9 / -7.3 | FAIL ; few trades |
| 58 | 1 ORB / Asian range | Asia sweep-fade@London mkt 1.8ATR | M5 | 14.9 | -2.3 | -2.1 | +0.6 | -3.9 | -0.5 / +0.2 | +2.4 / -3.6 | FAIL ; few trades |
| 59 | 2 Liquidity sweeps | PDH/PDL sweep any time mkt stop=ext | M15 | 18.5 | +2.2 | +0.4 | -1.0 | +1.8 | +2.8 / -0.7 | +2.3 / +1.1 | FAIL |
| 60 | 2 Liquidity sweeps | PDH/PDL sweep any time mkt 1.8ATR | M15 | 18.5 | +0.6 | -0.3 | -3.4 | -1.2 | +2.4 / -0.8 | +0.8 / -2.6 | FAIL |
| 61 | 2 Liquidity sweeps | PDH/PDL sweep any time stopentry(conf) stop=ext | M15 | 11.9 | +3.3 | +4.3 | +6.0 | +8.2 | +5.2 / +4.6 | +6.0 / +7.5 | all 4 > 0, pooled z 2.5 |
| 62 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 mkt stop=ext | M15 | 14.4 | +1.4 | +1.7 | +3.4 | +9.4 | +3.9 / -0.3 | +3.0 / +8.5 | all 4 > 0, z 1.7 (noise level) |
| 63 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 mkt 1.8ATR | M15 | 14.4 | -0.6 | -0.3 | -1.2 | +4.6 | +3.0 / -3.4 | -0.3 / +4.7 | FAIL |
| 64 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 stopentry(conf) stop=ext | M15 | 9.6 | +0.6 | +5.7 | +7.3 | +11.6 | +2.9 / +4.7 | +12.4 / +11.0 | all 4 > 0, pooled z 2.3 |
| 65 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 mkt stop=ext | M15 | 19.1 | +0.3 | -0.7 | -3.5 | +8.5 | +2.2 / -2.2 | +1.1 / +10.1 | FAIL |
| 66 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 mkt 1.8ATR | M15 | 19.1 | +0.3 | -0.2 | +0.6 | -0.4 | +2.3 / -1.9 | +4.2 / +2.1 | FAIL |
| 67 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 stopentry(conf) stop=ext | M15 | 10.6 | -1.3 | +3.8 | -2.5 | -4.9 | -0.0 / +4.0 | -1.0 / -5.0 | FAIL |
| 68 | 2 Liquidity sweeps | London range sweep in NY 08-12 mkt stop=ext | M15 | 22.1 | -0.8 | -1.5 | -2.0 | +4.0 | +1.2 / -2.7 | +1.7 / +2.0 | FAIL |
| 69 | 2 Liquidity sweeps | London range sweep in NY 08-12 mkt 1.8ATR | M15 | 22.1 | -1.8 | -0.1 | -3.3 | +1.9 | +1.7 / -2.9 | +1.3 / +0.1 | FAIL |
| 70 | 2 Liquidity sweeps | London range sweep in NY 08-12 stopentry(conf) stop=ext | M15 | 14.9 | -1.4 | +0.4 | +0.9 | -0.6 | +0.2 / -3.3 | +2.1 / -1.4 | FAIL |
| 71 | 2 Liquidity sweeps | PDH/PDL sweep any time mkt stop=ext | M5 | 19.2 | +2.3 | +0.8 | +2.2 | -5.0 | +1.8 / +0.6 | +4.6 / -5.7 | FAIL ; few trades |
| 72 | 2 Liquidity sweeps | PDH/PDL sweep any time mkt 1.8ATR | M5 | 19.2 | +3.9 | +1.1 | +2.2 | -3.0 | +3.8 / +1.0 | +4.0 / -3.6 | FAIL ; few trades |
| 73 | 2 Liquidity sweeps | PDH/PDL sweep any time stopentry(conf) stop=ext | M5 | 12.6 | +4.5 | +3.5 | +5.6 | -1.0 | +1.9 / +0.0 | +5.5 / -3.7 | FAIL ; few trades |
| 74 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 mkt stop=ext | M5 | 15.1 | +2.3 | +5.0 | +3.3 | +2.1 | +1.2 / +6.7 | +5.5 / -1.6 | all 4 > 0, z 1.9 (noise level) ; few trades |
| 75 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 mkt 1.8ATR | M5 | 15.1 | +4.0 | +2.1 | +5.5 | +3.3 | +1.4 / +1.5 | +2.9 / -1.9 | all 4 > 0, z 1.9 (noise level) ; few trades |
| 76 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 stopentry(conf) stop=ext | M5 | 10.4 | +4.3 | +3.0 | +8.6 | +4.1 | +3.0 / +3.2 | +2.3 / -0.7 | all 4 > 0, pooled z 2.0 ; few trades |
| 77 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 mkt stop=ext | M5 | 17.4 | -0.0 | -1.4 | -2.0 | +7.2 | +0.9 / -0.4 | -0.3 / +8.3 | FAIL ; few trades |
| 78 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 mkt 1.8ATR | M5 | 17.4 | +1.2 | -1.8 | -2.9 | +2.9 | +3.4 / -1.9 | -1.9 / +1.2 | FAIL ; few trades |
| 79 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 stopentry(conf) stop=ext | M5 | 9.6 | -1.5 | -2.3 | +0.1 | +7.3 | -2.8 / -2.3 | -1.7 / +5.0 | FAIL ; few trades |
| 80 | 2 Liquidity sweeps | London range sweep in NY 08-12 mkt stop=ext | M5 | 23.6 | -1.1 | -1.1 | -7.3 | +2.9 | +2.9 / -1.3 | -3.8 / +0.5 | FAIL |
| 81 | 2 Liquidity sweeps | London range sweep in NY 08-12 mkt 1.8ATR | M5 | 23.6 | -2.4 | -0.3 | -5.2 | +0.4 | +1.3 / -1.9 | -0.8 / -2.3 | FAIL |
| 82 | 2 Liquidity sweeps | London range sweep in NY 08-12 stopentry(conf) stop=ext | M5 | 15.7 | -0.6 | +1.8 | -3.5 | +3.6 | +1.4 / +0.3 | +0.6 / +0.3 | FAIL ; few trades |
| 83 | 3 VWAP | VWAP reclaim after 3 bars 1.8ATR | M15 | 97.8 | +1.1 | +1.8 | -0.7 | +3.2 | +2.1 / +1.3 | +0.9 / +3.1 | FAIL |
| 84 | 3 VWAP | VWAP reclaim after 3 bars stop=swing | M15 | 97.8 | +0.4 | +1.0 | -1.6 | +2.0 | +1.4 / +1.3 | -0.2 / +1.7 | FAIL |
| 85 | 3 VWAP | VWAP reject after 3 bars 1.8ATR | M15 | 71.2 | -0.8 | +0.8 | -1.4 | +0.9 | -0.2 / +1.0 | -1.0 / -0.3 | FAIL |
| 86 | 3 VWAP | VWAP reject after 3 bars stop=ext | M15 | 71.2 | +0.4 | +1.5 | -5.1 | +0.4 | +1.1 / +1.6 | -2.2 / -1.8 | FAIL |
| 87 | 3 VWAP | VWAP reclaim after 6 bars 1.8ATR | M15 | 61.0 | +1.8 | +1.5 | -2.6 | +2.3 | +3.7 / +1.5 | -2.6 / +1.5 | FAIL |
| 88 | 3 VWAP | VWAP reclaim after 6 bars stop=swing | M15 | 61.0 | +1.7 | +0.5 | -3.9 | -0.5 | +2.9 / +0.5 | -3.2 / -0.9 | FAIL |
| 89 | 3 VWAP | VWAP reject after 6 bars 1.8ATR | M15 | 45.4 | +0.1 | +1.1 | -0.5 | +1.7 | +0.6 / +1.3 | -0.4 / -1.1 | FAIL |
| 90 | 3 VWAP | VWAP reject after 6 bars stop=ext | M15 | 45.4 | +2.3 | +3.0 | -3.0 | +2.9 | +3.5 / +4.5 | -1.1 / +0.2 | FAIL |
| 91 | 3 VWAP | VWAP pullback slope>0.5ATR/2h 1.8ATR | M15 | 17.1 | +1.7 | -0.0 | +3.9 | -4.1 | +3.2 / +1.8 | +4.9 / -4.2 | FAIL |
| 92 | 3 VWAP | VWAP pullback slope>0.5ATR/2h stop=swing | M15 | 17.1 | +2.4 | +6.8 | -4.1 | -0.9 | +3.5 / +10.1 | -2.7 / -3.4 | FAIL |
| 93 | 3 VWAP | VWAP 1sig pullback slope>0.5 1.8ATR | M15 | 38.9 | -1.5 | +0.5 | +0.4 | +1.4 | -0.7 / +0.3 | -0.1 / +1.2 | FAIL |
| 94 | 3 VWAP | VWAP 1sig pullback slope>0.5 stop=swing | M15 | 38.9 | -0.2 | +0.1 | -1.3 | -1.0 | -0.3 / +0.6 | +0.8 / -3.8 | FAIL |
| 95 | 3 VWAP | VWAP pullback slope>1.0ATR/2h 1.8ATR | M15 | 5.3 | +0.1 | -2.4 | +4.0 | -2.7 | -0.8 / -4.2 | +7.3 / -6.6 | FAIL ; few trades |
| 96 | 3 VWAP | VWAP pullback slope>1.0ATR/2h stop=swing | M15 | 5.3 | -1.1 | +5.1 | +6.6 | +1.1 | +0.5 / +4.0 | +14.3 / -1.0 | FAIL ; few trades |
| 97 | 3 VWAP | VWAP 1sig pullback slope>1.0 1.8ATR | M15 | 11.3 | +0.5 | +2.5 | -0.9 | +8.8 | -0.2 / +2.6 | -0.8 / +8.4 | FAIL |
| 98 | 3 VWAP | VWAP 1sig pullback slope>1.0 stop=swing | M15 | 11.3 | -0.3 | +3.1 | +1.9 | +4.6 | -1.4 / +2.7 | +5.5 / +2.7 | FAIL |
| 99 | 3 VWAP | VWAP 2.0sig fade (first close beyond) 1.8ATR | M15 | 81.0 | +0.5 | +1.0 | -3.8 | -1.6 | +1.6 / -0.2 | -1.7 / -1.6 | FAIL |
| 100 | 3 VWAP | VWAP 2.0sig fade (first close beyond) 3ATR | M15 | 81.0 | +0.4 | +0.8 | -1.9 | -1.6 | +1.2 / -1.3 | -1.7 / -0.8 | FAIL |
| 101 | 3 VWAP | VWAP 2.0sig fade (close back inside) 1.8ATR | M15 | 86.4 | -1.1 | -0.3 | -0.8 | -0.3 | +0.1 / -1.1 | -2.3 / -1.3 | FAIL |
| 102 | 3 VWAP | VWAP 2.5sig fade (first close beyond) 1.8ATR | M15 | 42.3 | +1.0 | +1.5 | -2.7 | -2.4 | +1.8 / +2.0 | -0.7 / -3.0 | FAIL |
| 103 | 3 VWAP | VWAP 2.5sig fade (first close beyond) 3ATR | M15 | 42.3 | +0.1 | +1.8 | -0.7 | -0.8 | +1.3 / +1.7 | -0.9 / -0.5 | FAIL |
| 104 | 3 VWAP | VWAP 2.5sig fade (close back inside) 1.8ATR | M15 | 45.5 | -0.7 | +0.9 | -1.5 | -0.1 | -0.0 / -0.9 | -1.9 / -2.0 | FAIL |
| 105 | 3 VWAP | VWAP reclaim after 6 bars 1.8ATR | M5 | 112.5 | -1.0 | +1.5 | +0.1 | +1.4 | -0.9 / +0.8 | +1.6 / +1.3 | FAIL |
| 106 | 3 VWAP | VWAP reclaim after 6 bars stop=swing | M5 | 112.5 | -0.7 | +2.0 | -2.0 | +1.2 | +0.1 / +1.9 | -0.9 / +0.5 | FAIL |
| 107 | 3 VWAP | VWAP reject after 6 bars 1.8ATR | M5 | 70.4 | -0.2 | +0.8 | -3.5 | +2.0 | +0.6 / +1.7 | -3.2 / +1.1 | FAIL |
| 108 | 3 VWAP | VWAP reject after 6 bars stop=ext | M5 | 70.4 | +2.6 | +2.4 | -6.3 | +3.0 | +4.9 / +3.7 | -2.2 / +1.8 | FAIL |
| 109 | 3 VWAP | VWAP reclaim after 12 bars 1.8ATR | M5 | 78.2 | -0.6 | -0.1 | +0.6 | +1.4 | -2.1 / -1.4 | +1.0 / +1.8 | FAIL |
| 110 | 3 VWAP | VWAP reclaim after 12 bars stop=swing | M5 | 78.2 | +0.3 | +1.3 | -2.5 | +0.5 | +0.1 / +0.3 | -2.3 / +2.2 | FAIL |
| 111 | 3 VWAP | VWAP reject after 12 bars 1.8ATR | M5 | 47.6 | +0.3 | +0.9 | -1.5 | -0.7 | +1.0 / -0.3 | -2.1 / -1.5 | FAIL |
| 112 | 3 VWAP | VWAP reject after 12 bars stop=ext | M5 | 47.6 | +3.1 | +2.4 | -7.1 | +1.8 | +4.5 / +3.8 | -4.9 / +1.2 | FAIL |
| 113 | 3 VWAP | VWAP pullback slope>0.5ATR/2h 1.8ATR | M5 | 35.7 | +1.9 | +2.6 | -3.2 | +2.0 | +4.1 / +3.3 | -2.8 / +1.9 | FAIL |
| 114 | 3 VWAP | VWAP pullback slope>0.5ATR/2h stop=swing | M5 | 35.7 | +6.3 | +2.4 | -7.0 | +1.0 | +8.2 / +4.0 | -5.1 / -0.4 | FAIL |
| 115 | 3 VWAP | VWAP 1sig pullback slope>0.5 1.8ATR | M5 | 69.8 | +1.3 | +0.6 | -1.1 | +0.0 | +2.6 / -0.1 | -0.8 / -2.0 | FAIL |
| 116 | 3 VWAP | VWAP 1sig pullback slope>0.5 stop=swing | M5 | 69.8 | +0.7 | +1.3 | -0.9 | -0.1 | +1.6 / +1.2 | +1.4 / -3.0 | FAIL |
| 117 | 3 VWAP | VWAP pullback slope>1.0ATR/2h 1.8ATR | M5 | 15.6 | +4.7 | +3.3 | -1.4 | +2.2 | +5.7 / +3.9 | +2.4 / +4.4 | FAIL ; few trades |
| 118 | 3 VWAP | VWAP pullback slope>1.0ATR/2h stop=swing | M5 | 15.6 | +8.9 | +3.4 | -5.4 | +1.2 | +9.9 / +6.0 | +1.1 / +2.5 | FAIL ; few trades |
| 119 | 3 VWAP | VWAP 1sig pullback slope>1.0 1.8ATR | M5 | 35.6 | +0.9 | +2.5 | -2.1 | +1.9 | +1.9 / +2.0 | -1.9 / -0.0 | FAIL |
| 120 | 3 VWAP | VWAP 1sig pullback slope>1.0 stop=swing | M5 | 35.6 | +0.5 | +2.8 | -0.1 | +1.2 | +1.9 / +4.0 | +1.4 / -0.2 | FAIL |
| 121 | 3 VWAP | VWAP 2.0sig fade (first close beyond) 1.8ATR | M5 | 115.8 | +1.2 | +0.4 | -2.6 | -0.5 | +0.9 / -1.0 | -0.3 / -1.8 | FAIL |
| 122 | 3 VWAP | VWAP 2.0sig fade (first close beyond) 3ATR | M5 | 115.8 | +0.4 | +0.6 | -1.3 | -1.1 | +0.7 / -1.2 | -0.5 / -1.4 | FAIL |
| 123 | 3 VWAP | VWAP 2.0sig fade (close back inside) 1.8ATR | M5 | 116.1 | -1.3 | -0.5 | -0.3 | +0.6 | -1.4 / -2.0 | +0.1 / -0.3 | FAIL |
| 124 | 3 VWAP | VWAP 2.5sig fade (first close beyond) 1.8ATR | M5 | 66.2 | +2.8 | -0.4 | -3.0 | -1.7 | +2.6 / -0.8 | -2.3 / -3.9 | FAIL |
| 125 | 3 VWAP | VWAP 2.5sig fade (first close beyond) 3ATR | M5 | 66.2 | +1.6 | +0.3 | -1.7 | -2.0 | +3.2 / -0.2 | -1.0 / -4.5 | FAIL |
| 126 | 3 VWAP | VWAP 2.5sig fade (close back inside) 1.8ATR | M5 | 66.6 | +0.2 | +0.3 | -1.2 | -0.3 | +1.1 / +1.0 | -0.7 / -2.0 | FAIL |
| 127 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR continue 1.8ATR | M15 | 14.9 | -3.9 | +3.6 | -8.9 | +4.9 | +0.1 / -1.1 | -2.0 / -3.1 | FAIL |
| 128 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR continue stop=mid | M15 | 14.9 | -0.3 | -3.9 | -9.6 | -1.1 | +4.2 / -3.4 | -2.6 / -4.1 | FAIL |
| 129 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR fade 1.8ATR | M15 | 14.9 | -0.8 | +3.6 | -3.2 | +9.1 | +2.1 / -1.0 | +4.7 / +3.6 | FAIL |
| 130 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR fade stop=ext | M15 | 14.9 | +3.2 | +2.5 | -1.1 | +11.7 | +7.0 / +2.2 | +4.4 / +6.5 | FAIL |
| 131 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR continue 1.8ATR | M15 | 7.1 | -1.1 | +3.8 | -3.8 | -0.0 | +2.5 / +0.5 | +0.3 / -5.6 | FAIL ; few trades |
| 132 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR continue stop=mid | M15 | 7.1 | +2.5 | -2.7 | -8.4 | -1.5 | +5.7 / +0.3 | -3.1 / -4.0 | FAIL ; few trades |
| 133 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR fade 1.8ATR | M15 | 7.1 | -1.1 | -0.3 | +3.9 | +9.7 | +1.3 / -4.8 | +7.4 / +6.4 | FAIL ; few trades |
| 134 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR fade stop=ext | M15 | 7.1 | +3.2 | -0.5 | +0.0 | +11.3 | +6.7 / -0.8 | +2.7 / +10.6 | FAIL ; few trades |
| 135 | 4 Data bars / momentum / TOD | 0830 bar>1.5 break hi/lo stopentry 1.8ATR | M15 | 19.8 | -1.3 | +4.4 | -7.0 | +5.8 | +0.1 / +3.3 | -2.0 / +4.3 | FAIL |
| 136 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR continue 1.8ATR | M15 | 10.3 | +2.5 | -1.3 | +3.3 | +1.4 | +3.3 / -4.1 | +2.0 / +5.2 | FAIL |
| 137 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR continue stop=mid | M15 | 10.3 | +1.7 | +0.4 | +3.1 | +3.3 | +5.0 / -0.5 | +4.1 / -0.3 | all 4 > 0, z 0.9 (noise level) |
| 138 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR fade 1.8ATR | M15 | 10.3 | +0.4 | -3.1 | -1.0 | -2.2 | +2.5 / -5.5 | -3.5 / +2.8 | FAIL |
| 139 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR fade stop=ext | M15 | 10.3 | +1.2 | -1.1 | -4.3 | -2.7 | +2.5 / -4.7 | -1.0 / -3.0 | FAIL |
| 140 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR continue 1.8ATR | M15 | 2.7 | +9.8 | +2.0 | +14.5 | +4.9 | +4.7 / +1.4 | +12.3 / +0.8 | all 4 > 0, z 1.8 (noise level) ; few trades |
| 141 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR continue stop=mid | M15 | 2.7 | +15.8 | +7.9 | +8.5 | +10.6 | +17.7 / +6.9 | +9.0 / +0.8 | all 4 > 0, pooled z 2.7 ; few trades |
| 142 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR fade 1.8ATR | M15 | 2.7 | -7.9 | -6.9 | +5.2 | -12.8 | -8.3 / -5.8 | +10.6 / -7.0 | FAIL ; few trades |
| 143 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR fade stop=ext | M15 | 2.7 | -3.1 | -5.4 | -15.2 | -12.8 | -1.2 / -6.0 | -10.2 / -8.3 | FAIL ; few trades |
| 144 | 4 Data bars / momentum / TOD | 1000 bar>1.5 break hi/lo stopentry 1.8ATR | M15 | 11.7 | -1.4 | +2.6 | -3.9 | +3.5 | -0.7 / -3.0 | -2.0 / +8.0 | FAIL |
| 145 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>0ATR with 1.8ATR | M15 | 21.4 | +0.7 | +1.8 | +0.1 | +2.4 | +2.8 / +2.9 | +7.9 / +2.4 | all 4 > 0, z 0.9 (noise level) |
| 146 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>0ATR with 4ATR | M15 | 21.4 | +0.9 | +2.9 | +1.1 | -4.6 | +1.3 / +4.2 | +1.6 / -0.7 | FAIL |
| 147 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>2ATR with 1.8ATR | M15 | 2.9 | +0.9 | -5.6 | -7.8 | -2.8 | -1.9 / -6.2 | -5.4 / -1.9 | FAIL ; few trades |
| 148 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>2ATR with 4ATR | M15 | 2.9 | -5.3 | -1.0 | +4.0 | -9.5 | -8.8 / -1.1 | +17.2 / -0.6 | FAIL ; few trades |
| 149 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>0ATR with 1.8ATR | M15 | 21.4 | -1.8 | +1.3 | +2.3 | -0.7 | -0.3 / -1.4 | +1.9 / +2.0 | FAIL |
| 150 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>0ATR with 4ATR | M15 | 21.4 | -1.2 | +3.6 | -1.2 | -1.0 | +0.3 / -0.5 | -3.1 / +0.6 | FAIL |
| 151 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>2ATR with 1.8ATR | M15 | 3.8 | -1.7 | -2.5 | +2.7 | -10.9 | -4.4 / -4.8 | +3.9 / -6.6 | FAIL ; few trades |
| 152 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>2ATR with 4ATR | M15 | 3.8 | -8.1 | -6.8 | +1.9 | -6.6 | -9.2 / -8.3 | +3.4 / -6.3 | FAIL ; few trades |
| 153 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>0ATR with 1.8ATR | M15 | 20.8 | +1.9 | -0.5 | +4.8 | -8.2 | -0.5 / +1.3 | -3.7 / -5.6 | FAIL |
| 154 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>0ATR with 4ATR | M15 | 20.8 | +0.7 | -1.4 | +3.7 | -6.8 | -2.6 / -0.4 | -1.7 / -4.0 | FAIL |
| 155 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>2ATR with 1.8ATR | M15 | 14.7 | +0.4 | -0.8 | +7.0 | -10.3 | -0.2 / +3.3 | +2.7 / -8.8 | FAIL |
| 156 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>2ATR with 4ATR | M15 | 14.7 | +0.9 | -1.5 | +5.5 | -7.0 | -1.1 / -0.2 | +1.7 / -1.8 | FAIL |
| 157 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>0ATR with 1.8ATR | M15 | 21.4 | -1.1 | +2.5 | +4.4 | -3.5 | +0.6 / -1.3 | +3.6 / +1.7 | FAIL |
| 158 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>0ATR with 4ATR | M15 | 21.4 | +3.1 | -0.1 | +8.3 | -8.3 | +3.0 / -0.8 | +2.3 / -0.3 | FAIL |
| 159 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>2ATR with 1.8ATR | M15 | 12.6 | -2.4 | +1.7 | +4.8 | -8.3 | +2.5 / -1.0 | +5.9 / -4.9 | FAIL |
| 160 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>2ATR with 4ATR | M15 | 12.6 | +2.8 | -0.3 | +7.5 | -9.7 | +3.1 / +0.6 | +2.4 / -3.5 | FAIL |
| 161 | 4 Data bars / momentum / TOD | TOD long 14:00 NY 1.8ATR | M15 | 21.0 | +0.6 |  | +6.5 |  | -1.5 /  | +0.4 /  | one-direction TOD reference |
| 162 | 4 Data bars / momentum / TOD | TOD long 15:00 NY 1.8ATR | M15 | 20.8 | +2.3 |  | +7.7 |  | -0.6 /  | -1.9 /  | one-direction TOD reference |
| 163 | 4 Data bars / momentum / TOD | TOD short 07:00 NY 1.8ATR | M15 | 21.4 |  | +0.2 |  | +5.9 |  / -0.2 |  / +1.2 | one-direction TOD reference |
| 164 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR continue 1.8ATR | M5 | 14.4 | -2.5 | +0.3 | -1.6 | -1.5 | +4.2 / -0.8 | +4.7 / -4.7 | FAIL ; few trades |
| 165 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR continue stop=mid | M5 | 14.4 | -3.1 | -0.3 | -8.4 | -1.0 | +1.2 / -0.3 | -0.6 / -1.0 | FAIL ; few trades |
| 166 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR fade 1.8ATR | M5 | 14.4 | +0.1 | +3.9 | -4.2 | +4.3 | +2.7 / -0.9 | +0.8 / -1.3 | FAIL ; few trades |
| 167 | 4 Data bars / momentum / TOD | 0830 bar >1.5ATR fade stop=ext | M5 | 14.4 | -2.8 | -0.7 | -5.1 | -0.9 | +1.6 / -0.4 | +0.2 / -3.0 | FAIL ; few trades |
| 168 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR continue 1.8ATR | M5 | 7.1 | -2.8 | -1.0 | -1.4 | -2.3 | +2.7 / -4.5 | +2.1 / -6.1 | FAIL ; few trades |
| 169 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR continue stop=mid | M5 | 7.1 | -4.6 | +1.6 | -2.6 | -0.1 | +3.5 / +2.4 | +3.8 / -1.9 | FAIL ; few trades |
| 170 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR fade 1.8ATR | M5 | 7.1 | +1.1 | +0.9 | -2.4 | +1.2 | +6.1 / -2.8 | +0.9 / -4.6 | FAIL ; few trades |
| 171 | 4 Data bars / momentum / TOD | 0830 bar >2.5ATR fade stop=ext | M5 | 7.1 | -2.7 | +1.1 | -2.4 | -10.5 | +0.5 / -3.5 | +3.4 / -12.4 | FAIL ; few trades |
| 172 | 4 Data bars / momentum / TOD | 0830 bar>1.5 break hi/lo stopentry 1.8ATR | M5 | 21.4 | +0.5 | +2.1 | -3.7 | +3.5 | +7.3 / +2.7 | +5.4 / +0.3 | FAIL |
| 173 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR continue 1.8ATR | M5 | 7.6 | +0.7 | +1.6 | -1.1 | +4.1 | +0.7 / +1.1 | -3.8 / +4.3 | FAIL ; few trades |
| 174 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR continue stop=mid | M5 | 7.6 | +0.1 | -0.1 | -0.6 | -0.2 | +3.4 / +0.8 | +2.4 / -1.4 | FAIL ; few trades |
| 175 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR fade 1.8ATR | M5 | 7.6 | -1.6 | -0.9 | -0.5 | +1.4 | -1.0 / -0.8 | +0.1 / +3.5 | FAIL ; few trades |
| 176 | 4 Data bars / momentum / TOD | 1000 bar >1.5ATR fade stop=ext | M5 | 7.6 | -2.1 | -3.1 | -4.5 | -2.0 | -2.1 / -4.3 | -2.0 / +1.3 | FAIL ; few trades |
| 177 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR continue 1.8ATR | M5 | 2.2 | +3.1 | +2.3 | -3.3 | +4.6 | -6.8 / +2.3 | -4.8 / +6.8 | FAIL ; few trades |
| 178 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR continue stop=mid | M5 | 2.2 | +0.5 | +10.4 | -7.2 | +6.4 | -7.0 / +11.5 | -4.0 / +2.2 | FAIL ; few trades |
| 179 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR fade 1.8ATR | M5 | 2.2 | +1.9 | -7.0 | +0.6 | +10.4 | +2.9 / -0.2 | -0.3 / +9.7 | FAIL ; few trades |
| 180 | 4 Data bars / momentum / TOD | 1000 bar >2.5ATR fade stop=ext | M5 | 2.2 | -1.9 | -5.7 | -5.8 | -2.8 | +5.2 / -3.5 | -2.5 / +8.8 | FAIL ; few trades |
| 181 | 4 Data bars / momentum / TOD | 1000 bar>1.5 break hi/lo stopentry 1.8ATR | M5 | 10.1 | -1.0 | +4.8 | -1.5 | +5.3 | +0.2 / +3.1 | -1.8 / +4.6 | FAIL ; few trades |
| 182 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>0ATR with 1.8ATR | M5 | 21.4 | +0.5 | +2.2 | +2.5 | +3.7 | +0.5 / +1.0 | +3.4 / -1.2 | all 4 > 0, z 1.3 (noise level) |
| 183 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>0ATR with 4ATR | M5 | 21.4 | +0.2 | +1.3 | -1.0 | -0.4 | +1.8 / +0.7 | -1.8 / -1.4 | FAIL |
| 184 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>2ATR with 1.8ATR | M5 | 5.6 | +4.0 | -3.0 | -6.2 | -0.3 | +6.6 / -0.7 | -4.4 / -4.2 | FAIL ; few trades |
| 185 | 4 Data bars / momentum / TOD | mom NY 09:30-10:00 |r|>2ATR with 4ATR | M5 | 5.6 | +1.5 | +0.5 | -7.7 | -7.6 | +5.2 / -1.0 | -3.9 / -7.8 | FAIL ; few trades |
| 186 | 4 Data bars / momentum / TOD | mom COMEX 08:20-09:20 |r|>0ATR with 1.8ATR | M5 | 21.4 | -0.7 | +3.3 | -1.7 | +9.7 | -1.2 / +1.4 | +0.6 / +6.8 | FAIL |
| 187 | 4 Data bars / momentum / TOD | mom COMEX 08:20-09:20 |r|>0ATR with 4ATR | M5 | 21.4 | +0.6 | +2.7 | -2.9 | +2.7 | +0.3 / +0.0 | -2.9 / +5.2 | FAIL |
| 188 | 4 Data bars / momentum / TOD | mom COMEX 08:20-09:20 |r|>2ATR with 1.8ATR | M5 | 9.5 | +3.5 | +0.4 | -4.8 | +5.8 | +3.0 / -1.1 | -3.1 / +0.2 | FAIL ; few trades |
| 189 | 4 Data bars / momentum / TOD | mom COMEX 08:20-09:20 |r|>2ATR with 4ATR | M5 | 9.5 | +2.6 | +0.6 | -6.7 | +1.8 | +3.8 / -1.6 | -8.6 / -0.4 | FAIL ; few trades |
| 190 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>0ATR with 1.8ATR | M5 | 21.4 | -1.8 | +3.4 | +0.9 | +1.7 | -0.3 / +2.2 | +0.8 / +2.0 | FAIL |
| 191 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>0ATR with 4ATR | M5 | 21.4 | -1.6 | +2.3 | +2.4 | -2.5 | +2.4 / +1.9 | +0.6 / +3.5 | FAIL |
| 192 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>2ATR with 1.8ATR | M5 | 8.3 | -2.3 | +1.6 | +2.5 | -1.1 | +1.0 / +0.7 | +0.1 / -5.6 | FAIL ; few trades |
| 193 | 4 Data bars / momentum / TOD | mom London 1st hour |r|>2ATR with 4ATR | M5 | 8.3 | -4.9 | +3.5 | -0.3 | -7.4 | -3.3 / +1.0 | -3.7 / -8.9 | FAIL ; few trades |
| 194 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>0ATR with 1.8ATR | M5 | 20.8 | -0.9 | +3.5 | +0.8 | -5.2 | -2.0 / +6.3 | -1.5 / -3.7 | FAIL |
| 195 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>0ATR with 4ATR | M5 | 20.8 | +1.8 | -1.3 | +5.2 | -10.6 | -1.5 / -0.6 | -2.3 / -6.8 | FAIL |
| 196 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>2ATR with 1.8ATR | M5 | 17.9 | -2.4 | +3.8 | +1.9 | -8.2 | -2.4 / +7.2 | -0.1 / -6.9 | FAIL ; few trades |
| 197 | 4 Data bars / momentum / TOD | mom session to 15:00 |r|>2ATR with 4ATR | M5 | 17.9 | +1.2 | -2.5 | +6.1 | -11.4 | +0.6 / +1.7 | -0.3 / -3.2 | FAIL ; few trades |
| 198 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>0ATR with 1.8ATR | M5 | 21.4 | +0.3 | +0.4 | +2.5 | -2.5 | +1.4 / -3.5 | +0.8 / -1.5 | FAIL |
| 199 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>0ATR with 4ATR | M5 | 21.4 | +0.8 | +0.9 | +7.3 | -5.3 | +0.9 / -2.1 | -0.1 / +0.6 | FAIL |
| 200 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>2ATR with 1.8ATR | M5 | 16.0 | -0.7 | -1.9 | +3.7 | -4.6 | +3.0 / -2.5 | +6.1 / -3.1 | FAIL ; few trades |
| 201 | 4 Data bars / momentum / TOD | mom session to 12:00 |r|>2ATR with 4ATR | M5 | 16.0 | -1.3 | -0.8 | +8.8 | -7.5 | +2.8 / +0.2 | +3.4 / +0.0 | FAIL ; few trades |
| 202 | 4 Data bars / momentum / TOD | TOD long 14:00 NY 1.8ATR | M5 | 21.0 | -2.0 |  | +4.6 |  | -3.4 /  | +2.6 /  | one-direction TOD reference |
| 203 | 4 Data bars / momentum / TOD | TOD long 15:00 NY 1.8ATR | M5 | 20.8 | +0.8 |  | +4.9 |  | -0.3 /  | -3.0 /  | one-direction TOD reference |
| 204 | 4 Data bars / momentum / TOD | TOD short 07:00 NY 1.8ATR | M5 | 21.5 |  | -0.3 |  | +4.8 |  / +0.2 |  / +1.3 | one-direction TOD reference |
| 205 | 5 Mean reversion / NR7 / gaps / round numbers | 4 bars one way -> fade 1.8ATR | M15 | 111.1 | -0.2 | +0.9 | +1.1 | -1.1 | -1.0 / -0.2 | +0.6 / -1.7 | FAIL |
| 206 | 5 Mean reversion / NR7 / gaps / round numbers | 4 bars one way -> continue 1.8ATR | M15 | 111.1 | -0.5 | +0.1 | +1.7 | +0.2 | -0.1 / +0.1 | +2.4 / +0.1 | FAIL |
| 207 | 5 Mean reversion / NR7 / gaps / round numbers | 6 bars one way -> fade 1.8ATR | M15 | 25.7 | +1.9 | -2.0 | -2.5 | +0.5 | +2.8 / -0.1 | -1.8 / +1.5 | FAIL |
| 208 | 5 Mean reversion / NR7 / gaps / round numbers | 6 bars one way -> continue 1.8ATR | M15 | 25.7 | +2.5 | -0.6 | +1.3 | +3.1 | +0.9 / -1.4 | -0.9 / +2.6 | FAIL |
| 209 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>4ATR fade 1.8ATR | M15 | 25.2 | +0.5 | -0.3 | +1.2 | -0.0 | +2.1 / +1.0 | +0.9 / +0.1 | FAIL |
| 210 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>4ATR fade 3ATR | M15 | 25.2 | +0.9 | +3.1 | +1.5 | -0.2 | +1.6 / +3.8 | +1.5 / +1.1 | FAIL |
| 211 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>6ATR fade 1.8ATR | M15 | 6.6 | +4.0 | +5.3 | -6.7 | -4.3 | +2.3 / +6.5 | -7.5 / -1.2 | FAIL ; few trades |
| 212 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>6ATR fade 3ATR | M15 | 6.6 | +4.5 | +2.3 | -9.3 | -1.2 | +2.7 / +2.5 | -8.0 / -0.5 | FAIL ; few trades |
| 213 | 5 Mean reversion / NR7 / gaps / round numbers | z>3sig fade 1.8ATR | M15 | 19.5 | +0.7 | +0.0 | -4.0 | -2.8 | +0.6 / -3.8 | +0.4 / -3.3 | FAIL |
| 214 | 5 Mean reversion / NR7 / gaps / round numbers | NR7 breakout stop=other side | M15 | 471.3 | +0.2 | +0.8 | -0.5 | +1.2 | +0.7 / +1.5 | +0.9 / -0.2 | FAIL |
| 215 | 5 Mean reversion / NR7 / gaps / round numbers | NR7 breakout 1.8ATR | M15 | 471.3 | -0.0 | +0.3 | +1.7 | -0.1 | -0.5 / +0.6 | +0.3 / +0.4 | FAIL |
| 216 | 5 Mean reversion / NR7 / gaps / round numbers | inside bar breakout stop=other side | M15 | 380.0 | +0.2 | +0.9 | +0.2 | +1.9 | +0.2 / +1.5 | +1.2 / +0.1 | all 4 > 0, pooled z 2.1 |
| 217 | 5 Mean reversion / NR7 / gaps / round numbers | inside bar breakout 1.8ATR | M15 | 380.0 | -0.1 | -0.0 | +0.5 | +1.4 | -0.0 / +0.5 | +0.9 / +1.2 | FAIL |
| 218 | 5 Mean reversion / NR7 / gaps / round numbers | NR7+inside breakout stop=other side | M15 | 158.6 | +0.9 | +1.4 | -0.1 | +3.1 | +0.7 / +1.5 | +0.2 / +2.2 | FAIL |
| 219 | 5 Mean reversion / NR7 / gaps / round numbers | NR7+inside breakout 1.8ATR | M15 | 158.6 | -0.3 | -0.0 | +1.4 | +0.4 | -1.5 / -0.1 | +0.5 / +1.6 | FAIL |
| 220 | 5 Mean reversion / NR7 / gaps / round numbers | daily reopen gap>0.5ATR fade 1.8ATR | M15 | 1.8 | +0.9 | +9.9 | -16.1 | -7.5 | -8.7 / +7.1 | +0.0 / -6.9 | FAIL ; few trades |
| 221 | 5 Mean reversion / NR7 / gaps / round numbers | daily reopen gap>0.5ATR continue 1.8ATR | M15 | 1.8 | -5.0 | +5.5 | -3.4 | +13.4 | +1.0 / +13.1 | -2.9 / -3.1 | FAIL ; few trades |
| 222 | 5 Mean reversion / NR7 / gaps / round numbers | weekly reopen gap>0.5ATR fade 1.8ATR | M15 | 1.9 | -15.5 | +2.6 | -28.4 | +12.2 | -11.7 / +9.4 | -24.0 / +12.9 | FAIL ; few trades |
| 223 | 5 Mean reversion / NR7 / gaps / round numbers | weekly reopen gap>0.5ATR continue 1.8ATR | M15 | 1.9 | -9.8 | +18.4 | -8.0 | +24.8 | -17.0 / +16.7 | -12.9 / +20.1 | FAIL ; few trades |
| 224 | 5 Mean reversion / NR7 / gaps / round numbers | round $10 reject 1.8ATR | M15 | 133.3 | -0.7 | -0.6 | -1.9 | -0.2 | -0.0 / -1.3 | -1.0 / -0.9 | FAIL |
| 225 | 5 Mean reversion / NR7 / gaps / round numbers | round $10 break 1.8ATR | M15 | 165.9 | -0.2 | +1.4 | -0.7 | +4.2 | +1.1 / +1.1 | +1.1 / +3.5 | FAIL |
| 226 | 5 Mean reversion / NR7 / gaps / round numbers | round $50 reject 1.8ATR | M15 | 24.5 | -1.7 | -2.4 | -1.6 | +1.7 | -2.0 / -3.1 | -1.4 / +1.8 | FAIL |
| 227 | 5 Mean reversion / NR7 / gaps / round numbers | round $50 break 1.8ATR | M15 | 32.0 | +0.3 | +0.8 | +1.9 | +3.9 | +0.5 / +1.0 | +0.8 / +3.0 | all 4 > 0, z 1.4 (noise level) |
| 228 | 5 Mean reversion / NR7 / gaps / round numbers | 5 bars one way -> fade 1.8ATR | M5 | 159.6 | +0.9 | +0.8 | -1.6 | -0.5 | -0.2 / +1.0 | -0.3 / -0.4 | FAIL |
| 229 | 5 Mean reversion / NR7 / gaps / round numbers | 5 bars one way -> continue 1.8ATR | M5 | 159.6 | +0.4 | -0.4 | -0.2 | +1.7 | +0.1 / +0.4 | +0.3 / +0.8 | FAIL |
| 230 | 5 Mean reversion / NR7 / gaps / round numbers | 7 bars one way -> fade 1.8ATR | M5 | 37.4 | +2.9 | +0.9 | -0.8 | +0.2 | +4.0 / +0.2 | -1.1 / +1.3 | FAIL |
| 231 | 5 Mean reversion / NR7 / gaps / round numbers | 7 bars one way -> continue 1.8ATR | M5 | 37.4 | -2.2 | -2.5 | -0.2 | -0.3 | -1.4 / -4.3 | -1.0 / +1.3 | FAIL |
| 232 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>4ATR fade 1.8ATR | M5 | 94.2 | +2.5 | +0.5 | -0.2 | -0.3 | +2.9 / +0.6 | +0.9 / -0.3 | FAIL |
| 233 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>4ATR fade 3ATR | M5 | 94.2 | +2.5 | +2.0 | +0.3 | -1.7 | +2.8 / +2.0 | -0.7 / -1.4 | FAIL |
| 234 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>6ATR fade 1.8ATR | M5 | 45.0 | +2.0 | +2.8 | +5.0 | +1.5 | +3.2 / +4.3 | +1.7 / +1.8 | all 4 > 0, pooled z 2.6 |
| 235 | 5 Mean reversion / NR7 / gaps / round numbers | |C-VWAP|>6ATR fade 3ATR | M5 | 45.0 | +0.3 | +2.6 | +5.8 | -0.6 | +1.2 / +3.9 | +1.8 / -0.4 | FAIL |
| 236 | 5 Mean reversion / NR7 / gaps / round numbers | z>3sig fade 1.8ATR | M5 | 31.2 | +1.0 | -2.6 | -5.5 | -2.9 | +1.8 / -2.9 | -4.7 / -1.9 | FAIL |
| 237 | 5 Mean reversion / NR7 / gaps / round numbers | NR7 breakout stop=other side | M5 | 1359.6 | -0.3 | +0.4 | -2.0 | +1.9 | +1.3 / +1.6 | +1.0 / +0.9 | FAIL |
| 238 | 5 Mean reversion / NR7 / gaps / round numbers | NR7 breakout 1.8ATR | M5 | 1359.6 | +0.4 | +0.7 | +0.7 | +0.3 | +0.0 / +0.1 | -0.0 / +0.1 | all 4 > 0, pooled z 2.8 |
| 239 | 5 Mean reversion / NR7 / gaps / round numbers | inside bar breakout stop=other side | M5 | 1068.0 | -0.4 | -0.0 | -1.2 | +1.9 | +0.8 / +0.7 | +1.3 / +0.8 | FAIL |
| 240 | 5 Mean reversion / NR7 / gaps / round numbers | inside bar breakout 1.8ATR | M5 | 1068.0 | -0.2 | +0.9 | +0.9 | +0.9 | -0.3 / +0.5 | +0.5 / +0.8 | FAIL |
| 241 | 5 Mean reversion / NR7 / gaps / round numbers | NR7+inside breakout stop=other side | M5 | 428.6 | -1.2 | -0.2 | -2.5 | +0.8 | +0.5 / +0.8 | -0.0 / -0.4 | FAIL |
| 242 | 5 Mean reversion / NR7 / gaps / round numbers | NR7+inside breakout 1.8ATR | M5 | 428.6 | -0.3 | +0.4 | +0.6 | +0.2 | -0.8 / +0.2 | -0.5 / +0.1 | FAIL |
| 243 | 5 Mean reversion / NR7 / gaps / round numbers | daily reopen gap>0.5ATR fade 1.8ATR | M5 | 7.3 | +2.3 | -3.7 | +11.4 | -0.8 | -2.0 / -5.7 | +11.0 / -2.2 | FAIL ; few trades |
| 244 | 5 Mean reversion / NR7 / gaps / round numbers | daily reopen gap>0.5ATR continue 1.8ATR | M5 | 7.3 | +0.3 | +0.6 | +5.3 | -15.0 | +3.1 / +2.5 | +6.9 / -15.2 | FAIL ; few trades |
| 245 | 5 Mean reversion / NR7 / gaps / round numbers | weekly reopen gap>0.5ATR fade 1.8ATR | M5 | 3.4 | -2.6 | -2.3 | -9.5 | +2.0 | +2.6 / -1.1 | -8.3 / +8.1 | FAIL ; few trades |
| 246 | 5 Mean reversion / NR7 / gaps / round numbers | weekly reopen gap>0.5ATR continue 1.8ATR | M5 | 3.4 | +3.8 | +6.5 | -2.3 | +3.3 | +2.1 / +1.1 | -5.4 / +3.1 | FAIL ; few trades |
| 247 | 5 Mean reversion / NR7 / gaps / round numbers | round $10 reject 1.8ATR | M5 | 166.6 | -0.5 | -0.4 | -1.8 | +1.9 | -0.8 / -1.3 | -2.6 / +1.0 | FAIL |
| 248 | 5 Mean reversion / NR7 / gaps / round numbers | round $10 break 1.8ATR | M5 | 208.1 | +0.2 | +0.3 | -0.9 | +2.5 | +0.1 / -0.2 | -0.3 / +2.4 | FAIL |
| 249 | 5 Mean reversion / NR7 / gaps / round numbers | round $50 reject 1.8ATR | M5 | 30.9 | -2.8 | +0.3 | -1.7 | +3.0 | +0.8 / -0.3 | -2.3 / +2.8 | FAIL |
| 250 | 5 Mean reversion / NR7 / gaps / round numbers | round $50 break 1.8ATR | M5 | 39.6 | +3.2 | +0.9 | +2.0 | +3.9 | +4.8 / -0.8 | +1.0 / +4.5 | all 4 > 0, pooled z 2.5 |
| 251 | 6 Generic stop-entry controls | random stop-entry C+-0.3ATR 1.8ATR | M15 | 346.0 | +0.5 | +0.7 | -0.8 | +0.3 | +1.0 / +0.7 | -0.3 / +1.4 | FAIL |
| 252 | 6 Generic stop-entry controls | random stop-entry C+-1.0ATR 1.8ATR | M15 | 175.0 | +0.0 | -1.1 | +0.1 | +1.9 | +1.8 / -0.7 | +0.3 / +0.4 | FAIL |
| 253 | 6 Generic stop-entry controls | random-bar 6-bar hi/lo stop-entry 1.8ATR | M15 | 172.7 | +0.5 | -1.1 | +0.3 | +3.0 | +1.2 / -0.3 | +0.1 / +2.0 | FAIL |
| 254 | 6 Generic stop-entry controls | random-bar 24-bar hi/lo stop-entry 1.8ATR | M15 | 93.1 | -1.4 | -1.0 | +0.2 | +2.0 | -0.5 / +2.3 | +0.5 / +0.9 | FAIL |
| 255 | 6 Generic stop-entry controls | random stop-entry C+-0.3ATR 1.8ATR | M5 | 347.5 | +0.1 | +0.2 | +1.3 | -0.4 | -0.8 / +0.1 | +1.4 / -1.2 | FAIL |
| 256 | 6 Generic stop-entry controls | random stop-entry C+-1.0ATR 1.8ATR | M5 | 176.3 | +0.3 | -0.1 | +0.1 | +0.8 | +1.5 / +0.7 | +1.1 / +0.4 | FAIL |
| 257 | 6 Generic stop-entry controls | random-bar 6-bar hi/lo stop-entry 1.8ATR | M5 | 172.8 | +0.5 | -0.4 | +1.1 | +0.5 | +0.7 / -0.7 | +1.4 / -0.2 | FAIL |
| 258 | 6 Generic stop-entry controls | random-bar 24-bar hi/lo stop-entry 1.8ATR | M5 | 91.4 | +1.1 | -3.2 | -1.0 | +1.7 | +2.0 / -2.2 | -0.6 / +1.3 | FAIL |
| 259 | 2 Liquidity sweeps | PDH/PDL sweep any time mkt stop=ext | H1 | 17.4 | -2.4 | -0.2 | -0.5 | +1.6 | -2.4 / +1.7 | +1.3 / -0.5 | FAIL |
| 260 | 2 Liquidity sweeps | PDH/PDL sweep any time mkt 1.8ATR | H1 | 17.4 | -1.4 | +1.4 | -2.5 | +0.0 | -1.0 / +4.2 | -2.4 / -1.2 | FAIL |
| 261 | 2 Liquidity sweeps | PDH/PDL sweep any time stopentry(conf) stop=ext | H1 | 10.8 | +0.2 | +3.0 | -5.2 | +2.2 | +1.2 / +2.8 | -5.5 / -0.4 | FAIL |
| 262 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 mkt stop=ext | H1 | 12.9 | -4.4 | +2.6 | +6.2 | +3.8 | +0.8 / +4.0 | +5.2 / +1.7 | FAIL |
| 263 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 mkt 1.8ATR | H1 | 12.9 | -3.7 | +1.2 | -3.7 | +1.9 | +0.8 / +2.5 | -3.9 / -0.6 | FAIL |
| 264 | 2 Liquidity sweeps | PDH/PDL sweep NY 03-12 stopentry(conf) stop=ext | H1 | 8.4 | -5.2 | +5.8 | -3.8 | +2.9 | -2.1 / +9.1 | +1.1 / -3.5 | FAIL |
| 265 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 mkt stop=ext | H1 | 15.7 | +1.7 | -0.1 | -3.1 | -4.8 | +2.8 / +0.2 | +1.8 / -9.3 | FAIL |
| 266 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 mkt 1.8ATR | H1 | 15.7 | +2.0 | +0.1 | -0.8 | -2.3 | +3.5 / -1.1 | +0.1 / -6.9 | FAIL |
| 267 | 2 Liquidity sweeps | day-high/low(old>=2h) sweep 03-16 stopentry(conf) stop=ext | H1 | 9.1 | +1.3 | +4.2 | -4.0 | -6.1 | +2.3 / +4.3 | -2.9 / -8.4 | FAIL |
| 268 | 2 Liquidity sweeps | London range sweep in NY 08-12 mkt stop=ext | H1 | 18.4 | -1.5 | +1.4 | -6.0 | +0.4 | -0.0 / +0.4 | -4.2 / -2.5 | FAIL |
| 269 | 2 Liquidity sweeps | London range sweep in NY 08-12 mkt 1.8ATR | H1 | 18.4 | -1.5 | -0.5 | -3.8 | -1.0 | +0.0 / -1.4 | -4.4 / -2.4 | FAIL |
| 270 | 2 Liquidity sweeps | London range sweep in NY 08-12 stopentry(conf) stop=ext | H1 | 11.4 | +2.3 | +3.2 | -1.0 | -4.6 | +0.3 / +1.7 | -3.1 / -6.1 | FAIL |
| 271 | 7 Sensitivity A (NY open range) | A base start 09:30 L30 end 13:00 buf 0.05 1.8ATR | M15 | 25.2 | +1.8 | +4.5 | +3.9 | +3.1 | +2.2 / +3.0 | +4.9 / +1.7 | all 4 > 0, pooled z 2.4 |
| 272 | 7 Sensitivity A (NY open range) | A len start 09:30 L15 end 13:00 buf 0.05 1.8ATR | M15 | 30.4 | +1.6 | +3.2 | +0.9 | +4.0 | +0.6 / +2.1 | +0.5 / +1.4 | all 4 > 0, z 1.9 (noise level) |
| 273 | 7 Sensitivity A (NY open range) | A len start 09:30 L45 end 13:00 buf 0.05 1.8ATR | M15 | 21.0 | +1.4 | +3.2 | +1.6 | +4.1 | +0.6 / +2.6 | +1.5 / +10.9 | all 4 > 0, z 1.7 (noise level) |
| 274 | 7 Sensitivity A (NY open range) | A len start 09:30 L60 end 13:00 buf 0.05 1.8ATR | M15 | 18.5 | +1.5 | +1.4 | +3.6 | +3.4 | +1.6 / +0.4 | +4.3 / +8.8 | all 4 > 0, z 1.4 (noise level) |
| 275 | 7 Sensitivity A (NY open range) | A start start 08:30 L30 end 13:00 buf 0.05 1.8ATR | M15 | 29.2 | -0.1 | +3.9 | -2.9 | +2.9 | +0.5 / +2.6 | +0.9 / -0.5 | FAIL |
| 276 | 7 Sensitivity A (NY open range) | A start start 09:00 L30 end 13:00 buf 0.05 1.8ATR | M15 | 30.8 | +1.7 | +1.9 | -2.2 | +3.5 | +0.5 / +0.8 | -2.7 / +0.8 | FAIL |
| 277 | 7 Sensitivity A (NY open range) | A start start 10:00 L30 end 13:00 buf 0.05 1.8ATR | M15 | 24.3 | +0.6 | +0.3 | -0.4 | +0.4 | +1.6 / +1.2 | +0.1 / +6.0 | FAIL |
| 278 | 7 Sensitivity A (NY open range) | A end start 09:30 L30 end 12:00 buf 0.05 1.8ATR | M15 | 24.1 | +2.0 | +4.6 | +4.0 | +3.3 | +2.6 / +3.3 | +4.5 / +2.4 | all 4 > 0, pooled z 2.5 |
| 279 | 7 Sensitivity A (NY open range) | A end start 09:30 L30 end 16:00 buf 0.05 1.8ATR | M15 | 27.6 | +3.2 | +4.9 | +2.3 | +3.1 | +3.3 / +4.0 | +3.6 / +1.9 | all 4 > 0, pooled z 2.8 |
| 280 | 7 Sensitivity A (NY open range) | A stop start 09:30 L30 end 13:00 buf 0.05 1.0ATR | M15 | 25.2 | +1.6 | +3.2 | -1.1 | +2.7 | +2.3 / +3.8 | +1.5 / -0.2 | FAIL |
| 281 | 7 Sensitivity A (NY open range) | A stop start 09:30 L30 end 13:00 buf 0.05 3.0ATR | M15 | 25.2 | +1.3 | +2.4 | +2.8 | -1.6 | +1.0 / +1.5 | +1.7 / -0.6 | FAIL |
| 282 | 7 Sensitivity A (NY open range) | A buf start 09:30 L30 end 13:00 buf 0.30 1.8ATR | M15 | 22.2 | +3.0 | +2.1 | +1.7 | +0.3 | +2.6 / +0.6 | +1.8 / +1.1 | all 4 > 0, z 1.4 (noise level) |
| 283 | 7 Sensitivity A (NY open range) | A base start 09:30 L30 end 13:00 buf 0.05 1.8ATR | M5 | 25.4 | +2.0 | +3.2 | +1.0 | +3.2 | +1.7 / +2.3 | +1.0 / +2.9 | all 4 > 0, z 1.8 (noise level) |
| 284 | 7 Sensitivity A (NY open range) | A len start 09:30 L15 end 13:00 buf 0.05 1.8ATR | M5 | 30.5 | +1.9 | +2.4 | +1.0 | +3.8 | +0.8 / +2.8 | -0.4 / +1.3 | all 4 > 0, z 1.8 (noise level) |
| 285 | 7 Sensitivity A (NY open range) | A len start 09:30 L45 end 13:00 buf 0.05 1.8ATR | M5 | 21.2 | +2.2 | +1.6 | -0.9 | +2.0 | +2.0 / +0.5 | +0.5 / +7.2 | FAIL |
| 286 | 7 Sensitivity A (NY open range) | A len start 09:30 L60 end 13:00 buf 0.05 1.8ATR | M5 | 18.7 | +0.6 | +1.5 | +0.5 | +2.3 | +1.1 / -0.1 | +2.2 / +6.6 | all 4 > 0, z 0.7 (noise level) ; few trades |
| 287 | 7 Sensitivity A (NY open range) | A start start 08:30 L30 end 13:00 buf 0.05 1.8ATR | M5 | 29.5 | -0.7 | +1.7 | -2.5 | +3.5 | +2.9 / +1.1 | +2.6 / +0.4 | FAIL |
| 288 | 7 Sensitivity A (NY open range) | A start start 09:00 L30 end 13:00 buf 0.05 1.8ATR | M5 | 31.0 | +0.7 | +1.9 | -2.7 | +2.5 | +0.6 / +1.9 | -1.7 / +1.0 | FAIL |
| 289 | 7 Sensitivity A (NY open range) | A start start 10:00 L30 end 13:00 buf 0.05 1.8ATR | M5 | 24.6 | -0.6 | +1.9 | +0.1 | +1.4 | +0.4 / +1.5 | +0.8 / +5.3 | FAIL |
| 290 | 7 Sensitivity A (NY open range) | A end start 09:30 L30 end 12:00 buf 0.05 1.8ATR | M5 | 24.3 | +2.0 | +3.5 | +1.7 | +3.2 | +1.4 / +2.2 | +1.4 / +1.9 | all 4 > 0, z 1.9 (noise level) |
| 291 | 7 Sensitivity A (NY open range) | A end start 09:30 L30 end 16:00 buf 0.05 1.8ATR | M5 | 27.7 | +2.3 | +3.1 | -0.8 | +3.0 | +2.0 / +2.2 | -0.4 / +3.0 | FAIL |
| 292 | 7 Sensitivity A (NY open range) | A stop start 09:30 L30 end 13:00 buf 0.05 1.0ATR | M5 | 25.4 | -1.3 | +0.7 | -4.3 | +0.3 | +1.6 / +5.2 | +0.9 / +3.8 | FAIL |
| 293 | 7 Sensitivity A (NY open range) | A stop start 09:30 L30 end 13:00 buf 0.05 3.0ATR | M5 | 25.4 | +2.6 | +3.8 | +4.3 | +0.8 | +1.0 / +1.9 | +3.9 / +1.3 | all 4 > 0, pooled z 2.2 |
| 294 | 7 Sensitivity A (NY open range) | A buf start 09:30 L30 end 13:00 buf 0.30 1.8ATR | M5 | 23.2 | +1.8 | +1.4 | -2.3 | -1.2 | +0.6 / +0.8 | -1.5 / -0.5 | FAIL |
| 295 | 8 Sensitivity B (PDH/PDL sweep) | B base 00-24 first depth0.0 W3 buf0.05 ext+0.1 stop | M15 | 11.9 | +3.3 | +4.3 | +6.0 | +8.2 | +5.2 / +4.6 | +6.0 / +7.5 | all 4 > 0, pooled z 2.5 |
| 296 | 8 Sensitivity B (PDH/PDL sweep) | B W 00-24 first depth0.0 W1 buf0.05 ext+0.1 stop | M15 | 9.2 | +6.5 | +3.9 | +6.9 | +8.9 | +7.8 / +5.2 | +8.3 / +8.1 | all 4 > 0, pooled z 2.7 |
| 297 | 8 Sensitivity B (PDH/PDL sweep) | B W 00-24 first depth0.0 W6 buf0.05 ext+0.1 stop | M15 | 13.4 | +4.0 | +3.6 | +4.9 | +5.3 | +6.2 / +4.0 | +2.6 / +5.8 | all 4 > 0, pooled z 2.3 |
| 298 | 8 Sensitivity B (PDH/PDL sweep) | B buf 00-24 first depth0.0 W3 buf0.25 ext+0.1 stop | M15 | 10.3 | +2.5 | +5.9 | +8.2 | +10.4 | +4.7 / +6.1 | +8.7 / +10.3 | all 4 > 0, pooled z 2.6 |
| 299 | 8 Sensitivity B (PDH/PDL sweep) | B sbuf 00-24 first depth0.0 W3 buf0.05 ext+0.4 stop | M15 | 11.9 | +2.5 | +2.8 | +2.8 | +5.3 | +5.0 / +3.2 | +3.2 / +6.1 | all 4 > 0, z 1.6 (noise level) |
| 300 | 8 Sensitivity B (PDH/PDL sweep) | B atrstop 00-24 first depth0.0 W3 buf0.05 1.8ATR stop | M15 | 11.9 | +2.9 | +4.3 | +1.6 | +6.3 | +5.5 / +3.0 | +3.2 / +5.2 | all 4 > 0, z 1.9 (noise level) |
| 301 | 8 Sensitivity B (PDH/PDL sweep) | B atrstop3 00-24 first depth0.0 W3 buf0.05 3.0ATR stop | M15 | 11.9 | +2.4 | +3.0 | -0.2 | +2.3 | +5.0 / +2.8 | +3.0 / +1.4 | FAIL |
| 302 | 8 Sensitivity B (PDH/PDL sweep) | B all 00-24 all depth0.0 W3 buf0.05 ext+0.1 stop | M15 | 34.8 | +2.8 | +1.1 | +3.2 | +5.7 | +3.6 / +0.8 | +5.1 / +4.4 | all 4 > 0, pooled z 2.4 |
| 303 | 8 Sensitivity B (PDH/PDL sweep) | B depth 00-24 first depth0.3 W3 buf0.05 ext+0.1 stop | M15 | 11.8 | +1.1 | +3.1 | +6.7 | +7.2 | +1.8 / +3.6 | +6.5 / +5.9 | all 4 > 0, z 1.8 (noise level) |
| 304 | 8 Sensitivity B (PDH/PDL sweep) | B time 03-12 first depth0.0 W3 buf0.05 ext+0.1 stop | M15 | 9.6 | +0.6 | +5.7 | +7.3 | +11.6 | +2.9 / +4.7 | +12.4 / +11.0 | all 4 > 0, pooled z 2.3 |
| 305 | 8 Sensitivity B (PDH/PDL sweep) | B time 12-17 first depth0.0 W3 buf0.05 ext+0.1 stop | M15 | 3.8 | -2.8 | -1.0 | -3.7 | +0.4 | -1.4 / -3.9 | +0.1 / +4.6 | FAIL ; few trades |
| 306 | 8 Sensitivity B (PDH/PDL sweep) | B time 18-03 first depth0.0 W3 buf0.05 ext+0.1 stop | M15 | 5.4 | +9.1 | +1.1 | +4.1 | +3.7 | +6.7 / +2.4 | +0.6 / +2.7 | all 4 > 0, z 1.6 (noise level) ; few trades |
| 307 | 8 Sensitivity B (PDH/PDL sweep) | B base 00-24 first depth0.0 W3 buf0.05 ext+0.1 stop | M5 | 12.6 | +4.5 | +3.5 | +5.6 | -1.0 | +1.9 / +0.0 | +5.5 / -3.7 | FAIL ; few trades |
| 308 | 8 Sensitivity B (PDH/PDL sweep) | B W 00-24 first depth0.0 W1 buf0.05 ext+0.1 stop | M5 | 9.6 | +6.0 | +4.2 | +7.9 | -4.5 | +2.8 / +0.9 | +7.6 / -6.2 | FAIL ; few trades |
| 309 | 8 Sensitivity B (PDH/PDL sweep) | B W 00-24 first depth0.0 W6 buf0.05 ext+0.1 stop | M5 | 14.0 | +5.0 | +4.7 | +6.2 | +0.2 | +4.0 / +1.1 | +5.7 / -1.5 | all 4 > 0, pooled z 2.3 ; few trades |
| 310 | 8 Sensitivity B (PDH/PDL sweep) | B buf 00-24 first depth0.0 W3 buf0.25 ext+0.1 stop | M5 | 10.8 | +3.5 | +2.2 | +4.6 | +0.1 | +1.0 / -0.3 | +4.0 / -3.3 | all 4 > 0, z 1.3 (noise level) ; few trades |
| 311 | 8 Sensitivity B (PDH/PDL sweep) | B sbuf 00-24 first depth0.0 W3 buf0.05 ext+0.4 stop | M5 | 12.6 | +4.2 | +0.3 | +7.5 | -1.0 | +3.0 / -3.5 | +7.4 / -2.2 | FAIL ; few trades |
| 312 | 8 Sensitivity B (PDH/PDL sweep) | B atrstop 00-24 first depth0.0 W3 buf0.05 1.8ATR stop | M5 | 12.6 | +4.8 | +1.6 | +2.3 | +2.1 | +4.0 / -0.9 | +2.4 / -0.1 | all 4 > 0, z 1.5 (noise level) ; few trades |
| 313 | 8 Sensitivity B (PDH/PDL sweep) | B atrstop3 00-24 first depth0.0 W3 buf0.05 3.0ATR stop | M5 | 12.6 | +0.2 | +1.3 | +1.7 | -1.4 | -0.1 / +0.2 | +2.6 / -3.0 | FAIL ; few trades |
| 314 | 8 Sensitivity B (PDH/PDL sweep) | B all 00-24 all depth0.0 W3 buf0.05 ext+0.1 stop | M5 | 37.6 | +3.5 | +1.4 | +2.2 | +3.8 | +3.9 / +1.7 | +3.2 / +1.2 | all 4 > 0, pooled z 2.4 |
| 315 | 8 Sensitivity B (PDH/PDL sweep) | B depth 00-24 first depth0.3 W3 buf0.05 ext+0.1 stop | M5 | 12.9 | +5.6 | +4.2 | +6.6 | -2.8 | +3.7 / +3.9 | +9.9 / -0.2 | FAIL ; few trades |
| 316 | 8 Sensitivity B (PDH/PDL sweep) | B time 03-12 first depth0.0 W3 buf0.05 ext+0.1 stop | M5 | 10.4 | +4.3 | +3.0 | +8.6 | +4.1 | +3.0 / +3.2 | +2.3 / -0.7 | all 4 > 0, pooled z 2.0 ; few trades |
| 317 | 8 Sensitivity B (PDH/PDL sweep) | B time 12-17 first depth0.0 W3 buf0.05 ext+0.1 stop | M5 | 4.0 | -1.5 | +5.9 | -1.9 | +2.3 | -6.3 / +5.6 | -1.7 / -3.5 | FAIL ; few trades |
| 318 | 8 Sensitivity B (PDH/PDL sweep) | B time 18-03 first depth0.0 W3 buf0.05 ext+0.1 stop | M5 | 5.6 | +5.8 | -1.1 | +1.8 | -0.8 | +7.5 / -2.5 | -0.7 / -3.2 | FAIL ; few trades |
| 319 | 8 Sensitivity B (PDH/PDL sweep) | B base 00-24 first depth0.0 W3 buf0.05 ext+0.1 stop | H1 | 10.8 | +0.2 | +3.0 | -5.2 | +2.2 | +1.2 / +2.8 | -5.5 / -0.4 | FAIL |
| 320 | 8 Sensitivity B (PDH/PDL sweep) | B W 00-24 first depth0.0 W1 buf0.05 ext+0.1 stop | H1 | 7.9 | +2.9 | +4.7 | -3.9 | +4.0 | +4.4 / +4.0 | -6.6 / +0.7 | FAIL |
| 321 | 8 Sensitivity B (PDH/PDL sweep) | B W 00-24 first depth0.0 W6 buf0.05 ext+0.1 stop | H1 | 12.3 | +2.5 | +2.6 | -4.1 | +0.3 | +4.2 / +2.4 | -3.8 / -2.6 | FAIL |
| 322 | 8 Sensitivity B (PDH/PDL sweep) | B buf 00-24 first depth0.0 W3 buf0.25 ext+0.1 stop | H1 | 9.1 | -0.9 | +3.4 | +4.5 | +3.5 | +0.9 / +3.1 | +0.3 / -1.0 | FAIL |
| 323 | 8 Sensitivity B (PDH/PDL sweep) | B sbuf 00-24 first depth0.0 W3 buf0.05 ext+0.4 stop | H1 | 10.8 | +0.2 | +0.4 | -3.4 | +2.2 | +0.7 / +1.6 | -5.7 / +1.1 | FAIL |
| 324 | 8 Sensitivity B (PDH/PDL sweep) | B atrstop 00-24 first depth0.0 W3 buf0.05 1.8ATR stop | H1 | 10.8 | -1.4 | +1.1 | -3.1 | -0.3 | -2.7 / +3.4 | -1.4 / -1.9 | FAIL |
| 325 | 8 Sensitivity B (PDH/PDL sweep) | B atrstop3 00-24 first depth0.0 W3 buf0.05 3.0ATR stop | H1 | 10.8 | -0.1 | +2.7 | +1.7 | +1.7 | +0.7 / +4.8 | +1.0 / +1.9 | FAIL |
| 326 | 8 Sensitivity B (PDH/PDL sweep) | B all 00-24 all depth0.0 W3 buf0.05 ext+0.1 stop | H1 | 28.7 | +2.4 | +0.4 | -7.3 | +2.1 | +2.5 / +0.9 | -11.0 / +2.1 | FAIL |
| 327 | 8 Sensitivity B (PDH/PDL sweep) | B depth 00-24 first depth0.3 W3 buf0.05 ext+0.1 stop | H1 | 9.5 | +0.1 | -0.6 | -4.7 | -0.2 | +3.0 / -0.9 | -5.6 / -1.4 | FAIL |
| 328 | 8 Sensitivity B (PDH/PDL sweep) | B time 03-12 first depth0.0 W3 buf0.05 ext+0.1 stop | H1 | 8.4 | -5.2 | +5.8 | -3.8 | +2.9 | -2.1 / +9.1 | +1.1 / -3.5 | FAIL |
| 329 | 8 Sensitivity B (PDH/PDL sweep) | B time 12-17 first depth0.0 W3 buf0.05 ext+0.1 stop | H1 | 3.0 | +2.6 | -6.0 | -13.0 | +0.3 | -2.7 / +0.8 | -5.7 / -3.1 | FAIL ; few trades |
| 330 | 8 Sensitivity B (PDH/PDL sweep) | B time 18-03 first depth0.0 W3 buf0.05 ext+0.1 stop | H1 | 4.9 | +9.0 | +5.7 | -5.6 | +0.6 | +12.2 / +12.0 | -9.2 / -10.3 | FAIL |
| 331 | 9 Sensitivity C (round $ break) | C round $25 break 1.8ATR declust 1h | M5 | 92.8 | +1.8 | -2.4 | +1.3 | +2.0 | +2.1 / -3.2 | +2.1 / +0.4 | FAIL |
| 332 | 9 Sensitivity C (round $ break) | C round $50 break 1.8ATR declust 1h | M5 | 39.6 | +3.2 | +0.9 | +2.0 | +3.9 | +4.8 / -0.8 | +1.0 / +4.5 | all 4 > 0, pooled z 2.5 |
| 333 | 9 Sensitivity C (round $ break) | C round $100 break 1.8ATR declust 1h | M5 | 18.7 | +3.1 | +1.0 | +3.0 | +1.7 | +3.4 / +1.4 | +3.0 / +0.2 | all 4 > 0, z 1.5 (noise level) ; few trades |
| 334 | 9 Sensitivity C (round $ break) | C round $50 break 1.0ATR declust 1h | M5 | 39.6 | +4.4 | -0.9 | +0.1 | +2.8 | +5.5 / -1.5 | +0.1 / +0.4 | FAIL |
| 335 | 9 Sensitivity C (round $ break) | C round $50 break 3.0ATR declust 1h | M5 | 39.6 | +1.0 | +0.3 | +1.1 | +4.1 | +2.0 / -0.8 | +0.1 / +4.8 | all 4 > 0, z 1.5 (noise level) |
| 336 | 9 Sensitivity C (round $ break) | C round $50 break 1.8ATR declust 4h | M5 | 25.5 | -0.3 | +1.8 | +5.8 | +2.6 | +0.2 / +0.6 | +6.7 / +3.2 | FAIL |
| 337 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>5ATR fade 1.8ATR | M5 | 66.0 | +2.1 | +3.1 | +1.9 | +0.1 | +0.7 / +1.8 | +3.8 / -0.5 | all 4 > 0, pooled z 2.4 |
| 338 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>6ATR fade 1.8ATR | M5 | 45.0 | +2.0 | +2.8 | +5.0 | +1.5 | +3.2 / +4.3 | +1.7 / +1.8 | all 4 > 0, pooled z 2.6 |
| 339 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>7ATR fade 1.8ATR | M5 | 30.2 | +0.5 | -0.1 | +0.9 | +2.7 | +1.3 / +0.7 | +3.1 / +5.4 | FAIL |
| 340 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>8ATR fade 1.8ATR | M5 | 21.0 | +1.6 | +0.6 | +4.9 | +2.7 | -0.8 / -0.8 | +2.7 / +5.5 | all 4 > 0, z 1.4 (noise level) |
| 341 | 9 Sensitivity C (round $ break) | C round $25 break 1.8ATR declust 1h | M15 | 73.8 | +1.4 | -2.7 | -0.6 | +3.0 | +1.2 / -3.5 | +0.5 / +2.3 | FAIL |
| 342 | 9 Sensitivity C (round $ break) | C round $50 break 1.8ATR declust 1h | M15 | 32.0 | +0.3 | +0.8 | +1.9 | +3.9 | +0.5 / +1.0 | +0.8 / +3.0 | all 4 > 0, z 1.4 (noise level) |
| 343 | 9 Sensitivity C (round $ break) | C round $100 break 1.8ATR declust 1h | M15 | 14.8 | -1.4 | +3.0 | +1.7 | +0.6 | -3.3 / +1.5 | +3.1 / +1.1 | FAIL |
| 344 | 9 Sensitivity C (round $ break) | C round $50 break 1.0ATR declust 1h | M15 | 32.0 | +1.6 | +2.0 | +0.7 | +5.8 | +1.9 / +2.0 | +0.6 / +4.0 | all 4 > 0, pooled z 2.2 |
| 345 | 9 Sensitivity C (round $ break) | C round $50 break 3.0ATR declust 1h | M15 | 32.0 | -2.7 | +2.7 | +3.5 | +4.2 | -1.5 / +2.4 | +0.6 / +4.6 | FAIL |
| 346 | 9 Sensitivity C (round $ break) | C round $50 break 1.8ATR declust 4h | M15 | 22.8 | -1.3 | -0.0 | +3.5 | +2.6 | -0.1 / -1.2 | +5.8 / +3.1 | FAIL |
| 347 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>3ATR fade 1.8ATR | M15 | 50.1 | +0.1 | +3.0 | +0.1 | +2.2 | +0.9 / +2.5 | +1.7 / +0.6 | all 4 > 0, z 1.6 (noise level) |
| 348 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>4ATR fade 1.8ATR | M15 | 25.2 | +0.5 | -0.3 | +1.2 | -0.0 | +2.1 / +1.0 | +0.9 / +0.1 | FAIL |
| 349 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>5ATR fade 1.8ATR | M15 | 13.2 | +2.4 | +3.3 | -1.0 | -3.7 | +1.0 / +4.8 | -1.1 / -2.1 | FAIL |
| 350 | 9 Sensitivity C (round $ break) | C round $25 break 1.8ATR declust 1h | H1 | 44.1 | -1.9 | +0.1 | +0.4 | +2.3 | -1.2 / -1.3 | +0.3 / +2.2 | FAIL |
| 351 | 9 Sensitivity C (round $ break) | C round $50 break 1.8ATR declust 1h | H1 | 19.7 | -2.8 | +3.5 | +2.5 | +4.0 | -1.9 / +4.6 | +1.6 / +4.0 | FAIL |
| 352 | 9 Sensitivity C (round $ break) | C round $100 break 1.8ATR declust 1h | H1 | 9.4 | -5.5 | +4.4 | +8.6 | -1.2 | -7.1 / +5.0 | +10.9 / -0.5 | FAIL |
| 353 | 9 Sensitivity C (round $ break) | C round $50 break 1.0ATR declust 1h | H1 | 19.7 | -1.5 | +1.8 | +3.1 | +4.3 | -3.2 / +2.1 | +2.0 / +2.8 | FAIL |
| 354 | 9 Sensitivity C (round $ break) | C round $50 break 3.0ATR declust 1h | H1 | 19.7 | -2.3 | +4.3 | +2.0 | +1.7 | -2.0 / +5.0 | -1.7 / +4.5 | FAIL |
| 355 | 9 Sensitivity C (round $ break) | C round $50 break 1.8ATR declust 4h | H1 | 17.4 | -3.1 | +4.6 | +3.0 | +5.9 | -2.5 / +3.9 | +2.6 / +5.5 | FAIL |
| 356 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>2ATR fade 1.8ATR | H1 | 16.6 | -1.2 | -0.0 | +0.1 | +0.6 | +0.6 / +0.1 | +0.5 / +2.9 | FAIL |
| 357 | 9 Sensitivity D (VWAP distance fade) | D |C-VWAP|>3ATR fade 1.8ATR | H1 | 5.9 | -2.2 | +4.1 | -2.9 | +8.2 | -5.7 / +2.3 | -4.9 / +13.6 | FAIL |
