"""Acceso a SQLite. Los callbacks trabajan con funciones, no con SQL incrustado."""

import sqlite3
from contextlib import closing

import pandas as pd

from datos import COLUMNAS


def inicializar(ruta, datos):
    # Bloqueamos la inicialización hasta que esquema y semilla se confirmen juntos.
    with closing(sqlite3.connect(ruta)) as db, db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("PRAGMA user_version").fetchone()[0] == 0:
            db.execute("""
                CREATE TABLE consumo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    region TEXT NOT NULL,
                    periodo TEXT NOT NULL,
                    consumo_mwh INTEGER NOT NULL CHECK (consumo_mwh BETWEEN 0 AND 1000000000),
                    UNIQUE (region, periodo)
                )
            """)
            db.executemany(
                "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
                datos[COLUMNAS].itertuples(index=False, name=None),
            )
            db.execute("PRAGMA user_version = 1")


def listar(ruta):
    with closing(sqlite3.connect(ruta)) as db:
        return pd.read_sql_query("SELECT * FROM consumo ORDER BY region, periodo", db)


def consultar(ruta, registro_id):
    with closing(sqlite3.connect(ruta)) as db:
        db.row_factory = sqlite3.Row
        return db.execute("SELECT * FROM consumo WHERE id = ?", (registro_id,)).fetchone()


def guardar(ruta, registro_id, region, periodo, mwh):
    # Los ? reciben valores como parámetros. Al salir de with se confirma o revierte.
    with closing(sqlite3.connect(ruta)) as db, db:
        if registro_id is None:
            db.execute("INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
                       (region, periodo, mwh))
        else:
            resultado = db.execute(
                "UPDATE consumo SET region = ?, periodo = ?, consumo_mwh = ? WHERE id = ?",
                (region, periodo, mwh, registro_id),
            )
            if resultado.rowcount != 1:
                raise LookupError("El registro ya no existe.")


def eliminar(ruta, registro_id):
    with closing(sqlite3.connect(ruta)) as db, db:
        resultado = db.execute("DELETE FROM consumo WHERE id = ?", (registro_id,))
        if resultado.rowcount != 1:
            raise LookupError("El registro ya no existe.")
