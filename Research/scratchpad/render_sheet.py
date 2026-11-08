"""render one sheet of a workbook to PNG pages: python3 -I render_sheet.py BOOK SHEET OUTDIR"""
import sys, subprocess, os, glob
from openpyxl import load_workbook
book, sheet, out = sys.argv[1], sys.argv[2], sys.argv[3]
wb = load_workbook(book)
for n in wb.sheetnames:
    if n != sheet: del wb[n]
ws = wb[sheet]
ws.page_setup.orientation = "landscape"
ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
tag = sheet.replace(" ", "_")
x = os.path.join(out, tag + ".xlsx"); wb.save(x)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", out, x], check=True, capture_output=True)
for f in glob.glob(os.path.join(out, tag + "-*.png")): os.remove(f)
subprocess.run(["pdftoppm", "-r", "110", "-png", os.path.join(out, tag + ".pdf"), os.path.join(out, tag)], check=True)
print(sorted(glob.glob(os.path.join(out, tag + "-*.png"))))
