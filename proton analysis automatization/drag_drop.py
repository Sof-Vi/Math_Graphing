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
    .*?
    (?P<mev>0x[0-9A-Fa-f]+)?
    .*?
    expected_data\s*=\s*(?P<expected>[^\s,]+)?
    .*?
    Read_Data\s*=\s*(?P<read>[^\s,]+)?
    .*?
    err\s*=\s*(?P<err>\d+)?
    """,
    re.VERBOSE | re.IGNORECASE,
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

    # Date
    dt = re.search(
        r"\d{4}-\d{2}-\d{2}\s+\d+:\d+:\d+\.\d+",
        line
    )

    if dt:
        row[0] = dt.group()

    # Event
    event = re.search(
        r"\[[^\]]+\]",
        line
    )

    if event:
        row[1] = event.group()

    # MEV (0x + 3–4 hex chars)
    mev = re.search(
        r"\b0x[0-9A-Fa-f]{3,4}\b",
        line
    )

    if mev:
        row[2] = mev.group()

    # Expected data
    expected = re.search(
        r"expected_data\s*=\s*([^\s,]+)",
        line,
        re.IGNORECASE
    )

    if expected:
        row[3] = expected.group(1)

    # Read data
    read = re.search(
        r"Read_Data\s*=\s*([^\s,]+)",
        line,
        re.IGNORECASE
    )

    if read:
        row[4] = read.group(1)

    # Error
    err = re.search(
        r"err\s*=\s*(\d+)",
        line,
        re.IGNORECASE
    )

    if err:
        row[5] = 1 if int(err.group(1)) > 0 else 0

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
            "python drag_drop.py [insert the path inside the repo to the txt file]"
        )

    else:

        create_excel(sys.argv[1])
