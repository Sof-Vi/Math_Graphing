# Python 3.13
# Code was made using gpt 

import re
import sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo


OUTPUT_SUFFIX = "_organized.xlsx"

pattern = re.compile(
    r"""
    (?P<datetime>\d{4}-\d{2}-\d{2}\s+\d+:\d+:\d+\.\d+)
    ,\s*
    (?P<event>\[.*?\])
    \s*
    (?P<mev>0x[0-9A-Fa-f]+)?
    .*?
    (?:expected_data=(?P<expected>\d+))?
    .*?
    (?:Read_Data=(?P<read>\d+))?
    .*?
    (?:err=(?P<err>\d+))?
    """,
    re.VERBOSE,
)

HEADERS = [
    "Date & Time",
    "Event",
    "MEV",
    "Expected data",
    "Data Read",
    "Errors (0=No errors,1=Errors)"
]


def parse_line(line):

    row = ["", "", "", "", "", 0]

    match = pattern.search(line)

    if match:

        row[0] = match.group("datetime")
        row[1] = match.group("event")
        row[2] = match.group("mev") or ""
        row[3] = match.group("expected") or ""
        row[4] = match.group("read") or ""

        err = match.group("err")

        if err:
            row[5] = 1 if int(err) > 0 else 0

        return row

    # fallback for START/DONE/WATCHDOG

    parts = line.split(",", 1)

    if len(parts) == 2:
        row[0] = parts[0].strip()
        row[1] = parts[1].strip()

    return row


def autofit(ws):

    for col in ws.columns:

        max_len = 0
        letter = get_column_letter(col[0].column)

        for cell in col:

            try:
                length = len(str(cell.value))

                if length > max_len:
                    max_len = length

            except:
                pass

        ws.column_dimensions[letter].width = min(max_len + 4, 60)


def create_excel(txt_path):

    txt_path = Path(txt_path).expanduser().resolve()

    if not txt_path.exists():
        raise FileNotFoundError(f"File not found after resolving path: {txt_path}")

    wb = Workbook()
    ws = wb.active
    ws.title = "FRAM Data"

    ws.append(HEADERS)

    with open(
            txt_path,
            "r",
            encoding="utf-8",
            errors="ignore"
    ) as f:

        for line in f:

            line = line.strip()

            if line:
                ws.append(parse_line(line))

    # Freeze header
    ws.freeze_panes = "A2"

    # Excel Table + Filters
    last_row = ws.max_row
    last_col = ws.max_column

    table = Table(
            displayName="FRAM_Table",
            ref=f"A1:{get_column_letter(last_col)}{last_row}"
    )

    style = TableStyleInfo(
            name="TableStyleMedium2",
            showRowStripes=True,
            showColumnStripes=False
    )

    table.tableStyleInfo = style
    ws.add_table(table)

    # Autofit columns
    autofit(ws)

    output = txt_path.stem + OUTPUT_SUFFIX
    output_path = txt_path.parent / output

    wb.save(output_path)

    print(f"\nDone!")
    print(output_path)


if __name__ == "__main__":

    if len(sys.argv) < 2:

        print(
            "\nDrag TXT file into terminal:\n"
            "python drag_drop.py your_log.txt"
        )

    else:

        create_excel(sys.argv[1])
