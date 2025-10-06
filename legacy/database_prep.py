"""Legacy SQLite schema (deprecated).

This module used to provision a SQLite database that relied on deferred-date
columns such as ``fecha_diferida`` and ``valor_fecha_diferida``. The live
application now persists data in DuckDB using purely historical origin values.

The code has been intentionally removed to prevent the old schema from being
regenerated. If you need to inspect the historical migration scripts, refer to
Git history before the multi-CUIT DuckDB refactor.
"""

raise RuntimeError(
    "database_prep.py está deprecado. Usa db/duck.py con el esquema multi-CUIT."
)
