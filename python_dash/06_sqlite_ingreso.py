"""Lección 6. Crear una tabla vacía y guardar filas desde un formulario."""

import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
from dash import Dash, Input, Output, State, dcc, html

ruta_db = Path(os.environ.get("INGRESO_DB", Path(__file__).with_name("ingreso_dash.sqlite3")))

# CREATE TABLE define las columnas. La tabla sigue vacía hasta el primer INSERT.
with closing(sqlite3.connect(ruta_db)) as con, con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS consumo (
            id INTEGER PRIMARY KEY,
            region TEXT NOT NULL,
            periodo TEXT NOT NULL,
            consumo_mwh INTEGER NOT NULL
        )
    """)

app = Dash(__name__)
app.layout = html.Main([
    html.H1("Primeros registros en SQLite"),
    html.Section([
        html.P([
            html.Label("Región", htmlFor="region"),
            dcc.Input(id="region", type="text", placeholder="Piura"),
        ]),
        html.P([
            html.Label("Mes (AAAA-MM)", htmlFor="periodo"),
            dcc.Input(id="periodo", type="text", placeholder="2025-01"),
        ]),
        html.P([
            html.Label("Consumo (MWh)", htmlFor="mwh"),
            dcc.Input(id="mwh", type="number", min=0, step=1),
        ]),
        html.Button("Guardar", id="guardar"),
        html.P(id="mensaje", role="status"),
    ]),
    html.H2("Registros guardados"),
    html.Div(id="tabla"),
])


@app.callback(
    Output("tabla", "children"), Output("mensaje", "children"),
    Input("guardar", "n_clicks"),
    State("region", "value"), State("periodo", "value"), State("mwh", "value"),
)
def actualizar(n_clicks, region, periodo, mwh):
    mensaje = ""
    with closing(sqlite3.connect(ruta_db)) as con:
        # En la primera carga solo se ejecuta el SELECT.
        if n_clicks:
            if region and periodo and mwh is not None and mwh >= 0 and mwh % 1 == 0:
                con.execute(
                    "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
                    (region, periodo, int(mwh)),
                )
                con.commit()
                mensaje = "Registro guardado."
            else:
                mensaje = "Completa la región, el mes y un consumo entero no negativo."

        datos = pd.read_sql_query("SELECT * FROM consumo ORDER BY id", con)

    if datos.empty:
        return html.P("La tabla está vacía. Guarda tu primer registro."), mensaje

    tabla = html.Table([
        html.Thead(html.Tr([html.Th(columna) for columna in datos.columns])),
        html.Tbody([
            html.Tr([html.Td(valor) for valor in fila])
            for fila in datos.itertuples(index=False, name=None)
        ]),
    ])
    return tabla, mensaje


if __name__ == "__main__":
    app.run()
