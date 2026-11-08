"""Gold_No_Losing_Month.xlsx, version 2: the same results (bestmonth_book.pkl) plus an explanation block at the top of every sheet, a
'Strategies explained' sheet (every S-name, its timeframe, what its label means, every setting with its TradingView and EA name) and a
'Settings explained' sheet (time filters, loss-recovery rules, hard caps, monthly lock and the v4.2 settings). Input titles and EA labels are read
from the v4.2 files so the names are exact."""
import pickle, datetime, re, math, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter as L

S = "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad"
REPO = "/home/user/Bank-Loan-Report"
d = pickle.load(open(f"{S}/gold/bestmonth_book.pkl", "rb"))
MO = pickle.load(open(f"{S}/gold/monthly.pkl", "rb"))
STRATS = MO["strategies"]

# ---- exact names from the v4.2 files
pine = open(f"{REPO}/TradingView/Auction_Retest_Strategy.pine", encoding="utf8").read()
GROUPS = dict(re.findall(r'^(GRP_\w+)\s*=\s*"([^"]+)"', pine, re.M))
TV = {}
for m in re.finditer(r'^(\w+)\s*=\s*input\.\w+\((.*)$', pine, re.M):
    name, rest = m.group(1), m.group(2)
    t = re.match(r'\s*[^,]+,\s*"([^"]*)"', rest)
    g = re.search(r'group\s*=\s*(GRP_\w+)', rest)
    TV[name] = (t.group(1) if t else "", GROUPS.get(g.group(1), "") if g else "")
ea = open(f"{REPO}/MetaTrader5/AuctionRetestEA.mq5", encoding="utf8").read()
EA = {m.group(1): m.group(3).strip() for m in re.finditer(r'^input\s+\w+\s+(Inp\w+)\s*=\s*([^;]+);\s*//\s*(.*)$', ea, re.M)}
def tv(name, title=None):
    assert name in TV, name
    t, g = TV[name]
    return g, title or t
def ean(name):
    assert name in EA, name
    lab = EA[name].lstrip(". ").strip()
    return f"{name}  (MT5 shows: {lab})"

F = "Arial"
USD = '$#,##0;[Red]-$#,##0'
f_norm = Font(name=F, size=10); f_bold = Font(name=F, size=10, bold=True); f_title = Font(name=F, size=14, bold=True)
f_sub = Font(name=F, size=11, bold=True, color="1F3864"); f_head = Font(name=F, size=10, bold=True, color="FFFFFF")
fill_head = PatternFill("solid", fgColor="1F3864"); fill_green = PatternFill("solid", fgColor="E2EFDA"); fill_red = PatternFill("solid", fgColor="C00000")
fill_note = PatternFill("solid", fgColor="FFF8E1"); fill_sec = PatternFill("solid", fgColor="DDEBF7"); fill_new = PatternFill("solid", fgColor="FCE4D6")
wrap = Alignment(wrap_text=True, vertical="top"); hwrap = Alignment(wrap_text=True, vertical="center", horizontal="center")

def width_chars(ws, c1, c2):
    return sum((ws.column_dimensions[L(j)].width or 9) for j in range(c1, c2 + 1))
def wrap_lines(text, cw):
    """lines a wrapped cell needs: greedy word wrap, capitals and bold-ish text counted wider"""
    n = 0
    for p in str(text).split("\n"):
        cur, lines = 0.0, 1
        for w in p.split(" "):
            wl = sum(1.3 if ch.isupper() else 1.0 for ch in w)
            if cur and cur + 1 + wl > cw: lines += 1; cur = wl
            else: cur = cur + (1 if cur else 0) + wl
        n += lines
    return n
def fit(ws, r, ncols):
    n = 1
    for j in range(1, ncols + 1):
        v = ws.cell(r, j).value
        if v is None or v == "": continue
        cw = max(4, (ws.column_dimensions[L(j)].width or 9) * 1.0)
        n = max(n, wrap_lines(v, cw))
    ws.row_dimensions[r].height = 14.5 * n + 3
def note(ws, r, text, ncols, bold=False, fill=fill_note, font=None):
    """one wrapped line of explanation merged across the table width; row height from the text length"""
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
    c = ws.cell(r, 1, text); c.font = font or (f_bold if bold else f_norm); c.alignment = wrap
    for j in range(1, ncols + 1): ws.cell(r, j).fill = fill
    cpl = max(30, width_chars(ws, 1, ncols) * 1.15)
    lines = sum(max(1, math.ceil(len(p) / cpl)) for p in text.split("\n"))
    ws.row_dimensions[r].height = 14.5 * lines + 3
    return r + 1
def explain(ws, ncols, title, what, how, example=None):
    """the block at the top of a sheet: title, what it is, how to read it (and an example); returns the next free row"""
    ws.cell(1, 1, title).font = f_title
    r = 2
    r = note(ws, r, "WHAT THIS SHEET IS", ncols, font=f_sub, fill=fill_sec)
    for p in what: r = note(ws, r, p, ncols)
    r = note(ws, r, "HOW TO READ IT", ncols, font=f_sub, fill=fill_sec)
    for p in how: r = note(ws, r, "• " + p, ncols)
    if example:
        r = note(ws, r, "EXAMPLE", ncols, font=f_sub, fill=fill_sec)
        for p in example: r = note(ws, r, p, ncols)
    return r + 1
def put_table(ws, r0, title, header, rows, fmts, zero_col):
    ws.cell(r0, 1, title).font = f_bold
    h = r0 + 1
    for j, t in enumerate(header, 1):
        c = ws.cell(h, j, t); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
    ws.row_dimensions[h].height = 45
    for i, row in enumerate(rows):
        for j, v in enumerate(row, 1):
            c = ws.cell(h + 1 + i, j, v); c.font = f_norm
            if fmts[j - 1]: c.number_format = fmts[j - 1]
            if zero_col is not None and row[zero_col] == 0: c.fill = fill_green
    return h, h + len(rows)

wb = Workbook()
# ================================================================ Read me
ws = wb.active; ws.title = "Read me"
ws.column_dimensions["A"].width = 150
ws["A1"] = "Gold 2021-2026: settings with no losing month"; ws["A1"].font = Font(name=F, size=16, bold=True)
SHEETS = [
    ("Read me", "this page: what the workbook is, how to use it, the key results and the new settings."),
    ("Strategies explained", "what M1-S3, M15-S9 ... mean, what 'Most profit', 'Shortest losing streak' ... mean, and every setting of every strategy with its exact name in TradingView and in the EA."),
    ("Settings explained", "every value in the columns Time filters, Loss recovery, Hard cap and Monthly lock, where to set it, and the three v4.2 settings (monthly lock, profit lock, monthly restart)."),
    ("Calendar today", "the best settings for calendar months using only settings that already existed before v4.2 (no monthly lock)."),
    ("Calendar with lock", "the same with the monthly lock and the monthly restart: the main result of the study."),
    ("Mid-month today / Mid-month with lock", "the same two rankings with months counted from the 15th to the 14th (a check that the result does not depend on where a month starts)."),
    ("Robustness", "the two best settings with every hard cap and every lock amount: does the result depend on the exact numbers?"),
    ("Stress test", "the strongest settings re-run with extra costs and with 15th-14th months: which ones still have no losing month?"),
    ("... - month by month (5 sheets)", "one row per month for one chosen setting: trades, result, deepest fall, biggest trade."),
]
r = 3
def rm(text, font=f_norm, fill=None):
    global r
    c = ws.cell(r, 1, text); c.font = font; c.alignment = wrap
    if fill: c.fill = fill
    ws.row_dimensions[r].height = 14.5 * max(1, math.ceil(len(text) / 165)) + 3
    r += 1
rm("WHAT THIS WORKBOOK IS", f_sub, fill_sec)
rm("A search for settings with which every single month ends in profit. Each month from January 2021 to September 2026 was tested on its own, "
   "as if you started that month with a fresh $10,000 account and a fresh loss-recovery state, $50 base risk, the real FxPro gold spread as the cost "
   "and the 1:100 leverage limit. Settings were chosen on 2021-23 only and then checked on 2024-26, so the 24-26 columns show how a choice held up on "
   "months it was not chosen on.")
rm("HOW TO USE IT", f_sub, fill_sec)
for t in ("1. Read the key results below, then open 'Calendar with lock': each row is one complete setting (a strategy + a time filter + a loss-recovery rule + a hard cap + a lock). Green rows had no losing month at all.",
          "2. Look up the row's strategy (e.g. M15-S9) in 'Strategies explained' and set it up on that timeframe's chart: first the 'base settings' listed there, then the strategy's own changes.",
          "3. Set the money columns (Loss recovery, Hard cap, Monthly lock) with 'Settings explained', which gives the exact place of every setting in TradingView and in the EA.",
          "4. Check the setting's months in its '... - month by month' sheet if it has one, and its behaviour under stress in 'Robustness' and 'Stress test'.",
          "5. Backtest it yourself before trading it: these are results on past data and do not promise future results."):
    rm(t)
rm("THE SHEETS", f_sub, fill_sec)
for n, t in SHEETS: rm(f"{n}: {t}")
rm("KEY RESULTS", f_sub, fill_sec)
STALE = "Two new settings are needed to trade it"
assert sum(p.startswith(STALE) for p in d["readme"]) == 1
for p in d["readme"]:
    if p.startswith(STALE):                           # written before v4.2: both settings exist now
        p = ("Two settings are needed to trade it: the monthly lock (\"stop for the month once it is up $X\") and restarting the loss recovery on "
             "the 1st of each month. Both are now in the v4.2 strategy and EA (see below; they are off by default, so switch them on).")
    rm(p)
rm("NEW SETTINGS IN v4.2 (TradingView strategy and MT5 EA, group MONTHLY PROFIT LOCK; all off by default)", f_sub, fill_new)
for t in (f"Stop for the month once it is up $X - TradingView: '{tv('mLockOn')[1]}' + amount box; EA: InpMLockOn + InpMLockAmt. "
          "The study's 'Monthly lock +$X' column: once this month's closed profit reaches $X, no new trades until the 1st.",
          f"Restart the loss recovery on the 1st - TradingView: '{tv('mRestart')[1]}'; EA: InpMRestart. The study started every month like this (switch it on together with the lock).",
          f"Lock profit (your idea, not part of the study) - TradingView: '{tv('pLockOn')[1]}' with the amount and the lock %; EA: InpPLockOn, InpPLockAt, InpPLockPct. "
          "Once this month's closed profit reaches the amount, the lock % of the month's highest profit is locked (up $500 with 20% = $100, rising with new highs); "
          "if the month's profit falls back to the locked level, no new trades until the 1st."):
    rm("• " + t)
rm("Details: sheet 'Settings explained'.", Font(name=F, size=10, italic=True))
r += 1
rm("Signal settings of the two picks (changes from the original settings; full list in 'Strategies explained')", f_bold)
for k, cfg in d["picks_cfg"].items():
    rm(f"{k}: " + ", ".join(f"{a} = {b}" for a, b in cfg.items()))
rm("Other settings at their original values; M15-S9 is used WITHOUT its Asia kill zone ('no time filter'); final exit TP4 = 2R.", Font(name=F, size=10, italic=True))

# ================================================================ Strategies explained
ws = wb.create_sheet("Strategies explained")
for col, w in zip("ABCDEFGH", (11, 10, 24, 24, 26, 30, 30, 50)): ws.column_dimensions[col].width = w
NC = 8
r = explain(ws, NC, "Strategies explained: what M1-S3, M15-S9 ... are and how to set them up", [
    "The 19 strategies of the earlier gold study that made money with a fixed $50 risk. Every strategy = the original signal settings plus a few changes, "
    "chosen for one goal ('Most profit', 'Simplest' ...). This sheet lists every change with its exact name in TradingView and in the MT5 EA."],
    ["The name has two parts. M1 / M5 / M15 / H1 = the chart timeframe the strategy is made for: 1-minute, 5-minute, 15-minute or 1-hour candles. Load the "
     "strategy or the EA on a chart of that timeframe.",
     "S1, S2 ... = the strategy's number in that timeframe's list of the earlier study. Only the ones that made money at a fixed $50 are used here, so some numbers are "
     "missing (e.g. there is no M15-S2 or M5-S9).",
     "Section 1 below explains the goal words. Section 2 lists the BASE SETTINGS that every strategy starts from: they differ from the v4.2 defaults "
     "(v4.2's defaults are your own trading settings), so set these first. Section 3 lists each strategy's own changes, one row per setting.",
     "Columns of section 3: TradingView: group = the group heading in the strategy's (or indicator's) Settings > Inputs; TradingView: setting = the input's name; "
     "Value = what to set; EA input = the input's name in the EA (MT5 shows the label in brackets in the Inputs tab); EA value = what to set there."],
    ["M15-S7 'Every year positive' on a 15-minute chart: set the base settings, then Signal Break Lookback = 8, Half Stop = 1.2, Stop Distance = 4, and tick "
     "'When TP3 Hits, Move Stop To (R)' with 1.0."])
r = note(ws, r, "1. WHAT THE GOAL WORDS MEAN (what each strategy was picked for in the earlier study; 'both halves' = 2021-23 and 2024-26)", NC, font=f_sub, fill=fill_sec)
GOALS = [("Most profit", "The best result per trade after the spread in BOTH halves (ranked by the weaker half). The main recommendation of each timeframe."),
         ("Shortest losing streak", "The fewest losses in a row, while keeping a fair profit."),
         ("Shortest streak ind (indicator only)", "The same, without a partial close, so the TradingView indicator shows exactly the same trades and results."),
         ("Most trades (a day)", "The most trades while still profitable in both halves."),
         ("Every year +", "Profitable in every one of the 6 years 2021-2026 (the best of those)."),
         ("Simplest", "The fewest settings changed from the original ones that is still profitable."),
         ("Smoothest", "The best profit for its deepest fall (total R divided by the largest fall from a peak), among the 25 strongest settings."),
         ("Asia only", "The best setting that trades only in the Asia kill zone (05:30-09:30 India time).")]
for g, t in GOALS: r = note(ws, r, f"{g}: {t}", NC)
r += 1
r = note(ws, r, "2. BASE SETTINGS: every strategy starts from these (the original settings the study used). Set them first, then section 3.", NC, font=f_sub, fill=fill_sec)
hdr = ["Applies to", "", "Setting", "TradingView: group", "TradingView: setting", "Value (study)", "EA input", "EA value (study)"]
for j, t in enumerate(hdr, 1):
    c = ws.cell(r, j, t); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
ws.row_dimensions[r].height = 32; r += 1
BASE = [
    ("Final exit", "exitAt", "TP4 (v4.2 default: TP1)", "InpExitAt", "TP4"),
    ("Max fills a day", "maxFills", "5 (v4.2 default: 10)", "InpMaxFills", "5"),
    ("Half-stop cap", "halfCap", "off (v4.2 default: on)", "InpHalfCap", "false"),
    ("Days filter", "dayOn", "off = every day (v4.2: Tue-Thu)", "InpDayOn", "false"),
    ("Hours filter", "hoursOn", "off (v4.2: 06:00-23:00), unless section 3 lists hours", "InpHoursOn", "false"),
    ("Kill zones", "kzOn", "off (v4.2: on), unless section 3 lists kill zones", "InpKzOn", "false"),
    ("Kill zones follow summer time", "kzAuto", "on", "InpKzAuto", "true"),
    ("Value of the TP3 stop move", "mv3On|the value box of: When TP3 Hits, Move Stop To (R)", "1.0 (v4.2 default: 0); only used when section 3 ticks it", "InpMv3R", "1.0"),
    ("Value of the TP2 stop move", "mv2On|the value box of: When TP2 Hits, Move Stop To (R)", "0.6; only used when section 3 ticks it", "InpMv2R", "0.6"),
    ("Force-close / weekend close", "fcOn", "off (the study had none; v4.2: on)", "InpFcOn / InpWeekendOn", "false / false"),
    ("Daily news window", "dNewsOn", "off (the study had none; v4.2: 17:45-18:15)", "InpDNewsOn", "false"),
    ("Costs", "commLot", "the study counted the real spread and no commission, no earn-back (v4.2: spread 0.16 + $7 commission, earn-back on)", "InpCommLot / InpEarnBack", "0 / false"),
    ("Everything else", "", "the original values: Stop Distance 1.8, Half Stop 0.9, Session VWAP (hlc3), Entry Model, targets 0.6 / 1 / 1.5 / 2 R, filters off", "", "")]
for lab, key, val, ek, ev in BASE:
    g, t = (tv(key.split("|")[0], key.split("|")[1]) if "|" in key else tv(key)) if key else ("", "")
    row = ["all", "", lab, g, t, val, ean(ek.split(" / ")[0]) + (" / " + ek.split(" / ")[1] if " / " in ek else "") if ek else "", ev]
    for j, v in enumerate(row, 1):
        c = ws.cell(r, j, v); c.font = f_norm; c.alignment = wrap
    fit(ws, r, 8); r += 1
r += 1
r = note(ws, r, "3. EACH STRATEGY'S OWN CHANGES (on top of the base settings). 'as designed' in the other sheets = with its kill zones / hours below; 'no time filter' = without them.", NC, font=f_sub, fill=fill_sec)
hdr = ["Strategy", "Chart", "Picked for", "Setting", "TradingView: group", "TradingView: setting", "Value", "EA input + value"]
for j, t in enumerate(hdr, 1):
    c = ws.cell(r, j, t); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
ws.row_dimensions[r].height = 32; r += 1
CHART = {"M1": "1-minute", "M5": "5-minute", "M15": "15-minute", "H1": "1-hour"}
KZN = ("Asia 05:30-09:30", "London 11:30-14:30", "New York 16:30-19:30", "London Close 19:30-21:30")
def changes(cfg, exitR):
    out = []
    def add(lab, key, val, eav, title=None):
        g, t = tv(key, title); out.append((lab, g, t, val, eav))
    for k in sorted(cfg):
        v = cfg[k]
        if k == "stopAtr": add("Stop distance", "stopAtr", f"{v:g} x ATR", f"InpStopAtr = {v:g}")
        elif k == "cooldownBars": add("Cooldown after an exit", "cooldownBars", f"{v} bars", f"InpCooldown = {v}")
        elif k == "dispAtr": add("Min displacement range", "dispAtr", f"{v:g} x ATR", f"InpDispAtr = {v:g}")
        elif k == "dispBodyPct": add("Min displacement body", "dispBodyPct", f"{v:g} %", f"InpBodyPct = {v:g}")
        elif k == "momLen": add("Momentum lookback", "momLen", f"{v} bars (first box)", f"InpMomLen = {v}")
        elif k == "structLen": add("Structure lookback", "structLen", f"{v} bars", f"InpStructLen = {v}")
        elif k == "brkLen": add("Signal break lookback", "brkLen", f"{v} bars", f"InpBrkLen = {v}")
        elif k == "entryLen": add("Entry level lookback", "entryLen", f"{v} bars", f"InpEntryLen = {v}")
        elif k == "halfStopAtr": add("Half stop", "halfStopAtr", f"{v:g} x ATR (first box)", f"InpHalfStopAtr = {v:g}")
        elif k == "slopeBars": add("VWAP slope bars", "slopeBars", f"{v}", f"InpSlopeBars = {v}")
        elif k == "skipSunday": add("Skip Sunday open", "skipSunday", "off" if not v else "on", f"InpSkipSunday = {'true' if v else 'false'}")
        elif k == "vwAnchorG": add("VWAP anchor", "vwapAnchor", "Month" if v == "month" else str(v), "InpVwapAnchor = Month")
        elif k == "entryMode": add("Entry price", "entryMode", "Market (next bar open)", "InpEntryMode = Market (next bar open)")
        elif k == "tp4R": add("TP4 target", "tp1R", f"4th box = {v:g} R", f"InpTp4R = {v:g}")
        elif k == "mv2On": add("Stop move at TP2", "mv2On", "tick it, value 0.6", "InpMv2On = true, InpMv2R = 0.6")
        elif k == "mv3On": add("Stop move at TP3", "mv3On", "tick it, value 1.0", "InpMv3On = true, InpMv3R = 1.0")
        elif k == "chopOn": add("Choppy-session filter", "chopOn", f"tick it, value {cfg['chopMax']:g}", f"InpChopOn = true, InpChopMax = {cfg['chopMax']:g}")
        elif k == "emaOn": add("1h EMA20 speed filter", "emaOn", f"tick it, value {cfg['emaMax']:g}", f"InpEmaOn = true, InpEmaMax = {cfg['emaMax']:g}")
        elif k == "noChase": add("Don't chase filter", "noChase", f"tick it, value {cfg['noChaseSig']:g}", f"InpNoChase = true, InpNoChaseSig = {cfg['noChaseSig']:g}")
        elif k == "kzOn":
            on = [n for n, b in zip(KZN, cfg["kz"]) if b]
            add("Kill zones (time filter)", "kzOn", "tick it; tick only: " + ", ".join(on),
                "InpKzOn = true; " + ", ".join(f"{e} = {'true' if b else 'false'}" for e, b in zip(("InpKzAsia", "InpKzLon", "InpKzNy", "InpKzLc"), cfg["kz"])))
        elif k == "hoursOn":
            a, b = cfg["hoursSess"]
            add("Trading hours (time filter)", "hoursOn", f"tick it, {a // 100:02d}:{a % 100:02d} - {b // 100:02d}:{b % 100:02d}",
                f"InpHoursOn = true, InpStartH = {a // 100}, InpStartM = {a % 100}, InpEndH = {b // 100}, InpEndM = {b % 100}")
        elif k in ("chopMax", "emaMax", "noChaseSig", "kz", "hoursSess"): continue
        else: raise SystemExit("unmapped setting " + k)
    add("Final exit", "exitAt", f"TP4 (= {exitR:g} R)", "InpExitAt = TP4")
    return out
cur_tf = None
for st_ in STRATS:
    if st_["tf"] != cur_tf:
        cur_tf = st_["tf"]
        r = note(ws, r, f"{cur_tf}: {CHART[cur_tf]} chart", NC, bold=True, fill=fill_sec)
    rows = changes(st_["cfg"], st_["exitR"])
    for i, (lab, g, t, val, eav) in enumerate(rows):
        vals = [st_["key"] if i == 0 else "", CHART[st_["tf"]] if i == 0 else "", st_["name"] if i == 0 else "", lab, g, t, val, eav]
        for j, v in enumerate(vals, 1):
            c = ws.cell(r, j, v); c.font = f_bold if (i == 0 and j <= 3) else f_norm; c.alignment = wrap
        fit(ws, r, 8)
        r += 1
    r += 1

# ================================================================ Settings explained
ws = wb.create_sheet("Settings explained")
for col, w in zip("ABCD", (30, 62, 54, 52)): ws.column_dimensions[col].width = w
NC = 4
r = explain(ws, NC, "Settings explained: the money and time columns of this workbook", [
    "Every value that appears in the columns Time filters, Loss recovery, Hard cap and Monthly lock of the other sheets, what it does, and where you set it "
    "in the TradingView strategy and in the MT5 EA. At the end: the three settings added in v4.2."],
    ["Column A = the value as it appears in the sheets. B = what it does. C = TradingView: open the strategy's Settings > Inputs, find the group (in capitals) and the setting. "
     "D = the EA: the input's name (MT5's Inputs tab shows the label in brackets).",
     "All money results used $50 as the base risk."])
def section(title, rows, fill=fill_sec):
    global r
    r = note(ws, r, title, NC, font=f_sub, fill=fill)
    for j, t in enumerate(["In the sheets", "What it does", "TradingView", "MT5 EA"], 1):
        c = ws.cell(r, j, t); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
    r += 1
    for row in rows:
        for j, v in enumerate(row, 1):
            c = ws.cell(r, j, v); c.font = f_bold if j == 1 else f_norm; c.alignment = wrap
        ws.row_dimensions[r].height = 14.5 * max(1, max(math.ceil(len(str(v)) / (w * 1.1)) for v, w in zip(row, (30, 62, 54, 52)))) + 3
        r += 1
    r += 1
GR = GROUPS
section("TIME FILTERS COLUMN", [
    ("as designed", "The strategy with its own time filter, if it has one: M1 strategies = London Close kill zone only, M5 = 18:30-22:30 only, M15-S9 = Asia kill zone only "
     "(see 'Strategies explained'); the others have none.", f"{GR['GRP_W']}: as listed for the strategy", "as listed for the strategy"),
    ("no time filter", "The strategy without its time filter: every day, all hours.", f"{GR['GRP_W']}: Trade Only On The Ticked Days, Trade Only Between and Trade Only In Kill Zones all off",
     "InpDayOn = false, InpHoursOn = false, InpKzOn = false"),
    ("File 2 setup", "Your own setup: Tuesday, Wednesday, Thursday; kill zones Asia + London + New York; daily news window 17:45-18:15 India time with no new trades 60 minutes before.",
     f"{GR['GRP_W']}: ticked days Tue, Wed, Thu; kill zones Asia, London, New York. {GR['GRP_X']}: Daily News Window 17:45-18:15, No New Trades Before News 60",
     "InpDayOn = true (Tue, Wed, Thu); InpKzOn = true, InpKzLc = false; InpDNewsOn = true, 17:45, 30 min; InpNewsPre = 60")])
g = GR["GRP_L"]
def rec(lab, what, tvopt, eaopt, extra_tv="", extra_ea=""):
    return (lab, what, f"{g}: Loss Recovery = {tvopt}" + (f"; {extra_tv}" if extra_tv else ""), f"InpRec = {eaopt}" + (f"; {extra_ea}" if extra_ea else ""))
section("LOSS RECOVERY COLUMN (how the risk changes after losses)", [
    rec("Fixed $50", "Every trade risks the base $50.", "Off", "Off"),
    rec("Recover all on the next trade", "Next risk = base + every $ lost and not yet won back.", "Recover all losses on the next trade", "Recover all losses on the next trade"),
    rec("Recover over 3 trades", "Next risk = base + losses / 3.", "Recover losses over N trades", "Recover losses over N trades", "N Trades (Over N) = 3", "InpRecN = 3"),
    rec("Recover 50% of losses", "Next risk = base + 50% of the losses.", "Recover a % of losses per trade", "Recover a % of losses per trade", "% Of Losses = 50", "InpRecPct = 50"),
    rec("Martingale x2", "Next risk = base x 2 for every loss in a row (50, 100, 200 ...); back to the base after a win.", "Martingale (multiply after each loss)",
        "Martingale (multiply after each loss)", "Multiplier = 2", "InpRecMult = 2"),
    rec("Exact recovery at final TP", "Next risk = base + losses / final target R, so a win at the final target wins back the losses plus a normal win.", "Exact recovery at final TP", "Exact recovery at final TP"),
    rec("Fibonacci", "Next risk = base x 1, 1, 2, 3, 5, 8 ... by losses in a row.", "Fibonacci (1,1,2,3,5... x base)", "Fibonacci"),
    rec("D'Alembert", "Risk in units of the base: +1 unit after a loss, -1 after a win (minimum 1).", "D'Alembert (+1 unit per loss, -1 per win)", "D'Alembert"),
    rec("Labouchere", "A list 1-2-3: risk = base x (first + last); a loss adds that sum to the list, a win removes both ends; an empty list starts again.",
        "Labouchere (cancellation 1-2-3)", "Labouchere (cancellation 1-2-3)"),
    rec("Oscar's Grind", "+1 unit after each win until the cycle is +1 base in profit; unchanged after a loss.", "Oscar's Grind (+1 unit per win until +1 base)", "Oscar's Grind"),
    rec("Paroli", "Base x 2 for every win in a row, back to the base after 3 wins or any loss.", "Paroli (double after wins, reset after N)", "Paroli", "Wins Before Reset (Paroli) = 3", "InpParN = 3"),
    rec("Reverse D'Alembert", "+1 unit after a win, -1 after a loss.", "Reverse D'Alembert (+1 unit per win, -1 per loss)", "Reverse D'Alembert"),
    rec("Delayed recovery", "Base until 2 losses in a row, then base + losses / 3.", "Delayed recovery (after N losses, over N trades)", "Delayed recovery",
        "Losses Before Recovery Starts = 2, N Trades = 3", "InpDelayN = 2, InpRecN = 3"),
    rec("Rule C split 1 / Rule C split 3", "Carries the losses: next risk = max(base, losses not yet won back / split).", "Rule C: carry the losses", "Rule C: carry the losses",
        "Split The Loss Over This Many Trades = 1 or 3", "InpCSplit = 1 or 3"),
    rec("Crooks A", "Trades 1 and 2 of a cycle risk the base; from trade 3 every other trade is a recovery trade risking max(base, loss to win back / final target R).",
        "Crooks A (base, base, then recovery every 2nd trade)", "Crooks A"),
    rec("Crooks B split 2", "Like Crooks A, but the recovery trade goes for the loss / 2.", "Crooks B (Crooks A with the loss split over N trades)", "Crooks B", "Split = 2", "InpCSplit = 2"),
    rec("Crooks C", "Base until a trade wins; the trade after a win is the recovery trade (sized to win back the whole loss); a losing recovery trade -> base until the next win.",
        "Crooks C (base until a win, then one recovery trade)", "Crooks C"),
    rec("Crooks D", "Base, base, recovery: every 3rd trade is a recovery trade.", "Crooks D (base, base, recovery: every 3rd trade)", "Crooks D"),
    rec("Crooks C over 2 wins", "Crooks C, but the loss is won back over 2 winning recovery trades (half each).", "Crooks C", "Crooks C",
        "tick Crooks C: Win The Loss Back Over N Wins, N = 2", "InpCrkCnOn = true, InpCrkCn = 2"),
    rec("Crooks C forget after 2 / after 3", "Crooks C; after 2 (or 3) losing recovery trades in a row the loss is forgotten and a new cycle starts at the base.", "Crooks C", "Crooks C",
        "Crooks C: After N Losing Recovery Trades In A Row = Forget the loss; N = 2 or 3", "InpCrkPr = Forget the loss, InpCrkPrN = 2 or 3"),
    rec("Crooks C 50% forget 2", "Crooks C; recovery trades go for 50% of the loss, and after 2 losing recovery trades the loss is forgotten.", "Crooks C", "Crooks C",
        "Crooks C rule = Go for a % of the loss, forget it after N; % = 50; N = 2", "InpCrkPr = Go for a % of the loss, InpCrkPrPct = 50, InpCrkPrN = 2"),
    rec("Crooks C wait 2 wins N2", "Crooks C; after 2 losing recovery trades, base trades until 2 wins in a row, then the trade after the next loss-and-win is the recovery trade.",
        "Crooks C", "Crooks C", "Crooks C rule = Wait for M wins in a row, then a loss and a win; N = 2, M = 2", "InpCrkPr = Wait for M wins, InpCrkPrN = 2, InpCrkPrM = 2"),
    rec("Crooks C skip 3 days N2", "Crooks C; after 2 losing recovery trades, no trades for the rest of that day and 3 trading days.", "Crooks C", "Crooks C",
        "Crooks C rule = Skip D trading days; N = 2, D = 3", "InpCrkPr = Skip D trading days, InpCrkPrN = 2, InpCrkPrD = 3")])
gR = GR["GRP_R"]
section("HARD CAP COLUMN (the largest $ one trade may risk)", [
    ("no cap", "No limit: a recovery rule can make a trade as big as the leverage allows.", f"{gR}: Hard Cap: Max Loss Per Trade ($) off", "InpCapOn = false"),
    ("cap $500 clamp", "No trade risks more than $500; a bigger recovery trade is cut to $500 and the rest of the loss stays to be won back later.",
     f"{gR}: Hard Cap on, 500; If The Risk Would Exceed The Cap = Clamp risk to the cap", "InpCapOn = true, InpHardCap = 500, InpCapAction = Clamp"),
    ("cap $500 start again / cap $250 start again", "When a trade would risk more than the cap, the losses are forgotten and the trade risks the base again.",
     f"{gR}: Hard Cap on, 500 or 250; If The Risk Would Exceed The Cap = Start again from the base risk", "InpCapOn = true, InpHardCap = 500 or 250, InpCapAction = Start again")])
gM = GR["GRP_ML"]
section("MONTHLY LOCK COLUMN", [
    ("none", "No monthly lock: the strategy trades every signal all month.", f"{gM}: Stop For The Month Once It Is Up ($) off", "InpMLockOn = false"),
    ("+$50 / +$100 / +$150 / +$250 / +$500", "Once this month's closed profit reaches that amount, no new trades until the 1st of next month. The study also restarted the loss "
     "recovery on the 1st of every month: switch on both settings to reproduce it.", f"{gM}: Stop For The Month Once It Is Up ($) on + the amount; "
     f"and Restart The Loss Recovery On The 1st Of Each Month on", "InpMLockOn = true, InpMLockAmt = the amount; InpMRestart = true")])
section("NEW IN v4.2 (TradingView strategy and MT5 EA; all off by default; the strategy and the EA do exactly the same)", [
    (tv("mLockOn")[1], "When this calendar month's closed profit (time zone of DAYS AND HOURS; costs included) reaches the amount, no new trades until the 1st of next month. "
     "A trade already open runs to its exit. The table shows the month's profit.", f"{gM}: tick it and enter the amount (default 150)", ean("InpMLockOn") + "; " + ean("InpMLockAmt")),
    (tv("mRestart")[1], "On the 1st of each month the loss recovery starts again from the base risk, like the hard cap's Start again (the loss to win back, losing runs, the "
     "Labouchere list, Rule C's carried losses and the Crooks C rule state are forgotten). With a trade of the old month still open, right after it closes.",
     f"{gM}: tick it", ean("InpMRestart")),
    (tv("pLockOn")[1], "Your idea (not tested in this study). Once this month's closed profit reaches the amount, the lock % of the month's highest closed profit is locked: "
     "up $500 with 20% = $100 locked, rising with every new high (up $800 = $160). If the month's closed profit falls back to the locked level, no new trades until the 1st. "
     "It is checked when a trade closes, so one big losing trade can still end below the locked level.",
     f"{gM}: tick it, then the amount (default 500) and the lock % (default 20)", ean("InpPLockOn") + "; " + ean("InpPLockAt") + "; " + ean("InpPLockPct"))], fill=fill_new)
section("MONEY BASICS OF THE STUDY (the same for every row)", [
    ("Base risk", "$50 per trade.", f"{gR}: Base Risk Per Trade ($) = 50", "InpBaseRisk = 50"),
    ("Account", "Every month starts with a fresh $10,000 and a fresh loss-recovery state.", "Properties: Initial capital 10000; Restart The Loss Recovery On The 1st on", "your account; InpMRestart = true"),
    ("Costs", "The real FxPro gold spread at each trade; no commission.", "Spread and Commission (see the base settings)", "InpSpread / InpCommLot"),
    ("Leverage", "Position value at most 100 x the account (1:100).", f"{gR}: Leverage = 100", "InpLeverage = 100")])

# ================================================================ rankings
HOW_RANK = [
    "Each row is one complete setting: Strategy (signal settings) = the strategy (see 'Strategies explained'); Time filters = as designed / no time filter / File 2 setup; "
    "Loss recovery, Hard cap and Monthly lock = the money settings (see 'Settings explained').",
    "21-23 columns = the choice period (36 months, the ranking uses only these); 24-26 columns = the check period (33 months, not used to choose); All = all 69 months.",
    "For each period: losing months (fewer is better), months tested, worst month $ (the worst single month) and profit $ (all those months added up).",
    "Biggest trade risk $ = the most one trade risked. Deepest fall inside a month $ = the largest drop from a high inside any month, before the month recovered.",
    "Signals per month = trades per month on average. Green rows = no losing month in all 69 months. Use the arrows in the header row to sort or filter."]
RANK_TXT = {
    "Calendar today": ("Calendar months (1st to the last day) with the settings that existed before v4.2: no monthly lock. Only settings whose biggest trade risked at most $500. "
                       "The 25 best, ranked on 2021-23."),
    "Calendar with lock": ("Calendar months with the monthly lock ('stop for the month once it is up $X') and the monthly restart of the loss recovery: the main result. "
                           "Only settings whose biggest trade risked at most $500. The 25 best, ranked on 2021-23. The top row is the 'Best' of the Read me."),
    "Mid-month today": ("The same as 'Calendar today', but every month runs from the 15th to the 14th of the next month: a check that the result does not depend on where a "
                        "month starts."),
    "Mid-month with lock": "The same as 'Calendar with lock', with months from the 15th to the 14th of the next month."}
fm = [None] * 20
for j in (5, 6, 9, 10, 13, 14): fm[j] = "0"
for j in (7, 8, 11, 12, 15, 16, 17, 18): fm[j] = USD
fm[19] = "0.0"
for rk in d["rankings"]:
    w = wb.create_sheet(rk["sheet"][:31])
    for j in range(1, 21): w.column_dimensions[L(j)].width = 13
    for col, wd in ((1, 30), (2, 16), (3, 26), (4, 18), (5, 11)): w.column_dimensions[L(col)].width = wd
    top = rk["rows"][0]
    ex = [f"Top row: {top[0]}, {top[1]}, {top[2]}, {top[3]}, monthly lock {top[4]}: {top[13]} losing months of {top[14]}, worst month ${top[15]:,.0f}, "
          f"total ${top[16]:,.0f}; its biggest trade risked ${top[17]:,.0f}."]
    r0 = explain(w, 20, rk["sheet"], [RANK_TXT[rk["sheet"]]], HOW_RANK, ex)
    h, last = put_table(w, r0, rk["title"], d["header"], rk["rows"], fm, 13)
    w.auto_filter.ref = f"A{h}:{L(len(d['header']))}{last}"

# ================================================================ Robustness
w = wb.create_sheet("Robustness")
for j in range(1, 10): w.column_dimensions[L(j)].width = 16
w.column_dimensions["A"].width = 22
r0 = explain(w, 9, "Robustness", [
    "The two best settings (the winner M15-S9 and the runner-up M15-S7, see the table titles) re-run with every hard cap (no cap, $500 start again, $250 start again, "
    "$500 clamp) and every lock amount (none, +$50, +$100, +$150, +$250, +$500), on calendar months. It shows whether the result depends on the exact numbers chosen."],
    ["One row = one hard cap + one lock. Read down the 'All losing months (of 69)' column: green rows (0) had no losing month.",
     "21-23 / 24-26 losing = the losing months in each half. Worst month $ and Profit $ over all 69 months. Biggest trade risk $ = the most one trade risked; "
     "Deepest fall inside a month $ = the largest drop from a high inside any month.",
     "Rows with 'none' as the lock show what the setting does without the new monthly lock."],
    ["Winner with no cap and no lock: 13 losing months; with no cap and a +$50 lock: 0 losing months. The lock is what removes the losing months."])
rf = [None, None, "0", "0", "0", USD, USD, USD, USD]
r = r0
for t in d["robust"]:
    h, last = put_table(w, r, t["title"], d["robust_header"], t["rows"], rf, 2)
    r = last + 3

# ================================================================ Stress test
w = wb.create_sheet("Stress test")
for j in range(1, 17): w.column_dimensions[L(j)].width = 12
for col, wd in ((1, 26), (2, 16), (3, 26), (4, 18), (5, 10)): w.column_dimensions[L(col)].width = wd
r0 = explain(w, 16, "Stress test", [
    "The 383 settings with at most 1 losing calendar month (with the lock, trades up to $500) were re-run in 6 harder cases: calendar months and 15th-14th months, each with "
    "normal costs and with an extra cost of 0.02R and 0.05R per trade (like slippage or commission; 0.02R is about $1 on a $50 trade). The 40 that held up best."],
    ["Columns F-K = losing months in each of the 6 cases. Column L = the losing months of all 6 cases added up: green (0) = no losing month in any case, the most robust.",
     "Worst month in the 6 cases $ = the worst single month seen in any case. Calendar / 15th-14th profit $ = the total profit with normal costs. "
     "Deepest fall inside a month $ = the largest drop from a high inside any month.",
     "A setting that has 0 only in the first column but losing months with extra costs is fragile: a little slippage can turn a month negative."],
    [f"Top row: {d['stress'][0][0]}, {d['stress'][0][2]}, {d['stress'][0][3]}, lock {d['stress'][0][4]}: 0 losing months in all 6 cases, but only "
     f"${d['stress'][0][13]:,.0f} profit in 69 months."])
sf = [None, None, None, None, None, "0", "0", "0", "0", "0", "0", "0", USD, USD, USD, USD]
h, last = put_table(w, r0, d["stress_title"], d["stress_header"], d["stress"], sf, 11)

# ================================================================ month by month
names = d.get("months_names")
mf = [None, "0", USD, USD, USD]
for nm, t in zip(names, d["months"]):
    w = wb.create_sheet(nm[:31])
    w.column_dimensions["A"].width = 22
    for col in "BCDE": w.column_dimensions[col].width = 20
    for col in "FGH": w.column_dimensions[col].width = 18
    r0 = explain(w, 8, nm, [f"Every month of one setting: {t['title']}. Each month on its own with a fresh $10,000 and a fresh loss-recovery state."],
                 ["Month = the calendar month (India time). Trades taken = trades opened that month. Result of the month $ = the month's profit or loss; red = a losing month.",
                  "Deepest fall inside the month $ = how far the month went down from its high before it ended; Biggest trade risk $ = the most one trade risked that month.",
                  "The totals below the table are formulas: total, average month, months in profit / in loss, worst and best month, deepest fall, biggest trade."])
    h = r0
    for j, x in enumerate(d["months_header"], 1):
        c = w.cell(h, j, x); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
    w.row_dimensions[h].height = 45
    for i, row in enumerate(t["rows"]):
        row = list(row)
        row[0] = datetime.datetime.strptime(row[0], "%Y-%m").strftime("%b %Y")
        for j, v in enumerate(row, 1):
            c = w.cell(h + 1 + i, j, v); c.font = f_norm
            if mf[j - 1]: c.number_format = mf[j - 1]
    a, b = h + 1, h + len(t["rows"])
    w.conditional_formatting.add(f"C{a}:C{b}", CellIsRule(operator="lessThan", formula=["0"], fill=fill_red, font=Font(name=F, size=10, color="FFFFFF")))
    s = b + 2
    rngB, rngC, rngD, rngE = (f"{c}{a}:{c}{b}" for c in "BCDE")
    summ = [("Total", f"=SUM({rngB})", f"=SUM({rngC})", None), ("Average month", None, f"=AVERAGE({rngC})", None),
            ("Months in profit", None, f'=COUNTIF({rngC},">0")', None), ("Months in loss", None, f'=COUNTIF({rngC},"<0")', None),
            ("Worst month", None, f"=MIN({rngC})", None), ("Best month", None, f"=MAX({rngC})", None),
            ("Deepest fall", None, None, f"=MAX({rngD})"), ("Biggest trade", None, None, f"=MAX({rngE})")]
    for i, (lab, fb, fc, fe) in enumerate(summ):
        rr = s + i
        w.cell(rr, 1, lab).font = f_bold
        if fb: c = w.cell(rr, 2, fb); c.font = f_bold; c.number_format = "0"
        if fc:
            c = w.cell(rr, 3, fc); c.font = f_bold
            c.number_format = "0" if lab.startswith("Months") else USD
        if fe: c = w.cell(rr, 4 if lab == "Deepest fall" else 5, fe); c.font = f_bold; c.number_format = USD

out = f"{S}/Gold_No_Losing_Month.xlsx"
wb.save(out)
print("saved", out, "| sheets:", wb.sheetnames)
