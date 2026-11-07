import pickle, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter as L

S = "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad"
d = pickle.load(open(f"{S}/gold/bestmonth_book.pkl", "rb"))
F = "Arial"
USD = '$#,##0;[Red]-$#,##0'
f_norm = Font(name=F, size=10)
f_bold = Font(name=F, size=10, bold=True)
f_title = Font(name=F, size=12, bold=True)
f_head = Font(name=F, size=10, bold=True, color="FFFFFF")
fill_head = PatternFill("solid", fgColor="1F3864")
fill_green = PatternFill("solid", fgColor="E2EFDA")
fill_red = PatternFill("solid", fgColor="C00000")
wrap = Alignment(wrap_text=True, vertical="top")
hwrap = Alignment(wrap_text=True, vertical="center", horizontal="center")

wb = Workbook()
ws = wb.active; ws.title = "Read me"
ws.column_dimensions["A"].width = 140
ws["A1"] = "Gold 2021-2026: settings with no losing month"
ws["A1"].font = Font(name=F, size=16, bold=True)
r = 3
for p in d["readme"]:
    c = ws.cell(r, 1, p); c.font = f_norm; c.alignment = wrap; r += 1
r += 1
ws.cell(r, 1, "Signal settings of the picks").font = f_bold; r += 1
for k, cfg in d["picks_cfg"].items():
    c = ws.cell(r, 1, f"{k}: " + ", ".join(f"{a} = {b}" for a, b in cfg.items()))
    c.font = f_norm; c.alignment = wrap; r += 1
c = ws.cell(r, 1, "Other settings at their defaults; M15-S9 is used WITHOUT its Asia kill zone; final exit TP4 = 2R")
c.font = Font(name=F, size=10, italic=True); c.alignment = wrap

def put_table(ws, r0, title, header, rows, fmts, zero_col):
    ws.cell(r0, 1, title).font = f_bold if r0 > 1 else f_title
    h = r0 + 2
    for j, t in enumerate(header, 1):
        c = ws.cell(h, j, t); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
    ws.row_dimensions[h].height = 45
    for i, row in enumerate(rows):
        for j, v in enumerate(row, 1):
            c = ws.cell(h + 1 + i, j, v); c.font = f_norm
            if fmts[j - 1]: c.number_format = fmts[j - 1]
            if row[zero_col] == 0: c.fill = fill_green
    return h, h + len(rows)

def widths(ws, header, first=34):
    for j in range(1, len(header) + 1):
        ws.column_dimensions[L(j)].width = first if j == 1 else 15

fm = [None]*20
for j in (5,6,9,10,13,14): fm[j] = "0"
for j in (7,8,11,12,15,16,17,18): fm[j] = USD
fm[19] = "0.0"
for rk in d["rankings"]:
    w = wb.create_sheet(rk["sheet"][:31])
    h, last = put_table(w, 1, rk["title"], d["header"], rk["rows"], fm, 13)
    widths(w, d["header"])
    for col, wd in ((2,22),(3,26),(4,16),(5,12)): w.column_dimensions[L(col)].width = wd
    w.freeze_panes = w.cell(h + 1, 1)
    w.auto_filter.ref = f"A{h}:{L(len(d['header']))}{last}"

w = wb.create_sheet("Robustness")
rf = [None, None, "0", "0", "0", USD, USD, USD, USD]
r = 1
for t in d["robust"]:
    h, last = put_table(w, r, t["title"], d["robust_header"], t["rows"], rf, 2)
    r = last + 3
widths(w, d["robust_header"], 18)
w.column_dimensions["A"].width = 18; w.column_dimensions["B"].width = 16

names = ["Best - month by month", "Runner-up - month by month",
         "Today best - month by month", "Today 2nd - month by month"]
mf = [None, "0", USD, USD, USD]
for nm, t in zip(names, d["months"]):
    w = wb.create_sheet(nm)
    w["A1"] = t["title"]; w["A1"].font = f_title
    h = 3
    for j, x in enumerate(d["months_header"], 1):
        c = w.cell(h, j, x); c.font = f_head; c.fill = fill_head; c.alignment = hwrap
    w.row_dimensions[h].height = 45
    for i, row in enumerate(t["rows"]):
        row = list(row)
        row[0] = datetime.datetime.strptime(row[0], "%Y-%m").strftime("%b %Y")
        for j, v in enumerate(row, 1):
            c = w.cell(h + 1 + i, j, v); c.font = f_norm
            if mf[j-1]: c.number_format = mf[j-1]
    a, b = h + 1, h + len(t["rows"])
    w.conditional_formatting.add(f"C{a}:C{b}", CellIsRule(operator="lessThan", formula=["0"],
                                 fill=fill_red, font=Font(name=F, size=10, color="FFFFFF")))
    s = b + 2
    rngB, rngC, rngD, rngE = (f"{c}{a}:{c}{b}" for c in "BCDE")
    summ = [("Total", f"=SUM({rngB})", f"=SUM({rngC})", None),
            ("Average month", None, f"=AVERAGE({rngC})", None),
            ("Months in profit", None, f'=COUNTIF({rngC},">0")', "0"),
            ("Months in loss", None, f'=COUNTIF({rngC},"<0")', "0"),
            ("Worst month", None, f"=MIN({rngC})", None),
            ("Best month", None, f"=MAX({rngC})", None),
            ("Deepest fall", None, None, f"=MAX({rngD})"),
            ("Biggest trade", None, None, f"=MAX({rngE})")]
    for i, (lab, fb, fc, fe) in enumerate(summ):
        rr = s + i
        w.cell(rr, 1, lab).font = f_bold
        if fb: c = w.cell(rr, 2, fb); c.font = f_bold; c.number_format = "0"
        if fc:
            c = w.cell(rr, 3, fc); c.font = f_bold
            c.number_format = "0" if lab.startswith("Months") else USD
        if fe: c = w.cell(rr, 4 if lab == "Deepest fall" else 5, fe); c.font = f_bold; c.number_format = USD
    w.column_dimensions["A"].width = 20
    for col in "BCDE": w.column_dimensions[col].width = 18
    w.freeze_panes = w.cell(h + 1, 1)

wb.save(f"{S}/Gold_No_Losing_Month.xlsx")
print("saved")
