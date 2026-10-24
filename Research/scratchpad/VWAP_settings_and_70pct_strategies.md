# VWAP settings and "70% win rate" strategies - full results

Data: 10 instruments, 5-minute bars, 31 Aug - 21 Oct 2026 (328 instrument-days). 1:1 = target 1R, 1:2 = target 2R.
Break-even win rate: 50% at 1:1, 33.3% at 1:2. R/trade = average result per trade in units of the stop distance.

## 1. VWAP settings on your indicator

Sep / Oct = R per trade in each month. "x/10" = instruments better than the current settings. CI = 95% bootstrap range of the
1:2 difference vs the current settings (whole days resampled). null = share of random skips of the same size that did worse.

```
== family Source / weights
Session VWAP, hlc3, slope 3 bars (current)   | 1:1 win 54.0% E +0.081 (Sep +0.074 Oct +0.092) 0/10 | 1:2 n 1189 win 38.9% E +0.166 (Sep +0.142 Oct +0.204) 0/10 tot +197 CI [+0.000,+0.000]
Session VWAP rebuilt from volume (check)     | 1:1 win 54.0% E +0.079 (Sep +0.072 Oct +0.092) 0/10 | 1:2 n 1187 win 38.9% E +0.168 (Sep +0.145 Oct +0.204) 2/10 tot +199 CI [+0.000,+0.006]
Source = close                               | 1:1 win 53.4% E +0.068 (Sep +0.086 Oct +0.039) 2/10 | 1:2 n 1200 win 38.1% E +0.142 (Sep +0.141 Oct +0.145) 2/10 tot +171 CI [-0.057,+0.010]
Source = hl2                                 | 1:1 win 53.7% E +0.074 (Sep +0.063 Oct +0.092) 3/10 | 1:2 n 1178 win 38.7% E +0.161 (Sep +0.140 Oct +0.195) 4/10 tot +190 CI [-0.019,+0.010]
Source = ohlc4                               | 1:1 win 53.9% E +0.078 (Sep +0.064 Oct +0.099) 3/10 | 1:2 n 1179 win 38.5% E +0.155 (Sep +0.121 Oct +0.211) 3/10 tot +183 CI [-0.027,+0.006]
Equal weights (time-weighted average)        | 1:1 win 54.0% E +0.079 (Sep +0.086 Oct +0.068) 4/10 | 1:2 n 1167 win 38.2% E +0.147 (Sep +0.139 Oct +0.160) 2/10 tot +171 CI [-0.053,+0.016]

== family Anchor
Weekly VWAP                                  | 1:1 win 51.5% E +0.030 (Sep +0.037 Oct +0.019) 3/10 | 1:2 n 1114 win 35.5% E +0.066 (Sep +0.070 Oct +0.060) 2/10 tot  +74 CI [-0.173,-0.026]
Monthly VWAP                                 | 1:1 win 51.3% E +0.026 (Sep +0.020 Oct +0.035) 2/10 | 1:2 n 1050 win 36.0% E +0.080 (Sep +0.071 Oct +0.094) 2/10 tot  +84 CI [-0.175,-0.008]

== family Slope
Slope off (position only)                    | 1:1 win 53.4% E +0.068 (Sep +0.057 Oct +0.085) 4/10 | 1:2 n 1224 win 38.1% E +0.142 (Sep +0.112 Oct +0.191) 3/10 tot +174 CI [-0.066,+0.019]
Slope 1 bar                                  | 1:1 win 53.0% E +0.059 (Sep +0.057 Oct +0.062) 3/10 | 1:2 n 1213 win 37.4% E +0.123 (Sep +0.104 Oct +0.152) 3/10 tot +149 CI [-0.083,-0.007]
Slope 2 bars                                 | 1:1 win 53.5% E +0.070 (Sep +0.080 Oct +0.055) 3/10 | 1:2 n 1199 win 37.7% E +0.131 (Sep +0.113 Oct +0.159) 2/10 tot +157 CI [-0.062,-0.007]
Slope 5 bars                                 | 1:1 win 54.5% E +0.090 (Sep +0.078 Oct +0.108) 5/10 | 1:2 n 1164 win 38.0% E +0.139 (Sep +0.103 Oct +0.197) 3/10 tot +162 CI [-0.064,+0.005]
Slope 10 bars                                | 1:1 win 54.0% E +0.079 (Sep +0.087 Oct +0.066) 5/10 | 1:2 n 1106 win 37.7% E +0.131 (Sep +0.111 Oct +0.164) 3/10 tot +145 CI [-0.077,+0.008]
Slope 3, not across the session start        | 1:1 win 54.1% E +0.082 (Sep +0.071 Oct +0.100) 2/10 | 1:2 n 1190 win 38.8% E +0.165 (Sep +0.138 Oct +0.208) 2/10 tot +196 CI [-0.010,+0.010]
Slope only (no above/below rule)             | 1:1 win 54.0% E +0.081 (Sep +0.074 Oct +0.092) 0/10 | 1:2 n 1189 win 38.9% E +0.166 (Sep +0.142 Oct +0.204) 0/10 tot +197 CI [+0.000,+0.000]
No VWAP rule at all                          | 1:1 win 51.0% E +0.021 (Sep +0.009 Oct +0.040) 2/10 | 1:2 n 1291 win 35.7% E +0.071 (Sep +0.047 Oct +0.108) 1/10 tot  +92 CI [-0.156,-0.036]

== family Distance (skipped run invisibly)
Max 1.5 sigma from VWAP (Don't Chase)        | 1:1 win 56.7% E +0.135 (Sep +0.116 Oct +0.166) 7/10 | 1:2 n  402 win 43.3% E +0.299 (Sep +0.261 Oct +0.366) 9/10 tot +120 CI [+0.019,+0.245] null 99%
Max 2.0 sigma from VWAP (Don't Chase)        | 1:1 win 56.6% E +0.131 (Sep +0.106 Oct +0.170) 8/10 | 1:2 n  660 win 42.3% E +0.268 (Sep +0.231 Oct +0.331) 10/10 tot +177 CI [+0.032,+0.177] null 100%
Max 2.4 sigma from VWAP (Don't Chase)        | 1:1 win 55.6% E +0.112 (Sep +0.086 Oct +0.150) 8/10 | 1:2 n  895 win 40.3% E +0.210 (Sep +0.172 Oct +0.269) 8/10 tot +188 CI [-0.001,+0.090] null 95%
Max 3.0 sigma from VWAP (Don't Chase)        | 1:1 win 54.8% E +0.096 (Sep +0.078 Oct +0.124) 7/10 | 1:2 n 1096 win 39.5% E +0.185 (Sep +0.148 Oct +0.244) 6/10 tot +203 CI [-0.004,+0.044] null 93%
Min 0.25 ATR from VWAP                       | 1:1 win 54.0% E +0.081 (Sep +0.074 Oct +0.092) 0/10 | 1:2 n 1189 win 38.9% E +0.166 (Sep +0.142 Oct +0.204) 0/10 tot +197 CI [+0.000,+0.000] null  0%
Min 0.50 ATR from VWAP                       | 1:1 win 53.8% E +0.077 (Sep +0.072 Oct +0.085) 0/10 | 1:2 n 1183 win 38.8% E +0.164 (Sep +0.137 Oct +0.208) 1/10 tot +194 CI [-0.009,+0.004] null 16%
Min 1.00 ATR from VWAP                       | 1:1 win 54.7% E +0.093 (Sep +0.097 Oct +0.087) 9/10 | 1:2 n 1120 win 39.8% E +0.195 (Sep +0.176 Oct +0.225) 8/10 tot +218 CI [+0.011,+0.049] null 100%
Min 0.25 sigma from VWAP                     | 1:1 win 54.1% E +0.083 (Sep +0.074 Oct +0.097) 3/10 | 1:2 n 1184 win 38.9% E +0.168 (Sep +0.142 Oct +0.209) 3/10 tot +199 CI [-0.002,+0.007] null 64%
Min 0.50 sigma from VWAP                     | 1:1 win 54.7% E +0.094 (Sep +0.091 Oct +0.099) 8/10 | 1:2 n 1143 win 39.4% E +0.181 (Sep +0.158 Oct +0.218) 8/10 tot +207 CI [+0.000,+0.031] null 96%
Min 1.00 sigma from VWAP                     | 1:1 win 54.3% E +0.086 (Sep +0.074 Oct +0.106) 7/10 | 1:2 n 1011 win 38.6% E +0.157 (Sep +0.130 Oct +0.200) 3/10 tot +159 CI [-0.042,+0.024] null 27%
```

## 2. Classic intraday strategies (same data)

Signal on a candle close, entry at the next candle open, stop first when a candle touches both levels, every trade closed at the
end of its session, max 3 trades per day per instrument (opening range: 1). "after costs" subtracts 0.1 x ATR per trade.

```
Opening range breakout (30 min)
   1:1 (stop = other side)    n  305 0.9/day | target hit 39.7% | closed in profit 54.8% | own exit  0.0% | session close 28.2% | R/trade +0.093 (Sep +0.046 Oct +0.163) | after costs +0.065 | positive on 8/10
   1:2 (stop = other side)    n  305 0.9/day | target hit 18.4% | closed in profit 44.9% | own exit  0.0% | session close 41.0% | R/trade +0.089 (Sep -0.008 Oct +0.232) | after costs +0.060 | positive on 5/10
VWAP 2-sigma band reversion
   1:1 (1 ATR stop)           n  912 2.8/day | target hit 51.5% | closed in profit 51.5% | own exit  0.0% | session close  0.2% | R/trade +0.033 (Sep +0.077 Oct -0.034) | after costs -0.067 | positive on 4/10
   1:2 (1 ATR stop)           n  905 2.8/day | target hit 34.4% | closed in profit 34.5% | own exit  0.0% | session close  0.3% | R/trade +0.035 (Sep +0.065 Oct -0.012) | after costs -0.065 | positive on 4/10
   own exit, 1 ATR stop       n  911 2.8/day | target hit  0.0% | closed in profit 49.9% | own exit 51.0% | session close  0.4% | R/trade +0.003 (Sep +0.031 Oct -0.039) | after costs -0.097 | positive on 4/10  [avg win +0.98R, avg loss -0.97R]
   own exit, 3 ATR stop       n  892 2.7/day | target hit  0.0% | closed in profit 67.2% | own exit 72.2% | session close  2.4% | R/trade -0.038 (Sep -0.004 Oct -0.091) | after costs -0.072 | positive on 3/10  [avg win +0.33R, avg loss -0.80R]
Bollinger Band (20, 2) reversion
   1:1 (1 ATR stop)           n  953 2.9/day | target hit 46.3% | closed in profit 46.5% | own exit  0.0% | session close  0.2% | R/trade -0.072 (Sep -0.094 Oct -0.038) | after costs -0.172 | positive on 2/10
   1:2 (1 ATR stop)           n  953 2.9/day | target hit 32.5% | closed in profit 33.3% | own exit  0.0% | session close  0.9% | R/trade -0.011 (Sep -0.041 Oct +0.035) | after costs -0.111 | positive on 2/10
   own exit, 1 ATR stop       n  953 2.9/day | target hit  0.0% | closed in profit 44.9% | own exit 46.9% | session close  0.5% | R/trade -0.023 (Sep -0.042 Oct +0.008) | after costs -0.123 | positive on 4/10  [avg win +1.12R, avg loss -0.96R]
   own exit, 3 ATR stop       n  945 2.9/day | target hit  0.0% | closed in profit 62.4% | own exit 76.2% | session close  1.8% | R/trade -0.039 (Sep -0.030 Oct -0.054) | after costs -0.073 | positive on 2/10  [avg win +0.33R, avg loss -0.65R]
RSI(2) pullback in EMA200 trend (Connors-style)
   1:1 (1 ATR stop)           n  886 2.7/day | target hit 49.4% | closed in profit 49.7% | own exit  0.0% | session close  0.2% | R/trade -0.008 (Sep +0.027 Oct -0.060) | after costs -0.108 | positive on 6/10
   1:2 (1 ATR stop)           n  870 2.7/day | target hit 34.4% | closed in profit 35.5% | own exit  0.0% | session close  1.3% | R/trade +0.053 (Sep +0.082 Oct +0.010) | after costs -0.047 | positive on 6/10
   own exit, 1 ATR stop       n  886 2.7/day | target hit  0.0% | closed in profit 53.6% | own exit 57.3% | session close  0.1% | R/trade +0.003 (Sep +0.021 Oct -0.025) | after costs -0.097 | positive on 7/10  [avg win +0.81R, avg loss -0.93R]
   own exit, 3 ATR stop       n  880 2.7/day | target hit  0.0% | closed in profit 63.9% | own exit 88.1% | session close  0.5% | R/trade -0.001 (Sep +0.010 Oct -0.015) | after costs -0.034 | positive on 5/10  [avg win +0.26R, avg loss -0.46R]
EMA 9/21 cross with EMA200 trend
   1:1 (1 ATR stop)           n  753 2.3/day | target hit 50.2% | closed in profit 50.7% | own exit  0.0% | session close  1.3% | R/trade +0.019 (Sep -0.029 Oct +0.097) | after costs -0.081 | positive on 5/10
   1:2 (1 ATR stop)           n  749 2.3/day | target hit 36.4% | closed in profit 37.4% | own exit  0.0% | session close  2.1% | R/trade +0.117 (Sep +0.064 Oct +0.203) | after costs +0.017 | positive on 8/10
   own exit, 1 ATR stop       n  753 2.3/day | target hit  0.0% | closed in profit 23.5% | own exit 27.6% | session close  4.8% | R/trade +0.234 (Sep +0.240 Oct +0.226) | after costs +0.134 | positive on 9/10  [avg win +4.05R, avg loss -0.94R]
   own exit, 3 ATR stop       n  748 2.3/day | target hit  0.0% | closed in profit 31.1% | own exit 81.7% | session close  7.0% | R/trade +0.092 (Sep +0.060 Oct +0.143) | after costs +0.059 | positive on 8/10  [avg win +1.47R, avg loss -0.53R]
Random entries (benchmark)
   1:1 (1 ATR stop)           n  834 2.5/day | target hit 50.2% | closed in profit 50.5% | own exit  0.0% | session close  0.4% | R/trade +0.009 (Sep -0.009 Oct +0.038) | after costs -0.091 | positive on 7/10
   1:2 (1 ATR stop)           n  824 2.5/day | target hit 33.3% | closed in profit 34.6% | own exit  0.0% | session close  1.9% | R/trade +0.023 (Sep -0.022 Oct +0.093) | after costs -0.077 | positive on 5/10
How a 70-80% win rate is usually made: a small target against a bigger stop
   target 0.5R vs 1R stop  Random entries           n  838  target hit 65.6%  R/trade -0.015  after costs -0.115
   target 0.5R vs 1R stop  RSI(2) pullback          n  887  target hit 63.7%  R/trade -0.042  after costs -0.142
   target 0.5R vs 1R stop  VWAP 2-sigma reversion   n  915  target hit 64.5%  R/trade -0.030  after costs -0.130
   target 0.3R vs 1R stop  Random entries           n  839  target hit 73.7%  R/trade -0.042  after costs -0.142
   target 0.3R vs 1R stop  RSI(2) pullback          n  888  target hit 73.2%  R/trade -0.048  after costs -0.148
   target 0.3R vs 1R stop  VWAP 2-sigma reversion   n  917  target hit 74.0%  R/trade -0.033  after costs -0.133
   target 0.2R vs 1R stop  Random entries           n  839  target hit 78.9%  R/trade -0.054  after costs -0.154
   target 0.2R vs 1R stop  RSI(2) pullback          n  888  target hit 78.7%  R/trade -0.055  after costs -0.155
   target 0.2R vs 1R stop  VWAP 2-sigma reversion   n  917  target hit 77.9%  R/trade -0.064  after costs -0.164
sessions in the data: 328
```

