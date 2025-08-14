# Smartsheet_Column_#s
# README.md

## Smartsheet Column IDs

Get a quick inventory of your Smartsheet columns with their IDs, titles, types, and position index. Drop-in script. No drama.

### What this does

* Connects to a Smartsheet sheet
* Lists each column with: position index, title, ID, and type
* Outputs in a pretty table by default, with optional CSV or JSON

### Why you might care

You need the assigned Smartsheet column numbers and IDs for API work, formulas, or automations. This gives you the source of truth in seconds.

---

## Quick start

### 1. Prereqs

* Python 3.9+
* A Smartsheet API access token
* Your target Sheet ID

### 2. Install

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 3. Configure

Set these as environment variables or pass as flags.

```bash
# Option A: environment variables
export SMARTSHEET_ACCESS_TOKEN="YOUR_ACCESS_TOKEN"
export SMARTSHEET_SHEET_ID=1234567890123456

# Option B: flags when running
python get_columns.py --access-token YOUR_ACCESS_TOKEN --sheet-id 1234567890123456
```

### 4. Run

```bash
python get_columns.py            # reads env vars
python get_columns.py --format csv > columns.csv
python get_columns.py --format json > columns.json
```

### Example output

```
Columns for sheet "Customer Onboarding":
#  Title                 ID            Type
1  Primary Column        123456789012  TEXT_NUMBER
2  Status                223344556677  PICKLIST
3  Due Date              998877665544  DATE
```

---

## Flags

```text
--access-token TEXT   Overrides SMARTSHEET_ACCESS_TOKEN
--sheet-id INT        Overrides SMARTSHEET_SHEET_ID
--format {table,csv,json}  Default table
--timeout INT         HTTP timeout in seconds. Default 30
--debug               Verbose logging
```

---

## How to find your Sheet ID

1. Open the sheet in Smartsheet
2. Copy the long numeric ID from the URL

## How to create an API token

1. In Smartsheet, go to Account > Apps & Integrations > API Access
2. Create a new access token and copy it
3. Store it securely. Never commit tokens to Git

---

## Security posture

* Use environment variables or a secrets manager
* .gitignore prevents accidental commits of .env files and caches
* Do not paste real tokens in issues or screenshots

---

## Troubleshooting

* 401 Unauthorized: bad or expired token
* 404 Not Found: wrong sheet ID or no access
* Proxy or firewall: set standard env vars like HTTPS\_PROXY if needed

---

## License

MIT. See LICENSE.

## Contributing

Issues and PRs are welcome. Keep it lean and readable.

---

# get\_columns.py

```python
#!/usr/bin/env python3
"""
Smartsheet Column IDs - list columns with position index, title, ID, and type.

Usage
-----
Environment variables:
  SMARTSHEET_ACCESS_TOKEN, SMARTSHEET_SHEET_ID

Or pass flags:
  python get_columns.py --access-token TOKEN --sheet-id 123456...

Output formats: table, csv, json
"""
import argparse
import csv
import json
import os
import sys
import time

import smartsheet


def parse_args():
    p = argparse.ArgumentParser(description="List Smartsheet columns with IDs and types")
    p.add_argument("--access-token", dest="token", help="Smartsheet API access token")
    p.add_argument("--sheet-id", dest="sheet_id", type=int, help="Smartsheet sheet ID")
    p.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")
    p.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    p.add_argument("--debug", action="store_true", help="Enable verbose logging")
    return p.parse_args()


def get_config(args):
    token = args.token or os.getenv("SMARTSHEET_ACCESS_TOKEN")
    sheet_id = args.sheet_id or os.getenv("SMARTSHEET_SHEET_ID")
    if sheet_id is not None and not isinstance(sheet_id, int):
        try:
            sheet_id = int(sheet_id)
        except ValueError:
            sys.exit("SMARTSHEET_SHEET_ID must be an integer")
    if not token:
        sys.exit("Missing access token. Set SMARTSHEET_ACCESS_TOKEN or use --access-token")
    if not sheet_id:
        sys.exit("Missing sheet ID. Set SMARTSHEET_SHEET_ID or use --sheet-id")
    return token, sheet_id


def fetch_columns(token, sheet_id, timeout, debug=False):
    client = smartsheet.Smartsheet(token)
    client.errors_as_exceptions(True)
    # The SDK uses a global timeout on the underlying HTTP client. We simulate with retry if needed.
    # For simplicity, we do a single call with a basic retry.
    last_err = None
    for attempt in range(1, 3):
        try:
            sheet = client.Sheets.get_sheet(sheet_id)
            return sheet
        except Exception as e:
            last_err = e
            if debug:
                sys.stderr.write(f"Attempt {attempt} failed: {e}\n")
            time.sleep(0.5)
    raise last_err


def to_rows(sheet):
    rows = []
    for idx, col in enumerate(sheet.columns, start=1):
        rows.append({
            "position": idx,
            "title": getattr(col, "title", None),
            "id": getattr(col, "id", None),
            "type": getattr(col, "type", None),
            "primary": getattr(col, "primary", False),
        })
    return rows


def print_table(sheet_name, rows):
    print(f'Columns for sheet "{sheet_name}":')
    headers = ["#", "Title", "ID", "Type"]
    widths = [max(len(str(r["position"])) for r in rows + [{"position": headers[0]}]),
              max(len(str(r["title"])) for r in rows + [{"title": headers[1]}]),
              max(len(str(r["id"])) for r in rows + [{"id": headers[2]}]),
              max(len(str(r["type"])) for r in rows + [{"type": headers[3]}])]
    fmt = f"{{:>{widths[0]}}}  {{:<{widths[1]}}}  {{:<{widths[2]}}}  {{:<{widths[3]}}}"
    print(fmt.format(*headers))
    for r in rows:
        print(fmt.format(r["position"], r["title"], r["id"], r["type"]))


def print_csv(rows):
    writer = csv.DictWriter(sys.stdout, fieldnames=["position", "title", "id", "type", "primary"])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)


def print_json(rows):
    json.dump(rows, sys.stdout, indent=2)
    print()


def main():
    args = parse_args()
    token, sheet_id = get_config(args)
    try:
        sheet = fetch_columns(token, sheet_id, args.timeout, args.debug)
    except Exception as e:
        sys.exit(f"Error fetching sheet: {e}")

    rows = to_rows(sheet)
    if args.format == "table":
        print_table(getattr(sheet, "name", str(sheet_id)), rows)
    elif args.format == "csv":
        print_csv(rows)
    else:
        print_json(rows)


if __name__ == "__main__":
    main()
```

---

# requirements.txt

```
smartsheet-python-sdk
```

---

# .gitignore

```
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.venv/
venv/
.env
.env.*
*.env

# OS
.DS_Store
Thumbs.db

# Tooling
.idea/
.vscode/
.mypy_cache/
.pytest_cache/
```

---

# LICENSE

Copyright (c) 2025 Eduardo Rodriguez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files to deal in the Software
without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and or sell copies of the
Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

---

# .env.example

```
SMARTSHEET_ACCESS_TOKEN=your_token_here
SMARTSHEET_SHEET_ID=1234567890123456
```

