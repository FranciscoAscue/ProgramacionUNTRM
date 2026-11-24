"""Lección 2. Un selector cambia una figura mediante Input y Output."""

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)
app = Dash(__name__, title="Consumo eléctrico · Callback")
app.layout = html.Main([
    html.H1("Evolución mensual por región"),
    html.Label("Región", htmlFor="region"),
    dcc.Dropdown(sorted(datos.region.unique()), id="region", placeholder="Todas las regiones"),
    dcc.Graph(id="grafico"),
])

# El ID conecta estos argumentos con los componentes del layout.
# Cambiar region.value vuelve a ejecutar la función y actualiza grafico.figure.
@app.callback(Output("grafico", "figure"), Input("region", "value"))
def actualizar(region):
    visibles = datos[datos.region == region] if region else datos
    mensual = visibles.groupby("periodo", as_index=False)["consumo_mwh"].sum()
    return px.line(mensual, x="periodo", y="consumo_mwh", markers=True,
                   labels={"periodo": "Mes", "consumo_mwh": "Consumo (MWh)"})


if __name__ == "__main__":
    app.run()
