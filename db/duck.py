from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import duckdb

from models.bien import Bien
from models.empresa import EmpresaData
from models.indice_facpce import GestorIndicesFACPCE

SCHEMA = r"""
CREATE SEQUENCE IF NOT EXISTS seq_empresa START 1;

CREATE TABLE IF NOT EXISTS empresa (
  id INTEGER PRIMARY KEY DEFAULT nextval('seq_empresa'),
  cuit VARCHAR NOT NULL UNIQUE,
  razon_social VARCHAR,
  fecha_inicio VARCHAR,
  fecha_cierre VARCHAR,
  ejercicio_liquidacion VARCHAR,
  ejercicio_anterior VARCHAR,
  configurada BOOLEAN
);

CREATE TABLE IF NOT EXISTS tipos_bienes (
  empresa_id INTEGER NOT NULL,
  nombre VARCHAR NOT NULL,
  PRIMARY KEY (empresa_id, nombre),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id)
);

CREATE TABLE IF NOT EXISTS bienes (
  id INTEGER NOT NULL,
  empresa_id INTEGER NOT NULL,
  descripcion VARCHAR NOT NULL,
  tipo_bien VARCHAR NOT NULL,
  es_amortizable BOOLEAN,
  anos_amortizacion INTEGER,
  ejercicio_alta INTEGER,
  fecha_ingreso VARCHAR,
  fecha_baja VARCHAR,
  valor_origen DOUBLE,
  PRIMARY KEY (empresa_id, id),
    FOREIGN KEY (empresa_id) REFERENCES empresa(id)
);

CREATE TABLE IF NOT EXISTS meta (
    key VARCHAR PRIMARY KEY,
    value VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_empresa_cuit ON empresa(cuit);
CREATE INDEX IF NOT EXISTS idx_bienes_empresa ON bienes(empresa_id);
CREATE INDEX IF NOT EXISTS idx_bienes_tipo ON bienes(empresa_id, tipo_bien);
CREATE INDEX IF NOT EXISTS idx_bienes_ejercicio ON bienes(empresa_id, ejercicio_alta);

CREATE TABLE IF NOT EXISTS indices_facpce (
  fecha VARCHAR PRIMARY KEY,
  indice DOUBLE NOT NULL,
  observaciones VARCHAR,
  fecha_carga VARCHAR
);

INSERT OR IGNORE INTO meta(key, value) VALUES ('schema_version', '2');
UPDATE meta SET value = '2' WHERE key = 'schema_version' AND value <> '2';
"""


def connect(db_path: str = "data/cartera.duckdb") -> duckdb.DuckDBPyConnection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(path))


def init_schema(con: duckdb.DuckDBPyConnection) -> None:
    con.execute(SCHEMA)


def _get_empresa_id_by_cuit(con: duckdb.DuckDBPyConnection, cuit: str) -> Optional[int]:
    row = con.execute("SELECT id FROM empresa WHERE cuit = ?", [cuit]).fetchone()
    return row[0] if row else None


def upsert_empresa(con: duckdb.DuckDBPyConnection, empresa: EmpresaData) -> int:
    empresa_id = _get_empresa_id_by_cuit(con, empresa.cuit)
    if empresa_id is None:
        row = con.execute(
            """
            INSERT INTO empresa(
                cuit, razon_social, fecha_inicio, fecha_cierre,
                ejercicio_liquidacion, ejercicio_anterior, configurada
            ) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id
            """,
            [
                empresa.cuit,
                empresa.razon_social,
                empresa.fecha_inicio,
                empresa.fecha_cierre,
                empresa.ejercicio_liquidacion,
                empresa.ejercicio_anterior,
                int(bool(empresa.configurada)),
            ],
        ).fetchone()
        empresa_id = int(row[0])
    else:
        con.execute(
            """
            UPDATE empresa
               SET razon_social = ?,
                   fecha_inicio = ?,
                   fecha_cierre = ?,
                   ejercicio_liquidacion = ?,
                   ejercicio_anterior = ?,
                   configurada = ?
             WHERE id = ?
            """,
            [
                empresa.razon_social,
                empresa.fecha_inicio,
                empresa.fecha_cierre,
                empresa.ejercicio_liquidacion,
                empresa.ejercicio_anterior,
                int(bool(empresa.configurada)),
                empresa_id,
            ],
        )
    return empresa_id


def save_company_state(
    con: duckdb.DuckDBPyConnection,
    empresa: EmpresaData,
    tipos_bienes: List[str],
    bienes: Dict[int, Bien],
    gestor_indices: GestorIndicesFACPCE,
) -> None:
    if not empresa or not empresa.cuit:
        raise ValueError("Empresa/CUIT is required to save")

    con.execute("BEGIN")
    try:
        empresa_id = upsert_empresa(con, empresa)

        con.execute("DELETE FROM tipos_bienes WHERE empresa_id = ?", [empresa_id])
        for nombre in tipos_bienes:
            con.execute(
                "INSERT INTO tipos_bienes(empresa_id, nombre) VALUES (?, ?)",
                [empresa_id, nombre],
            )

        con.execute("DELETE FROM bienes WHERE empresa_id = ?", [empresa_id])
        for bien_id in sorted(bienes.keys()):
            bien = bienes[bien_id]
            data = bien.to_sql_dict()
            con.execute(
                """
                INSERT INTO bienes(
                    id, empresa_id, descripcion, tipo_bien, es_amortizable,
                    anos_amortizacion, ejercicio_alta, fecha_ingreso, fecha_baja,
                    valor_origen
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    data["id"],
                    empresa_id,
                    data["descripcion"],
                    data["tipo_bien"],
                    int(bool(data["es_amortizable"])),
                    data["anos_amortizacion"],
                    data["ejercicio_alta"],
                    data["fecha_ingreso"],
                    data["fecha_baja"],
                    data["valor_origen"],
                ],
            )

        for indice in gestor_indices.get_todos_indices():
            con.execute(
                """
                INSERT OR REPLACE INTO indices_facpce(fecha, indice, observaciones, fecha_carga)
                VALUES (?, ?, ?, ?)
                """,
                [
                    indice.fecha,
                    float(indice.indice),
                    indice.observaciones,
                    indice.fecha_carga,
                ],
            )

        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise


def load_by_cuit(
    con: duckdb.DuckDBPyConnection, cuit: str
) -> Tuple[Optional[EmpresaData], List[str], Dict[int, Bien], GestorIndicesFACPCE]:
    empresa_id = _get_empresa_id_by_cuit(con, cuit)
    if empresa_id is None:
        return None, [], {}, GestorIndicesFACPCE()

    row = con.execute(
        """
        SELECT id, cuit, razon_social, fecha_inicio, fecha_cierre,
               ejercicio_liquidacion, ejercicio_anterior, configurada
          FROM empresa
         WHERE id = ?
        """,
        [empresa_id],
    ).fetchone()

    empresa = EmpresaData()
    empresa.cuit = row[1]
    empresa.razon_social = row[2]
    empresa.fecha_inicio = row[3]
    empresa.fecha_cierre = row[4]
    empresa.ejercicio_liquidacion = row[5]
    empresa.ejercicio_anterior = row[6]
    empresa.configurada = bool(row[7])

    tipos_rows = con.execute(
        "SELECT nombre FROM tipos_bienes WHERE empresa_id = ? ORDER BY nombre",
        [empresa_id],
    ).fetchall()
    tipos = [tipo_row[0] for tipo_row in tipos_rows]

    bienes_rows = con.execute(
        """
        SELECT id, descripcion, tipo_bien, es_amortizable, anos_amortizacion,
               ejercicio_alta, fecha_ingreso, fecha_baja, valor_origen
          FROM bienes
         WHERE empresa_id = ?
      ORDER BY id
        """,
        [empresa_id],
    ).fetchall()

    bienes: Dict[int, Bien] = {}
    for (
        bien_id,
        descripcion,
        tipo_bien,
        es_amortizable,
        anos_amortizacion,
        ejercicio_alta,
        fecha_ingreso,
        fecha_baja,
        valor_origen,
    ) in bienes_rows:
        data = {
            "id": bien_id,
            "descripcion": descripcion,
            "tipo_bien": tipo_bien,
            "es_amortizable": bool(es_amortizable),
            "anos_amortizacion": anos_amortizacion,
            "ejercicio_alta": ejercicio_alta,
            "fecha_ingreso": fecha_ingreso,
            "fecha_baja": fecha_baja,
            "valor_origen": valor_origen,
        }
        bien = Bien.from_sql_dict(data)
        bienes[bien.id] = bien

    gestor = GestorIndicesFACPCE()
    indices_rows = con.execute(
        "SELECT fecha, indice, observaciones FROM indices_facpce"
    ).fetchall()
    for fecha, indice_val, observaciones in indices_rows:
        gestor.agregar_indice(fecha, float(indice_val), observaciones)

    return empresa, tipos, bienes, gestor
