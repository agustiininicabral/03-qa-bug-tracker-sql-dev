# QA Bug Tracker (SQL + Desarrollo)

## Objetivo
Sistema simple de tracking de bugs: dataset + esquema SQL + consultas + CLI en Python (SQLite) para crear/importar/listar bugs.

## Stack
- SQL (consultas analíticas)
- Python (CLI)
- SQLite (local)

## Cómo ejecutar (rápido)
1) `python app/bugtracker.py init`
2) `python app/bugtracker.py import --csv data/bugs.csv`
3) `python app/bugtracker.py list-open --limit 10`
4) (Opcional) `sql/queries.sql` para analítica (adaptable a PostgreSQL)

## Estructura
```
03-qa-bug-tracker-sql-dev/
├── app/bugtracker.py
├── data/bugs.csv
└── sql/
```

## Sugerencia
- En entrevistas: explica cómo medirías backlog, lead time y severidad para priorizar.
