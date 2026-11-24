"""Lección 3. Una tabla, cuatro formas de agrupar y visualizar."""

from dash import Dash, dcc, html

from dashboard import graficos
from datos import leer_consumo

datos = leer_consumo()
app = Dash(__name__, title="Consumo eléctrico · Gráficos")

# Se construyen las figuras al arrancar. En dashboard.py puedes ver groupby,
# pivot y la configuración gráfica que produce cada una.
app.layout = html.Main([
    html.H1("Cuatro vistas del consumo eléctrico"),
    html.P("Datos ficticios del Perú · MWh"),
    html.Div([dcc.Graph(figure=figura) for figura in graficos(datos)], className="graficos"),
])

if __name__ == "__main__":
    app.run()
