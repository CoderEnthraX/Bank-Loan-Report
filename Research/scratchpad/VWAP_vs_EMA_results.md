# VWAP vs EMA 50 / 100 / 200 - all results

Same engine for every row (displacement + retest, 1.8 ATR stop); only the trend reference changes. 10 instruments, 31 Aug - 21 Oct 2026, every row starts at bar 200.
1:1 = exit at 1R (break-even win rate 50%). 1:2 = exit at 2R (break-even win rate 33.3%). R = average result per trade. Sep / Oct = average R per trade at 1:2 in each period.
"Better on" = instruments where the 1:2 average beats the VWAP model. "Range" = 95% bootstrap range of the 1:2 difference vs the VWAP model (whole days resampled); if it includes 0 the difference may be luck.
"(skipped run invisibly)" = setups failing the EMA rule are not shown or traded but still run in the background, so a later, worse signal does not take their place. "vs random" = how often randomly skipping the same number of VWAP trades did worse (95% would be convincing).

## Replace VWAP with one EMA (or nothing)

| Setup | 1:1 win % | 1:1 R | 1:2 trades | 1:2 win % | 1:2 R | Sep / Oct | Better on | Total R (1:2) | Range vs VWAP | vs random |
|---|---|---|---|---|---|---|---|---|---|---|
| VWAP side (the model) | 54.1 | +0.082 | 1154 | 39.0 | +0.170 | +0.16 / +0.19 | - | +196 | - | - |
| No side filter | 51.0 | +0.021 | 1251 | 35.5 | +0.065 | +0.07 / +0.06 | 1/10 | +81 | -0.168 to -0.048 | - |
| EMA50 side (close vs EMA50 + slope) | 52.1 | +0.041 | 1169 | 37.5 | +0.124 | +0.12 / +0.13 | 2/10 | +145 | -0.095 to +0.004 | - |
| EMA100 side (close vs EMA100 + slope) | 54.1 | +0.082 | 1127 | 38.3 | +0.150 | +0.14 / +0.16 | 6/10 | +169 | -0.067 to +0.025 | - |
| EMA200 side (close vs EMA200 + slope) | 53.4 | +0.067 | 1095 | 37.6 | +0.129 | +0.13 / +0.13 | 3/10 | +141 | -0.101 to +0.023 | - |
| EMA50 side, position only | 52.3 | +0.045 | 1213 | 36.9 | +0.106 | +0.13 / +0.07 | 3/10 | +128 | -0.117 to -0.011 | - |
| EMA100 side, position only | 53.1 | +0.062 | 1164 | 37.0 | +0.111 | +0.11 / +0.10 | 3/10 | +129 | -0.111 to -0.012 | - |
| EMA200 side, position only | 53.6 | +0.071 | 1128 | 38.0 | +0.141 | +0.13 / +0.15 | 3/10 | +159 | -0.092 to +0.033 | - |

## Replace VWAP with two EMAs together

| Setup | 1:1 win % | 1:1 R | 1:2 trades | 1:2 win % | 1:2 R | Sep / Oct | Better on | Total R (1:2) | Range vs VWAP | vs random |
|---|---|---|---|---|---|---|---|---|---|---|
| EMA50>EMA100, close>EMA50 | 53.2 | +0.064 | 987 | 36.4 | +0.091 | +0.10 / +0.08 | 3/10 | +90 | -0.147 to -0.005 | - |
| EMA100>EMA200, close>EMA100 | 51.1 | +0.022 | 926 | 36.1 | +0.082 | +0.09 / +0.06 | 3/10 | +76 | -0.165 to -0.006 | - |
| EMA50>EMA200, close>EMA50 | 51.7 | +0.034 | 963 | 36.3 | +0.090 | +0.10 / +0.07 | 4/10 | +87 | -0.161 to -0.004 | - |
| EMA50>100>200, close>EMA50 | 51.1 | +0.021 | 831 | 35.5 | +0.065 | +0.08 / +0.05 | 1/10 | +54 | -0.192 to -0.025 | - |

## VWAP and an EMA together

| Setup | 1:1 win % | 1:1 R | 1:2 trades | 1:2 win % | 1:2 R | Sep / Oct | Better on | Total R (1:2) | Range vs VWAP | vs random |
|---|---|---|---|---|---|---|---|---|---|---|
| VWAP + close>EMA200 | 53.6 | +0.073 | 1084 | 38.5 | +0.154 | +0.15 / +0.16 | 5/10 | +167 | -0.061 to +0.033 | - |
| VWAP + close>EMA200 (skipped run invisibly) | 53.8 | +0.076 | 963 | 39.6 | +0.187 | +0.18 / +0.19 | 5/10 | +180 | -0.021 to +0.051 | 82% |
| VWAP + close>EMA100 | 54.2 | +0.084 | 1124 | 39.1 | +0.172 | +0.17 / +0.18 | 3/10 | +193 | -0.029 to +0.034 | - |
| VWAP + close>EMA100 (skipped run invisibly) | 53.8 | +0.075 | 1079 | 39.6 | +0.187 | +0.18 / +0.20 | 7/10 | +202 | -0.004 to +0.039 | 93% |
| VWAP + close>EMA50 | 54.2 | +0.084 | 1138 | 39.2 | +0.176 | +0.17 / +0.19 | 4/10 | +200 | -0.015 to +0.027 | - |
| VWAP + close>EMA50 (skipped run invisibly) | 53.9 | +0.077 | 1127 | 39.3 | +0.179 | +0.16 / +0.20 | 6/10 | +202 | -0.002 to +0.021 | 88% |
| VWAP + EMA50>EMA200 | 52.1 | +0.042 | 918 | 36.4 | +0.092 | +0.10 / +0.09 | 4/10 | +84 | -0.149 to +0.001 | - |
| VWAP + EMA50>EMA200 (skipped run invisibly) | 53.0 | +0.060 | 711 | 39.2 | +0.177 | +0.21 / +0.12 | 5/10 | +126 | -0.055 to +0.074 | 58% |
| VWAP + EMA50>EMA100 | 52.7 | +0.055 | 965 | 36.1 | +0.082 | +0.09 / +0.07 | 4/10 | +79 | -0.154 to -0.020 | - |
| VWAP + EMA50>EMA100 (skipped run invisibly) | 53.0 | +0.060 | 761 | 38.4 | +0.151 | +0.16 / +0.14 | 3/10 | +115 | -0.077 to +0.040 | 27% |
| VWAP + EMA100>EMA200 | 51.1 | +0.023 | 876 | 36.0 | +0.079 | +0.10 / +0.04 | 4/10 | +69 | -0.163 to -0.009 | - |
| VWAP + EMA100>EMA200 (skipped run invisibly) | 52.5 | +0.051 | 673 | 38.6 | +0.159 | +0.19 / +0.10 | 5/10 | +107 | -0.079 to +0.060 | 37% |

## Your idea: above EMA200, pull back near EMA50, then the buy signal

| Setup | 1:1 win % | 1:1 R | 1:2 trades | 1:2 win % | 1:2 R | Sep / Oct | Better on | Total R (1:2) | Range vs VWAP | vs random |
|---|---|---|---|---|---|---|---|---|---|---|
| pullback to EMA50 (6 bars, 0.0 ATR) in EMA200 trend, no VWAP | 47.2 | -0.056 | 529 | 34.2 | +0.026 | +0.06 / -0.03 | 3/10 | +14 | -0.256 to -0.027 | - |
| pullback to EMA50 (6 bars, 0.0 ATR) in EMA200 trend, + VWAP | 48.5 | -0.030 | 445 | 35.5 | +0.065 | +0.11 / -0.01 | 3/10 | +29 | -0.224 to +0.017 | - |
| pullback to EMA50 (6 bars, 0.0 ATR) in EMA200 trend, + VWAP (skipped run invisibly) | 47.4 | -0.053 | 294 | 38.1 | +0.143 | +0.17 / +0.10 | 4/10 | +42 | -0.163 to +0.118 | 33% |
| pullback to EMA50 (12 bars, 0.0 ATR) in EMA200 trend, no VWAP | 49.0 | -0.021 | 655 | 35.3 | +0.058 | +0.11 / -0.03 | 2/10 | +38 | -0.215 to -0.018 | - |
| pullback to EMA50 (12 bars, 0.0 ATR) in EMA200 trend, + VWAP | 50.6 | +0.013 | 573 | 36.5 | +0.094 | +0.15 / +0.00 | 5/10 | +54 | -0.183 to +0.034 | - |
| pullback to EMA50 (12 bars, 0.0 ATR) in EMA200 trend, + VWAP (skipped run invisibly) | 50.6 | +0.012 | 401 | 38.7 | +0.160 | +0.23 / +0.04 | 5/10 | +64 | -0.113 to +0.102 | 40% |
| pullback to EMA50 (6 bars, 0.5 ATR) in EMA200 trend, no VWAP | 48.0 | -0.040 | 640 | 34.7 | +0.041 | +0.10 / -0.06 | 2/10 | +26 | -0.234 to -0.025 | - |
| pullback to EMA50 (6 bars, 0.5 ATR) in EMA200 trend, + VWAP | 49.3 | -0.013 | 557 | 35.9 | +0.077 | +0.14 / -0.03 | 3/10 | +43 | -0.198 to +0.012 | - |
| pullback to EMA50 (6 bars, 0.5 ATR) in EMA200 trend, + VWAP (skipped run invisibly) | 49.5 | -0.010 | 384 | 38.3 | +0.148 | +0.20 / +0.05 | 3/10 | +57 | -0.131 to +0.093 | 34% |
| pullback to EMA50 (12 bars, 0.5 ATR) in EMA200 trend, no VWAP | 49.2 | -0.017 | 744 | 36.4 | +0.093 | +0.15 / +0.00 | 3/10 | +69 | -0.170 to +0.017 | - |
| pullback to EMA50 (12 bars, 0.5 ATR) in EMA200 trend, + VWAP | 50.7 | +0.013 | 666 | 37.5 | +0.126 | +0.18 / +0.03 | 6/10 | +84 | -0.137 to +0.055 | - |
| pullback to EMA50 (12 bars, 0.5 ATR) in EMA200 trend, + VWAP (skipped run invisibly) | 51.4 | +0.028 | 486 | 39.7 | +0.191 | +0.25 / +0.08 | 6/10 | +93 | -0.067 to +0.110 | 66% |

## Standalone EMA strategies (no VWAP displacement model)

| Setup | 1:1 win % | 1:1 R | 1:2 trades | 1:2 win % | 1:2 R | Sep / Oct | Better on | Total R (1:2) | Range vs VWAP | vs random |
|---|---|---|---|---|---|---|---|---|---|---|
| EMA50 bounce in EMA200 trend (standalone) | 51.2 | +0.025 | 1067 | 35.1 | +0.052 | +0.09 / -0.02 | 1/10 | +55 | -0.237 to -0.004 | - |
| EMA50 bounce in EMA200 trend + VWAP side (standalone) | 51.2 | +0.024 | 865 | 34.5 | +0.034 | +0.09 / -0.06 | 2/10 | +29 | -0.252 to -0.024 | - |
| EMA50/EMA200 cross (standalone) | 54.3 | +0.087 | 331 | 35.6 | +0.069 | +0.08 / +0.05 | 2/10 | +23 | -0.256 to +0.059 | - |
| EMA50/EMA100 cross (standalone) | 52.9 | +0.058 | 495 | 38.2 | +0.145 | +0.16 / +0.11 | 5/10 | +72 | -0.168 to +0.121 | - |
| EMA20/EMA50 cross (standalone) | 52.8 | +0.056 | 823 | 38.8 | +0.163 | +0.21 / +0.09 | 7/10 | +134 | -0.118 to +0.106 | - |
| EMA20/EMA50 cross + VWAP side (standalone) | 53.3 | +0.066 | 693 | 38.4 | +0.152 | +0.23 / +0.03 | 5/10 | +105 | -0.142 to +0.111 | - |

Standalone strategies enter at the signal candle close with a plain 1.8 ATR stop (the engine's market mode), so their fills are approximate.
