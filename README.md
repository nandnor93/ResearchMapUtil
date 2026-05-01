# ResearchMap JSON (JSONL) to CSV Converter

ほぼ完全にChatGPT製。READMEも含めて。


## 📄 README — 日本語版

### 概要
このスクリプトは、ResearchMap形式の JSON (JSONL) ファイルを読み込み、以下の形式で出力します。
- JSONL（1行1オブジェクト）
- カテゴリ分け済みCSV
- JSPS科研費 年次報告用CSV 論文用・学会用

研究業績データ（発表、論文、受賞など）を簡単に集約・分類・CSV化できます。また、ソート、重複除去、著者フィルターも可能です。

### 特長
- 複数ファイルのマージ
- 日付（YYYY-MM-DD）による範囲指定フィルタ
- 著者（日本語／英語名）によるフィルタ（複数指定可）
- 重複（同日付＋同タイトル）の除去オプション
- CSV出力
    - カテゴリ分け（国内発表／国際発表／招待講演／論文／受賞）
    - 英日両タイトル＆著者名を列分け
- JSPS年次報告フォーマットCSV出力
    - 学会・論文フォーマットそれぞれ対応


### 要件
- Python 3.7 以上
- 標準ライブラリのみ（`json`, `argparse`, `csv`, `datetime`, `sys`）

### 使い方

```bash
./researchmap_util.py [OPTIONS] file1.jsonl file2.jsonl …
```

#### 主なオプション

| オプション                         | 説明                      |
| ----------------------------- | ----------------------- |
| `--start-date YYYY-MM-DD`     | 取得開始日（inclusive）        |
| `--end-date   YYYY-MM-DD`     | 取得終了日（inclusive）        |
| `--author NAME [NAME ...]`    | 著者名フィルタ（日本語／英語）         |
| `--dedupe`                    | 同一日付＋タイトルの重複アイテムを一度だけ出力 |
| `--jsonl`                     | JSONL形式で出力              |
| `--csv`                       | カテゴリ分けCSVとして出力          |
| `--csv-jsps-papers`           | JSPS年次報告の学術論文用CSVで出力 ※査読有無・国際共著は手動で記載 |
| `--csv-jsps-conferences`      | JSPS年次報告の国内・国際用CSVで出力 |
| `--output, -o FILE`           | 出力先ファイル（デフォルト: stdout）  |


#### CSV出力カラム（`--csv` 時）

```
Date, Category,
Title (En), Title (Ja),
Authors (En), Authors (Ja),
Publication/Award/Event,
Volume, Number, Start Page, End Page
```

#### 例

1. 全ファイルをマージして標準出力にJSON（整形済み）で出力  
   ```bash
   ./researchmap_util.py data1.jsonl data2.jsonl
   ```
2. 2024年度以降の国際発表のみ CSV 出力  
   ```bash
   ./researchmap_util.py --start-date 2024-04-01 --csv data.jsonl | grep 'International Presentation' > intl_presentations.csv
   ```
3. 特定著者の成果を重複除去して JSONL 化  
   ```bash
   ./researchmap_util.py --author "Hokkai M." "北海 道大" --dedupe --jsonl a.jsonl b.jsonl > filtered.jsonl
   ```
4. 特定著者の特定年度のJSPS年次報告CSV
   ```bash
   ./researchmap_util.py --start-date 2025-04-01 --end-date 2026-03-31 --csv-jsps-paper data.json -o hokkai-2025-kiban.csv --author "Hokkai M." "北海 道大" "Hokudai H." "北大 花子"
   ```

---

## 📄 README — English Version

### Overview

This script ingests one or more ResearchMap-format JSONL files and outputs:

* JSONL (one object per line)
* A categorized CSV
* A formatted CSV for JSPS KAKEN annual reports

It streamlines aggregation, classification, and CSV export of research achievements (presentations, papers, awards, etc.).

### Features

* Merge multiple input files
* Date-range filtering (`YYYY-MM-DD`    )
* Author filtering (Japanese/English names, multiple)
* Duplicate removal by date+title
* CSV export
   * Category assignment (Domestic Presentation / International Presentation / Invited Talk / Academic Paper / Award)
   * CSV fields for `volume`, `number`, `starting_page`, `ending_page`
* JSPS annual report format
   * CSV formats for papers and conferences

### Requirements

* Python 3.7+
* Standard library only (`json`, `argparse`, `csv`, `datetime`, `sys`)


### Usage

```bash
./researchmap_util.py [OPTIONS] file1.jsonl file2.jsonl …
```

#### Main Options

| Option                        | Description                                 |
| ----------------------------- | ------------------------------------------- |
| `--start-date YYYY-MM-DD`     | Start date (inclusive)                      |
| `--end-date   YYYY-MM-DD`     | End date (inclusive)                        |
| `--author NAME [NAME ...]`    | Filter by author name (Ja/En)               |
| `--dedupe`                    | Remove duplicates with identical date+title |
| `--jsonl`                     | Output as JSONL                             |
| `--csv`                       | Output as categorized CSV                   |
| `--csv-jsps-papers`           | Output as JSPS annual report CSV for academic papers \*peer review and intl. co-authorship must be filled manually |
| `--csv-jsps-conferences`      | Output as JSPS annual report CSV for domestic/international conferences |
| `--output, -o FILE`           | Output file (default: stdout)               |

#### CSV Columns (`--csv`)

```
Date, Category,
Title (En), Title (Ja),
Authors (En), Authors (Ja),
Publication/Award/Event,
Volume, Number, Start Page, End Page
```

#### Examples

1. Merge all files and print pretty JSON:  
   ```bash
   ./researchmap_util.py data1.jsonl data2.jsonl
   ```
2. Export international presentations since 2024 as CSV:  
   ```bash
   ./researchmap_util.py --start-date 2024-04-01 --csv data.jsonl | grep 'International Presentation' > intl_presentations.csv
   ```
3. Filter for a specific author, remove duplicates, and output JSONL:  
   ```bash
   ./researchmap_util.py --author "Hokkai M." "北海 道大" --dedupe --jsonl a.jsonl b.jsonl > filtered.jsonl
   ```
4. JSPS annual report CSV for a specific author and fiscal year:  
   ```bash
   ./researchmap_util.py --start-date 2025-04-01 --end-date 2026-03-31 --csv-jsps-paper data.json -o hokkai-2025-kiban.csv --author "Hokkai M." "北海 道大" "Hokudai H." "北大 花子"
   ```
