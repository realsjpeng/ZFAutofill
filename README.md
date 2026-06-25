# ZFAutofill

A small desktop tool that automates score entry on the **正方教务系统**
(Zhengfang Educational Administration System) and other systems that use the
same DOM structure. It embeds the grade-entry page in a Qt WebEngine view,
reads scores from a local file (`.txt` / `.xls` / `.xlsx`) and injects them
into the web form via JavaScript.

> **How generic is it?** The script targets the iframe name `zhuti`, which
> is the standard container in 正方教务系统. As long as your school's
> grade-entry form uses the same `iframe[name="zhuti"]` plus the
> `DataGrid1:_ctl{n}:ps` / `:qm` input names, this tool works. No other
> code changes needed.

<table>
  <tr>
    <td width="50%"><img src="media/screenshot1.jpg" alt="Main window" width="100%"></td>
    <td width="50%"><img src="media/screenshot2.jpg" alt="Open txt/xls/xlsx file" width="100%"></td>
  </tr>
  <tr>
    <td align="center"><em>Main window</em></td>
    <td align="center"><em>Open txt / xls / xlsx file</em></td>
  </tr>
  <tr>
    <td width="50%"><img src="media/screenshot3.jpg" alt="Excel column picker dialog" width="100%"></td>
    <td width="50%"><img src="media/screenshot4.jpg" alt="Auto-filled scores" width="100%"></td>
  </tr>
  <tr>
    <td align="center"><em>Excel column picker dialog</em></td>
    <td align="center"><em>Scores auto-filled</em></td>
  </tr>
</table>

---

<video controls width="100%">
  <source src="https://raw.githubusercontent.com/realsjpeng/ZFAutofill/refs/heads/main/media/demo.mp4" type="video/mp4">
</video>

*Demo recording using the local demo site — shows navigating to the mock page, selecting an `.xlsx` file, and auto-filling scores into the form. · BGM: "Technology" by The_Mountain — Pixabay*

---

## Features

- **Embedded browser** — defaults to the unified authentication page of **Jinling Institute of Technology (金陵科技学院)**. The URL shown in the address bar is stored in `config.json` as `base_url`. **Change it to your own school's 正方教务系统 grade-entry page** before using.
- **Address bar + Go button** — edit the URL and hit *Go* (or press `Enter`).
  The new address is written to `config.json` immediately, so the next launch
  opens the same page. Effectively a one-slot "history".
- **Open button** (top-left) — pick a score file:
  - `.txt` — two whitespace-separated columns per line, e.g. `91.0  86.3`.
  - `.xls` / `.xlsx` — a dialog lets you choose the worksheet, the two columns
    and a row range (e.g. `B3:B36`). Selections are remembered for next time.
- **Rounded Run button** at the bottom — fills the scores into the page and
  triggers the page's save button. Has a subtle green glow and a play icon.
- **Auto-fill scores** — reads regular scores and final scores from a local file and injects them into the web form automatically.
- **i18n** — UI strings follow the system locale (English / 简体中文).

## Run from source

1. Install Python 3.9 or newer.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python main.py
   ```
4. Log in inside the embedded browser.

## Usage

1. **Log in** to the Zhengfang Educational Administration System in the embedded browser.
2. **Navigate** to the grade-entry page — you should see the score table with regular score / final score columns.
3. **Open a score file** via the **Open** button at the **top-left corner** of the toolbar (supports `.txt`, `.xls`, `.xlsx`).
4. **Click the Run button** at the **bottom-right corner** to start autofill.
5. The program reads the file and fills the web form automatically.

## Input file format

**TXT** — one student per line, two whitespace-separated columns
(regular score, then final score):

```
91.0   86.3
91.0   83.0
83.0   91.0
50.6   35.0
```

**XLS / XLSX** — open the file via the **Open** button. The dialog shows a
preview, then you pick:

- the worksheet
- the two columns (e.g. `B` and `C`)
- the row range (e.g. start `3`, end `36` for `B3:B36`)

The dialog remembers the previous selection, so re-running with the same file
is a single click.

## Build executable

You can compile the project into a standalone executable with the built-in build script:

```bash
python build.py          # single-file executable
python build.py --dir    # directory output (faster build)
```

The output goes to `dist/`. Requires Python 3.9+ and PyInstaller (auto-installed if missing).

## Configuration

`config.json` lives next to the script and is created/updated automatically.
Fields:

| key            | meaning                                                        |
| -------------- | -------------------------------------------------------------- |
| `base_url`     | URL opened at launch; the last URL you navigated to via *Go*.  |
| `last_sheet`   | Last selected worksheet (Excel only).                          |
| `last_col1`    | 0-based index of the first column.                             |
| `last_col2`    | 0-based index of the second column.                            |
| `last_start`   | 1-based first row of the range.                                |
| `last_end`     | 1-based last row of the range (inclusive).                     |

Missing keys fall back to sensible defaults, so older configs keep working.

## Local demo site (ZFmock)

The `ZFmock/` folder provides everything you need to try the tool without connecting to a real school system:

| File | Purpose |
|---|---|
| `mock.html` | A local web page that mimics the Zhengfang grade-entry interface. Open it in the address bar via `file:///path/to/ZFmock/mock.html` (replace with the actual path on your machine). |
| `example.txt` | Sample input file (plain text, two columns). |
| `example.xls` | Same data in old Excel format. |
| `example.xlsx` | Same data in new Excel format. |

Load one of the example files with the **Open** button, then click **Run** to see the scores filled into the mock page.

## Adapting to other systems

This tool was written for 正方教务系统, but the script in
`run_input_scores` is short and easy to tweak. To target a different DOM:

1. Change the iframe selector, e.g. `document.querySelector('iframe[name="..."]')`.
2. Change the input name template, e.g. `` `input[name="..."+i] ` ``.
3. Change the save button selector, e.g. `button.save-btn`.

The rest of the app (file loading, address bar, i18n, build pipeline) stays
as-is.

## Troubleshooting

- *"Missing dependency 'openpyxl' / 'xlrd'"* — install them with
  `pip install openpyxl xlrd` (already listed in `requirements.txt`).
- *Empty dropdowns in the Excel dialog* — the sheet really has no
  cells; open the file in Excel/LibreOffice to verify.
- *Run button does nothing visible* — make sure the embedded page is on the
  actual score-entry screen and that the page exposes
  `iframe[name="zhuti"]`.

## License

GNU GENERAL PUBLIC LICENSE v3.0

Copyright (C) 2025 ZFAutofill contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

---