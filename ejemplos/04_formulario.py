"""Lección 4. Botón y State para leer un formulario."""

from pathlib import Path

import pandas as pd
from dash import Dash, Input, Output, State, dcc, html

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)
regiones = sorted(datos.region.unique())
app = Dash(__name__, title="Consumo eléctrico · Formulario")
app.layout = html.Main([
    html.H1("Previsualizar un registro de consumo"),
    html.Section([
        html.Label("Región", htmlFor="region"),
        dcc.Dropdown(regiones, id="region"),
        html.Label("Mes (AAAA-MM)", htmlFor="periodo"),
        dcc.Input(id="periodo", type="text", placeholder="2025-01"),
        html.Label("Consumo (MWh)", htmlFor="mwh"),
        dcc.Input(id="mwh", type="text", inputMode="numeric"),
        html.Div(html.Button("Previsualizar", id="previsualizar"), className="acciones"),
        html.P(id="mensaje", role="status"),
    ], className="panel formulario"),
])


# Los campos son State: se leen cuando se pulsa el botón. La lección
# muestra esos valores en pantalla.
@app.callback(
    Output("mensaje", "children"), Input("previsualizar", "n_clicks"),
    State("region", "value"), State("periodo", "value"), State("mwh", "value"),
    prevent_initial_call=True,
)
def revisar(_clics, region, periodo, mwh):
    if not region or not periodo or not mwh:
        return "Completa los tres campos."
    return f"{region} · {periodo} · {mwh} MWh."


if __name__ == "__main__":
    app.run()
