"""Lección 2. Un selector cambia una figura mediante Input y Output."""

from dash import Dash, Input, Output, dcc, html

from dashboard import evolucion, filtrar
from datos import leer_consumo

datos = leer_consumo()
app = Dash(__name__, title="Consumo eléctrico · Callback")
app.layout = html.Main([
    html.H1("Evolución mensual por región"),
    html.Label("Región", htmlFor="region"),
    dcc.Dropdown(sorted(datos.region.unique()), "Lima", id="region", clearable=False),
    dcc.Graph(id="grafico"),
])

# El ID conecta estos argumentos con los componentes del layout.
# Cambiar region.value vuelve a ejecutar la función y actualiza grafico.figure.
@app.callback(Output("grafico", "figure"), Input("region", "value"))
def actualizar(region):
    return evolucion(filtrar(datos, region, None))


if __name__ == "__main__":
    app.run()
