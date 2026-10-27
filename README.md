# QA Bug Tracker — SQLite + SQL

CLI local para importar bugs desde CSV, crear registros, listar el backlog abierto y analizar severidad, lead time y WIP. El dataset es sintético.

![Bug tracker CI](https://github.com/agustiininicabral/03-qa-bug-tracker-sql-dev/actions/workflows/ci.yml/badge.svg)

## Requisitos

- Python 3.12 o posterior.
- No requiere dependencias externas.

## Uso rápido

Desde la raíz del repositorio:

```powershell
python app/bugtracker.py init
python app/bugtracker.py import --csv data/bugs.csv
python app/bugtracker.py list-open --limit 10
python app/bugtracker.py add --module Checkout --severity High --reported_by QA --assigned_to "Dev 1" --title "Validación faltante" --description "El formulario no informa el campo requerido."
```

El archivo local `bugtracker.db` se crea en el directorio actual y está excluido de Git. Para usar otra ruta, definí la variable de entorno `BUGTRACKER_DB`.

## Validaciones

La importación verifica columnas obligatorias, IDs positivos y únicos, fechas ISO, fecha de resolución no anterior a la creación, severidad/estado admitidos y campos de texto no vacíos. La validación completa ocurre antes de insertar filas, para evitar importaciones parciales por errores de formato.

El CLI también rechaza límites no positivos al listar bugs. Los IDs nuevos se asignan mediante SQLite.

## SQL analítico

Los scripts de `sql/` están orientados a PostgreSQL e incluyen:
- Backlog abierto por severidad.
- Lead time de resolución.
- Backlog total.
- Bugs por módulo en los últimos 90 días.
- WIP por persona asignada.

El CLI usa SQLite y su esquema local; el esquema y las consultas SQL del directorio `sql/` son para una base PostgreSQL separada.

## Pruebas y CI

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions ejecuta pruebas unitarias y un smoke test que inicializa la base temporal, importa el CSV incluido y lista bugs abiertos.

## Limitaciones

El proyecto no implementa autenticación, permisos multiusuario, API web ni auditoría de cambios. Es una demo local, no un sistema de seguimiento de bugs listo para producción.

## Licencia

MIT.
