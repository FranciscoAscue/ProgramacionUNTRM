"""Lección 6. Consultar CSV importado a SQLite con SELECT y GROUP BY."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)
app = Dash(__name__, title="Consumo eléctrico · Consultas SQL")
app.layout = html.Main([
    html.H1("Consumo anual consultado con SQL"),
    html.P("Cada consulta usa una base SQLite temporal en memoria."),
    html.Label("Región", htmlFor="region"),
    dcc.Dropdown(sorted(datos.region.unique()), id="region", placeholder="Todas las regiones"),
    dcc.Graph(id="grafico"),
    html.Pre(id="resultado"),
])


@app.callback(
    Output("grafico", "figure"), Output("resultado", "children"),
    Input("region", "value"),
)
def consultar(region):
    # La conexión se cierra al finalizar el callback. La base desaparece con ella.
    with closing(sqlite3.connect(":memory:")) as con:
        datos.to_sql("consumo", con, index=False)
        resumen = pd.read_sql_query("""
            SELECT substr(periodo, 1, 4) AS anio, SUM(consumo_mwh) AS total_mwh
            FROM consumo WHERE (? IS NULL OR region = ?)
            GROUP BY anio ORDER BY anio
        """, con, params=(region, region))

    # SQLite agrega las filas. Plotly recibe el resultado de la consulta.
    figura = px.bar(resumen, x="anio", y="total_mwh", title=f"Consumo anual · {region or 'Todas las regiones'}",
                    labels={"anio": "Año", "total_mwh": "Consumo (MWh)"})
    return figura, resumen.to_string(index=False)


if __name__ == "__main__":
    app.run()
