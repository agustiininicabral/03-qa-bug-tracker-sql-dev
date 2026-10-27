"""Local SQLite bug tracker CLI with validated CSV import."""

from __future__ import annotations

import argparse
import csv
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

DB_PATH = Path(os.environ.get("BUGTRACKER_DB", "bugtracker.db"))
SEVERITIES = {"Low", "Medium", "High", "Critical"}
STATUSES = {"Open", "In Progress", "Blocked", "Resolved", "Closed"}
CSV_COLUMNS = {
    "bug_id",
    "created_date",
    "resolved_date",
    "module",
    "severity",
    "status",
    "reported_by",
    "assigned_to",
    "title",
    "description",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS bug (
  bug_id INTEGER PRIMARY KEY,
  created_date TEXT NOT NULL,
  resolved_date TEXT,
  module TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('Low','Medium','High','Critical')),
  status TEXT NOT NULL CHECK (status IN ('Open','In Progress','Blocked','Resolved','Closed')),
  reported_by TEXT NOT NULL,
  assigned_to TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bug_status ON bug(status);
CREATE INDEX IF NOT EXISTS idx_bug_severity ON bug(severity);
CREATE INDEX IF NOT EXISTS idx_bug_created ON bug(created_date);
"""


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    connection = get_conn()
    try:
        with connection:
            connection.executescript(SCHEMA)
    finally:
        connection.close()
    print(f"OK: DB inicializada: {DB_PATH}")


def _validate_rows(rows: list[dict[str, str]], fieldnames: list[str] | None) -> None:
    missing = CSV_COLUMNS - set(fieldnames or [])
    if missing:
        raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")
    seen_ids: set[int] = set()
    for line, row in enumerate(rows, start=2):
        try:
            bug_id = int(row["bug_id"])
            created = date.fromisoformat(row["created_date"])
            resolved = row["resolved_date"].strip()
            if resolved and date.fromisoformat(resolved) < created:
                raise ValueError("resolved date precedes created date")
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError(f"CSV row {line}: invalid bug ID or dates") from error
        if bug_id <= 0 or bug_id in seen_ids:
            raise ValueError(f"CSV row {line}: bug_id must be positive and unique")
        seen_ids.add(bug_id)
        if row["severity"] not in SEVERITIES:
            raise ValueError(f"CSV row {line}: invalid severity")
        if row["status"] not in STATUSES:
            raise ValueError(f"CSV row {line}: invalid status")
        for field in ("module", "reported_by", "assigned_to", "title", "description"):
            if not row[field].strip():
                raise ValueError(f"CSV row {line}: {field} must not be blank")


def import_csv(csv_path: Path) -> int:
    with csv_path.open("r", newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        _validate_rows(rows, reader.fieldnames)

    connection = get_conn()
    try:
        with connection:
            for row in rows:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO bug
                    (bug_id, created_date, resolved_date, module, severity, status,
                     reported_by, assigned_to, title, description)
                    VALUES (?, ?, NULLIF(?, ''), ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(row["bug_id"]), row["created_date"], row["resolved_date"],
                        row["module"], row["severity"], row["status"], row["reported_by"],
                        row["assigned_to"], row["title"], row["description"],
                    ),
                )
    finally:
        connection.close()
    print(f"OK: {len(rows)} bugs importados desde {csv_path}")
    return len(rows)


def add_bug(
    module: str,
    severity: str,
    reported_by: str,
    assigned_to: str,
    title: str,
    description: str,
) -> int:
    if severity not in SEVERITIES:
        raise ValueError("Invalid severity.")
    if not all(value.strip() for value in (module, reported_by, assigned_to, title, description)):
        raise ValueError("Bug fields must not be blank.")

    connection = get_conn()
    try:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO bug
                (created_date, resolved_date, module, severity, status, reported_by,
                 assigned_to, title, description)
                VALUES (?, NULL, ?, ?, 'Open', ?, ?, ?, ?)
                """,
                (date.today().isoformat(), module, severity, reported_by, assigned_to, title, description),
            )
            bug_id = int(cursor.lastrowid)
    finally:
        connection.close()
    print(f"OK: Bug creado con ID: {bug_id}")
    return bug_id


def list_open(limit: int = 20) -> list[tuple]:
    if limit < 1:
        raise ValueError("limit must be a positive integer.")
    connection = get_conn()
    try:
        rows = connection.execute(
            """
            SELECT bug_id, created_date, module, severity, status, title
            FROM bug
            WHERE status IN ('Open','In Progress','Blocked')
            ORDER BY created_date DESC, bug_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        connection.close()
    for row in rows:
        print(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Bug Tracker CLI (SQLite).")
    subparsers = parser.add_subparsers(dest="cmd", required=True)
    subparsers.add_parser("init")

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("--csv", required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--module", required=True)
    add_parser.add_argument("--severity", required=True, choices=sorted(SEVERITIES))
    add_parser.add_argument("--reported_by", required=True)
    add_parser.add_argument("--assigned_to", required=True)
    add_parser.add_argument("--title", required=True)
    add_parser.add_argument("--description", required=True)

    list_parser = subparsers.add_parser("list-open")
    list_parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    try:
        if args.cmd == "init":
            init_db()
        elif args.cmd == "import":
            import_csv(Path(args.csv))
        elif args.cmd == "add":
            add_bug(
                args.module, args.severity, args.reported_by, args.assigned_to,
                args.title, args.description,
            )
        elif args.cmd == "list-open":
            list_open(args.limit)
    except (OSError, ValueError, sqlite3.Error, csv.Error) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
