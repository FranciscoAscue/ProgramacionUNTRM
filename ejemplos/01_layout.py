"""Lección 1. Leer una tabla CSV y construir un layout con una figura fija."""

from dash import Dash, dcc, html

from dashboard import evolucion, tabla
from datos import leer_consumo

# En esta lección preparamos los datos una sola vez, al arrancar.
datos = leer_consumo().query("region == 'Lima'")
app = Dash(__name__, title="Consumo eléctrico · Dash básico")

# Cada objeto html.* representa un elemento del árbol de la página.
# dcc.Graph recibe una figura de Plotly y aporta zoom y datos al pasar el ratón.
app.layout = html.Main([
    html.H1("Consumo eléctrico mensual en Lima"),
    html.P("Datos ficticios del Perú · MWh"),
    html.Section(dcc.Graph(figure=evolucion(datos)), className="panel"),
    html.Section([
        html.H2("Primeras 12 filas de Lima"),
        html.Div(tabla(datos.head(12)), className="tabla"),
    ], className="panel"),
])

if __name__ == "__main__":
    app.run()
