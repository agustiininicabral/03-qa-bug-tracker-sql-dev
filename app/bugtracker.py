import sqlite3
from pathlib import Path
import argparse
import csv
from datetime import date

DB_PATH = Path("bugtracker.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS bug (
  bug_id INTEGER PRIMARY KEY,
  created_date TEXT NOT NULL,
  resolved_date TEXT,
  module TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  reported_by TEXT NOT NULL,
  assigned_to TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL
);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_conn()
    with conn:
        conn.executescript(SCHEMA)
    conn.close()
    print("OK: DB inicializada:", DB_PATH)

def import_csv(csv_path: Path):
    conn = get_conn()
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    with conn:
        for r in rows:
            conn.execute(
                """
                INSERT OR REPLACE INTO bug
                (bug_id, created_date, resolved_date, module, severity, status, reported_by, assigned_to, title, description)
                VALUES (?, ?, NULLIF(?, ''), ?, ?, ?, ?, ?, ?, ?)
                """,
                (int(r["bug_id"]), r["created_date"], r["resolved_date"], r["module"], r["severity"], r["status"],
                 r["reported_by"], r["assigned_to"], r["title"], r["description"])
            )
    conn.close()
    print(f"OK: {len(rows)} bugs importados desde {csv_path}")

def add_bug(module, severity, reported_by, assigned_to, title, description):
    conn = get_conn()
    today = date.today().isoformat()
    with conn:
        cur = conn.execute("SELECT COALESCE(MAX(bug_id), 0) + 1 FROM bug")
        bug_id = cur.fetchone()[0]
        conn.execute(
            """INSERT INTO bug (bug_id, created_date, resolved_date, module, severity, status, reported_by, assigned_to, title, description)
               VALUES (?, ?, NULL, ?, ?, 'Open', ?, ?, ?, ?)
            """,
            (bug_id, today, module, severity, reported_by, assigned_to, title, description)
        )
    conn.close()
    print("OK: Bug creado con ID:", bug_id)

def list_open(limit=20):
    conn = get_conn()
    q = """SELECT bug_id, created_date, module, severity, status, title
           FROM bug WHERE status IN ('Open','In Progress','Blocked')
           ORDER BY created_date DESC LIMIT ?"""
    rows = conn.execute(q, (limit,)).fetchall()
    conn.close()
    for r in rows:
        print(r)

def main():
    ap = argparse.ArgumentParser(description="Bug Tracker CLI (SQLite).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")
    pimp = sub.add_parser("import")
    pimp.add_argument("--csv", required=True)

    padd = sub.add_parser("add")
    padd.add_argument("--module", required=True)
    padd.add_argument("--severity", required=True, choices=["Low","Medium","High","Critical"])
    padd.add_argument("--reported_by", required=True)
    padd.add_argument("--assigned_to", required=True)
    padd.add_argument("--title", required=True)
    padd.add_argument("--description", required=True)

    plist = sub.add_parser("list-open")
    plist.add_argument("--limit", type=int, default=20)

    args = ap.parse_args()

    if args.cmd == "init":
        init_db()
    elif args.cmd == "import":
        import_csv(Path(args.csv))
    elif args.cmd == "add":
        add_bug(args.module, args.severity, args.reported_by, args.assigned_to, args.title, args.description)
    elif args.cmd == "list-open":
        list_open(args.limit)

if __name__ == "__main__":
    main()