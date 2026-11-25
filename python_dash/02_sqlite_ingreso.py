import os
import sqlite3
from contextlib import closing

import pandas as pd
from dash import Dash, Input, Output, State, dcc, html

ruta_db = os.path.join("datos", "consumo_electrico.sqlite3")

with closing(sqlite3.connect(ruta_db)) as con, con:
    con.execute("""
    CREATE TABLE IF NOT EXISTS consumo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        periodo TEXT NOT NULL,
        consumo_mwh INTEGER NOT NULL
    )""")

app = Dash(__name__)

app.layout = html.Main([
    html.H1("Consumo Eléctrico"),
    html.Section([
        html.P([
            html.Label("Región:"),
            dcc.Input(id="region", type="text", placeholder="Ingrese la región"),
        ]),
        html.P([
            html.Label("Periodo:"),
            dcc.Input(id="periodo", type="text", placeholder="Ingrese el periodo"),
        ]),
        html.P([
            html.Label("Consumo (MWh):"),
            dcc.Input(id="consumo", type="number", placeholder="Ingrese el consumo"),
        ]),
        html.Button("Guardar", id="guardar"),
        html.P(id="mensaje", role="status"),
    ]),
    html.H2("Datos Ingresados"),
    html.Div(id="tabla"),
])

@app.callback(
    Output("tabla", "children"),
    Input("guardar", "n_clicks"),
    State("region", "value"),
    State("periodo", "value"),
    State("consumo", "value"),
)

def actualizar(n_clicks, region, periodo, consumo):
    mensaje = ""
    with closing(sqlite3.connect(ruta_db)) as con:
        if n_clicks:
            if region and periodo and consumo is not None and consumo >= 0:
                con.execute(
                    "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
                    (region, periodo, consumo)
                )
                con.commit()
                mensaje = "Datos guardados correctamente."
            else:
                mensaje = "Por favor, complete todos los campos correctamente."
        datos = pd.read_sql_query("SELECT * FROM consumo ORDER BY id", con)

        if datos.empty:
            return html.P("No hay datos ingresados.", role="status")

        tabla = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in datos.columns])),
            html.Tbody([
                html.Tr([html.Td(valor) for valor in fila])
                for fila in datos.itertuples(index=False, name=None)
            ]),
        ]) 
        
        return tabla, mensaje

if __name__ == "__main__":
    app.run()