"""Lección 1. Leer el CSV y colocar una figura y una tabla en el layout."""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)

# Cada punto suma los consumos de todas las regiones de la muestra.
mensual = datos.groupby("periodo", as_index=False)["consumo_mwh"].sum()
figura = px.line(mensual, x="periodo", y="consumo_mwh", markers=True,
                 labels={"periodo": "Mes", "consumo_mwh": "Consumo (MWh)"})

app = Dash(__name__)
app.layout = html.Main([
    html.H1("Consumo eléctrico mensual"),
    dcc.Graph(figure=figura),
    html.H2("Primeras 12 filas del CSV"),
    html.Table([
        html.Thead(html.Tr([html.Th(columna) for columna in datos.columns])),
        html.Tbody([
            html.Tr([html.Td(valor) for valor in fila])
            for fila in datos.head(12).itertuples(index=False, name=None)
        ]),
    ]),
])

if __name__ == "__main__":
    app.run()
