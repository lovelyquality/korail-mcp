"""Inspect headers and row counts for all 6 local data files."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import openpyxl
import csv
from pathlib import Path

DATA = Path(r"E:\AI\MCP\m-freight\data")

print("=== XLSX: freight_codes.xlsx ===")
wb = openpyxl.load_workbook(DATA / "freight_codes.xlsx", read_only=True)
ws = wb.active
n = 0
for i, row in enumerate(ws.iter_rows(values_only=True)):
    if i < 5:
        print(row)
    n += 1
print(f"total rows: {n}")
wb.close()

for name in ["consignment_fee.csv", "consignment_fee_per_wagon.csv",
             "facility_basic.csv", "facility_scale.csv", "facility_photo.csv"]:
    print(f"\n=== CSV: {name} ===")
    with open(DATA / name, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)
    print("header:", rows[0])
    print(f"data rows: {len(rows) - 1}")
    if len(rows) > 1:
        print("sample row 1:", rows[1])
