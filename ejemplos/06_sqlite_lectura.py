"""Lección 6. Consultar CSV importado a SQLite con SELECT y GROUP BY."""

import sqlite3
from contextlib import closing

import plotly.express as px
from dash import Dash, Input, Output, dcc, html
import pandas as pd

from datos import leer_consumo

datos = leer_consumo()
app = Dash(__name__, title="Consumo eléctrico · Consultas SQL")
app.layout = html.Main([
    html.H1("Consumo anual consultado con SQL"),
    html.P("Cada consulta usa una base SQLite temporal en memoria."),
    html.Label("Región", htmlFor="region"),
    dcc.Dropdown(sorted(datos.region.unique()), "Lima", id="region", clearable=False),
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
            FROM consumo WHERE region = ?
            GROUP BY anio ORDER BY anio
        """, con, params=(region,))

    # SQLite agrega las filas. Plotly recibe el resultado de la consulta.
    figura = px.bar(resumen, x="anio", y="total_mwh", title=f"Consumo anual · {region}",
                    labels={"anio": "Año", "total_mwh": "Consumo (MWh)"})
    return figura, resumen.to_string(index=False)


if __name__ == "__main__":
    app.run()
