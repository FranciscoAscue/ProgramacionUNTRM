"""Lección 5. Dos entradas actualizan seis salidas del dashboard."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)
regiones = sorted(datos.region.unique())
anios = sorted(datos.periodo.str[:4].unique())

app = Dash(__name__)
app.layout = html.Main([
    html.H1("Consumo eléctrico por región"),
    html.Div([
        html.Div([
            html.Label("Región", htmlFor="filtro-region"),
            dcc.Dropdown(regiones, id="filtro-region", placeholder="Todas las regiones"),
        ]),
        html.Div([
            html.Label("Año", htmlFor="filtro-anio"),
            dcc.Dropdown(anios, id="filtro-anio", placeholder="Todos los años"),
        ]),
    ], className="filtros"),
    html.Div(id="resumen", className="indicadores"),
    html.Div([
        dcc.Graph(id="evolucion"),
        dcc.Graph(id="por-region"),
        dcc.Graph(id="por-anio"),
        dcc.Graph(id="mapa-calor"),
    ], className="graficos"),
    html.H2("Tabla de consumo"),
    html.Div(id="tabla", className="tabla"),
])


# El orden del return coincide con el orden de los Output.
@app.callback(
    Output("resumen", "children"),
    Output("evolucion", "figure"),
    Output("por-region", "figure"),
    Output("por-anio", "figure"),
    Output("mapa-calor", "figure"),
    Output("tabla", "children"),
    Input("filtro-region", "value"),
    Input("filtro-anio", "value"),
)
def actualizar_dashboard(region, anio):
    visibles = datos
    # Con los selectores vacíos se muestran todos los registros.
    if region:
        visibles = visibles[visibles.region == region]
    if anio:
        visibles = visibles[visibles.periodo.str.startswith(anio)]

    # Los gráficos reutilizan las mismas filas, agrupadas de distintas formas.
    mensual = visibles.groupby("periodo", as_index=False)["consumo_mwh"].sum()
    regional = visibles.groupby("region", as_index=False)["consumo_mwh"].sum()
    con_anio = visibles.assign(anio=visibles.periodo.str[:4])
    anual = con_anio.groupby("anio", as_index=False)["consumo_mwh"].sum()
    matriz = visibles.pivot(index="region", columns="periodo", values="consumo_mwh")

    linea = px.line(mensual, x="periodo", y="consumo_mwh", title="Evolución mensual", markers=True)
    barras = px.bar(regional.sort_values("consumo_mwh"), x="consumo_mwh", y="region",
                    orientation="h", title="Consumo por región")
    por_anio = px.bar(anual, x="anio", y="consumo_mwh", title="Consumo por año")
    calor = go.Figure(go.Heatmap(x=matriz.columns.tolist(), y=matriz.index.tolist(),
                                 z=matriz.to_numpy(), colorscale="Teal", colorbar={"title": "MWh"}))
    linea.update_xaxes(type="category", nticks=10, title="Mes")
    linea.update_yaxes(title="MWh")
    barras.update_xaxes(title="MWh")
    barras.update_yaxes(title="Región")
    por_anio.update_xaxes(title="Año", type="category")
    por_anio.update_yaxes(title="MWh")
    calor.update_layout(title="Consumo por región y mes")
    calor.update_xaxes(type="category", nticks=10, title="Mes")
    calor.update_yaxes(type="category", title="Región")

    indicadores = [
        html.Div([html.Span(etiqueta), html.Strong(f"{valor:,}".replace(",", " "))],
                 className="indicador")
        for etiqueta, valor in [
            ("Consumo total (MWh)", visibles.consumo_mwh.sum()),
            ("Regiones", visibles.region.nunique()),
            ("Registros", len(visibles)),
        ]
    ]
    tabla = html.Table([
        html.Thead(html.Tr([html.Th(columna) for columna in ("Región", "Mes", "Consumo (MWh)")])),
        html.Tbody([
            html.Tr([html.Td(fila.region), html.Td(fila.periodo),
                     html.Td(f"{fila.consumo_mwh:,}".replace(",", " "))])
            for fila in visibles.itertuples(index=False)
        ]),
    ])
    return indicadores, linea, barras, por_anio, calor, tabla


if __name__ == "__main__":
    app.run()
