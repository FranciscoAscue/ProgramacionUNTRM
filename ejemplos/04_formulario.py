"""Lección 4. Botón, State y validación de un formulario."""

from dash import Dash, Input, Output, State, dcc, html

from datos import leer_consumo, validar_consumo

regiones = sorted(leer_consumo().region.unique())
app = Dash(__name__, title="Consumo eléctrico · Formulario")
app.layout = html.Main([
    html.H1("Validar un registro de consumo"),
    html.Section([
        html.Label("Región", htmlFor="region"),
        dcc.Dropdown(regiones, id="region"),
        html.Label("Mes (AAAA-MM)", htmlFor="periodo"),
        dcc.Input(id="periodo", type="text", placeholder="2025-01"),
        html.Label("Consumo (MWh)", htmlFor="mwh"),
        dcc.Input(id="mwh", type="text", inputMode="numeric"),
        html.Div(html.Button("Validar", id="validar"), className="acciones"),
        html.P(id="mensaje", role="status"),
    ], className="panel formulario"),
])


# Los campos son State: se leen cuando se pulsa el botón. La lección
# solo valida y muestra el resultado, sin escribir una fila en la base.
@app.callback(
    Output("mensaje", "children"), Input("validar", "n_clicks"),
    State("region", "value"), State("periodo", "value"), State("mwh", "value"),
    prevent_initial_call=True,
)
def revisar(_clics, region, periodo, mwh):
    try:
        region, periodo, mwh = validar_consumo(regiones, region, periodo, mwh)
    except ValueError as error:
        return str(error)
    return f"Registro válido: {region} · {periodo} · {mwh} MWh."


if __name__ == "__main__":
    app.run()
