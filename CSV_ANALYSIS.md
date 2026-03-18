# CSV Analysis Report — images.csv

## File Info
- **File:** images.csv
- **Separator:** comma (`,`)
- **Encoding:** UTF-8
- **Total rows:** 341 (excluding header)
- **API Resource:** `/images`

## Schema

| Column | Python Type | SQL Type | Nullable | Notes |
|---|---|---|---|---|
| image_url | str | TEXT | No | Primary URL of the image |
| alt_text | Optional[str] | TEXT | Yes | Alt text, many empty values |
| page_source | Optional[str] | TEXT | Yes | Source page URL |
| width | Optional[int] | INTEGER | Yes | Many empty values |
| height | Optional[int] | INTEGER | Yes | Many empty values |
| format | str | TEXT | No | svg, jpg, png |
| estimated_size_kb | float | REAL | No | File size in KB |
| category | str | TEXT | No | misc, home, etc. |
| downloaded | bool | BOOLEAN | No | True/False |
| local_path | Optional[str] | TEXT | Yes | Local file path |

## Auto-generated column
- `id` — INTEGER PRIMARY KEY AUTOINCREMENT (not present in CSV)

## Sample values
- Formats: svg, jpg, png
- Categories: misc, home (and possibly others)
- downloaded: always True in sample, but treated as boolean
- width/height: frequently empty
