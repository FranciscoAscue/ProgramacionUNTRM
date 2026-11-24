"""Lección 5. Conectar dos filtros con varias salidas de Dash."""

from dash import Dash, Input, Output, html

from dashboard import IDS_GRAFICOS, contenido_dashboard, filtrar, vista
from datos import leer_consumo

datos = leer_consumo()
regiones = sorted(datos.region.unique())
anios = sorted(datos.periodo.str[:4].unique())
app = Dash(__name__, title="Consumo eléctrico · Dashboard")

app.layout = html.Main([
    html.H1("Consumo eléctrico por región"),
    html.P("Datos ficticios del Perú · MWh"),
    html.Section(contenido_dashboard(regiones, anios), className="panel"),
])


# Cada Input observa la propiedad value de un componente del layout.
# Los valores devueltos se asignan a los Output en el orden declarado.
@app.callback(
    Output("resumen", "children"),
    *[Output(id_grafico, "figure") for id_grafico in IDS_GRAFICOS],
    Output("tabla", "children"),
    Input("filtro-region", "value"),
    Input("filtro-anio", "value"),
)
def actualizar_dashboard(region, anio):
    return vista(filtrar(datos, region, anio))


if __name__ == "__main__":
    app.run()
