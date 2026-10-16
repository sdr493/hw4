"""Export the databases to self-contained HTML viewers in output/.

- data/campus_customs.db -> output/database_viewer.html (password hashes redacted)
- data/promotions.db     -> output/promotions_viewer.html (promo codes shown; this file is not committed)
"""

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent
REDACTED_COLUMNS = {"password_hash"}
VIEWERS = [
    # (database, output file, title, subtitle)
    (ROOT / "data" / "campus_customs.db", ROOT / "output" / "database_viewer.html",
     "Database", "Read-only export of data/campus_customs.db. Password hashes are redacted."),
    (ROOT / "data" / "promotions.db", ROOT / "output" / "promotions_viewer.html",
     "Promotions", "Read-only export of data/promotions.db: one single-use 10% code per user. used_at is set once a code is applied."),
]


def load_tables(db_path: Path) -> list[dict]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    tables = []
    names = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY rowid")]
    for name in names:
        info = conn.execute(f'PRAGMA table_info("{name}")').fetchall()
        fks = conn.execute(f'PRAGMA foreign_key_list("{name}")').fetchall()
        fk_map = {fk[3]: f"{fk[2]}.{fk[4]}" for fk in fks}
        columns = [{
            "name": c[1], "type": c[2] or "", "notnull": bool(c[3]),
            "default": c[4], "pk": bool(c[5]), "fk": fk_map.get(c[1]),
        } for c in info]
        col_names = [c["name"] for c in columns]
        rows = []
        for row in conn.execute(f'SELECT * FROM "{name}"'):
            rows.append(["[redacted]" if col in REDACTED_COLUMNS else val
                         for col, val in zip(col_names, row)])
        tables.append({"name": name, "columns": columns, "rows": rows})
    conn.close()
    return tables


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Campus Customs Database</title>
<style>
:root { --bg:#0b0b0d; --panel:#16161a; --line:#2a2a31; --text:#f2f2f5; --muted:#a3a3ad; --pink:#ff4fa3; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text); font:15px/1.5 system-ui, sans-serif; }
header { padding:24px 16px 8px; max-width:1400px; margin:auto; }
h1 { margin:0; font-size:26px; } h1 span { color:var(--pink); }
p.sub { color:var(--muted); margin:4px 0 0; }
nav { display:flex; gap:8px; flex-wrap:wrap; padding:16px; max-width:1400px; margin:auto; }
nav button { background:var(--panel); color:var(--text); border:1px solid var(--line); border-radius:999px;
  padding:8px 16px; cursor:pointer; font:inherit; }
nav button[aria-selected=true] { background:var(--pink); color:#000; border-color:var(--pink); font-weight:600; }
main { max-width:1400px; margin:auto; padding:0 16px 40px; }
h2 { font-size:18px; color:var(--pink); margin:24px 0 8px; }
.wrap { overflow:auto; border:1px solid var(--line); border-radius:10px; max-height:70vh; }
table { border-collapse:collapse; width:100%; font-size:13px; }
th, td { padding:8px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }
th { background:var(--panel); position:sticky; top:0; }
td.long { max-width:420px; } td pre { margin:0; white-space:pre-wrap; word-break:break-word; font:12px ui-monospace, monospace; color:var(--muted); }
.tag { display:inline-block; font-size:11px; padding:1px 6px; border-radius:6px; margin-left:4px; border:1px solid var(--pink); color:var(--pink); }
input { width:100%; max-width:420px; padding:10px 12px; background:var(--panel); color:var(--text);
  border:1px solid var(--line); border-radius:8px; font:inherit; }
input:focus { outline:2px solid var(--pink); }
.count { color:var(--muted); margin-left:8px; }
</style></head><body>
<header><h1>Campus Customs <span>__TITLE__</span></h1>
<p class="sub">__SUBTITLE__</p></header>
<nav role="tablist" id="tabs"></nav>
<main id="main"></main>
<script>
const TABLES = __DATA__;
const tabs = document.getElementById('tabs'), main = document.getElementById('main');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function cell(v) {
  if (v === null) return '<td><span style="color:var(--muted)">NULL</span></td>';
  const s = String(v);
  if (/^[\\[{]/.test(s)) { try { return '<td class="long"><pre>' + esc(JSON.stringify(JSON.parse(s), null, 1)) + '</pre></td>'; } catch {} }
  return '<td' + (s.length > 80 ? ' class="long"' : '') + '>' + esc(s) + '</td>';
}
function show(i) {
  const t = TABLES[i];
  [...tabs.children].forEach((b, j) => b.setAttribute('aria-selected', i === j));
  const schema = t.columns.map(c => '<tr><td>' + esc(c.name) + (c.pk ? '<span class="tag">PK</span>' : '') +
    (c.fk ? '<span class="tag">FK → ' + esc(c.fk) + '</span>' : '') + '</td><td>' + esc(c.type) + '</td><td>' +
    (c.notnull ? 'yes' : 'no') + '</td><td>' + esc(c.default ?? '') + '</td></tr>').join('');
  main.innerHTML = '<h2>Fields</h2><div class="wrap"><table><tr><th>Column</th><th>Type</th><th>Required</th><th>Default</th></tr>' +
    schema + '</table></div><h2>Rows<span class="count" id="count"></span></h2>' +
    '<label for="q" style="display:block;color:var(--muted);margin-bottom:6px">Filter rows</label>' +
    '<input id="q" placeholder="Type to filter…"><div class="wrap" style="margin-top:12px"><table id="rows"></table></div>';
  const head = '<tr>' + t.columns.map(c => '<th>' + esc(c.name) + '</th>').join('') + '</tr>';
  const render = q => {
    const rows = t.rows.filter(r => !q || r.some(v => String(v).toLowerCase().includes(q)));
    document.getElementById('rows').innerHTML = head + rows.map(r => '<tr>' + r.map(cell).join('') + '</tr>').join('');
    document.getElementById('count').textContent = rows.length + ' of ' + t.rows.length;
  };
  document.getElementById('q').oninput = e => render(e.target.value.toLowerCase());
  render('');
}
TABLES.forEach((t, i) => { const b = document.createElement('button'); b.role = 'tab';
  b.textContent = t.name + ' (' + t.rows.length + ')'; b.onclick = () => show(i); tabs.appendChild(b); });
show(0);
</script></body></html>
"""


def main() -> None:
    for db_path, out_path, title, subtitle in VIEWERS:
        if not db_path.exists():
            print(f"Skipped {db_path.name} (not created yet)")
            continue
        out_path.parent.mkdir(exist_ok=True)
        data = json.dumps(load_tables(db_path)).replace("</", "<\\/")
        page = PAGE.replace("__TITLE__", title).replace("__SUBTITLE__", subtitle).replace("__DATA__", data)
        out_path.write_text(page, encoding="utf-8")
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
