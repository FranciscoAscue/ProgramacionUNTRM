"""Transformaciones de la tabla y figuras que reutilizan los ejemplos."""

import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html


def filtros(regiones, anios=None):
    # El valor por defecto de cada dropdown es None: no aplica ese filtro.
    return html.Div([
        html.Div([
            html.Label("Región", htmlFor="filtro-region"),
            dcc.Dropdown(regiones, id="filtro-region", placeholder="Todas las regiones"),
        ]),
        html.Div([
            html.Label("Año", htmlFor="filtro-anio"),
            dcc.Dropdown(anios or [], id="filtro-anio", placeholder="Todos los años"),
        ]),
    ], className="filtros")


def filtrar(datos, region, anio):
    if region:
        datos = datos[datos.region.eq(region)]
    if anio:
        datos = datos[datos.periodo.str.startswith(anio + "-")]
    return datos


def formatear(figura, titulo):
    figura.update_layout(
        title=titulo, template="plotly_white", margin=dict(l=64, r=24, t=62, b=55),
        colorway=["#007e80", "#ad602d", "#3857a6", "#bf4177"],
    )
    return figura


def evolucion(datos):
    # Los totales nacionales de la muestra suman una fila por región y mes.
    mensual = datos.groupby("periodo", as_index=False).consumo_mwh.sum()
    figura = px.line(mensual, x="periodo", y="consumo_mwh", markers=True,
                     labels={"periodo": "Mes", "consumo_mwh": "Consumo (MWh)"})
    figura.update_xaxes(type="category", nticks=10)
    figura.update_yaxes(tickformat="~s")
    return formatear(figura, "Evolución mensual")


def graficos(datos):
    if datos.empty:
        # Mantener los cuatro outputs con una figura legible cuando el filtro queda vacío.
        return tuple(
            formatear(go.Figure().add_annotation(text="Sin registros para este filtro",
                       x=.5, y=.5, xref="paper", yref="paper", showarrow=False), titulo)
            for titulo in ("Evolución mensual", "Consumo por región",
                           "Consumo por año", "Consumo por región y mes")
        )

    etiquetas = {"region": "Región", "periodo": "Mes", "anio": "Año",
                 "consumo_mwh": "Consumo (MWh)"}
    por_region = datos.groupby("region", as_index=False).consumo_mwh.sum()
    barras = px.bar(por_region.sort_values("consumo_mwh"), x="consumo_mwh",
                    y="region", orientation="h", labels=etiquetas)
    barras.update_xaxes(tickformat="~s")

    por_anio = datos.assign(anio=datos.periodo.str[:4])
    por_anio = por_anio.groupby("anio", as_index=False).consumo_mwh.sum()
    anual = px.bar(por_anio, x="anio", y="consumo_mwh", labels=etiquetas)
    anual.update_xaxes(type="category")
    anual.update_yaxes(tickformat="~s")

    # pivot convierte filas región-mes en una matriz. Los faltantes quedan vacíos.
    matriz = datos.pivot(index="region", columns="periodo", values="consumo_mwh")
    calor = go.Figure(go.Heatmap(
        z=matriz.to_numpy(), x=matriz.columns.tolist(), y=matriz.index.tolist(),
        colorscale="Teal", colorbar={"title": "MWh"},
        hovertemplate="%{y} · %{x}<br>%{z:,} MWh<extra></extra>",
    ))
    calor.update_xaxes(type="category", nticks=10, title_text="Mes")
    calor.update_yaxes(type="category", title_text="Región")
    return (
        evolucion(datos), formatear(barras, "Consumo por región"),
        formatear(anual, "Consumo por año"), formatear(calor, "Consumo por región y mes"),
    )


def contenido_dashboard(regiones, anios=None):
    return [
        filtros(regiones, anios),
        html.Div(id="resumen", className="indicadores"),
        html.Div([dcc.Graph(id=id_grafico, config={"displaylogo": False}) for id_grafico in IDS_GRAFICOS],
                 className="graficos"),
        html.H2("Tabla de consumo"),
        html.Div(id="tabla", className="tabla"),
    ]


IDS_GRAFICOS = ("evolucion", "por-region", "por-anio", "mapa-calor")


def numero(valor):
    return f"{valor:,.0f}".replace(",", " ")


def tabla(datos, acciones=None):
    if datos.empty:
        return html.P("No hay filas para los filtros actuales.")
    encabezados = ["Región", "Mes", "Consumo (MWh)"]
    if acciones is not None:
        encabezados.append("Acciones")

    filas = []
    for fila in datos.itertuples(index=False):
        celdas = [html.Td(fila.region), html.Td(fila.periodo),
                  html.Td(numero(fila.consumo_mwh))]
        if acciones is not None:
            celdas.append(html.Td(acciones(fila), className="acciones-fila"))
        filas.append(html.Tr(celdas))
    return html.Table([
        html.Thead(html.Tr([html.Th(c, scope="col") for c in encabezados])),
        html.Tbody(filas),
    ])


def vista(datos):
    # Un único subconjunto alimenta todas las salidas del dashboard.
    indicadores = [
        html.Div([html.Span(etiqueta), html.Strong(numero(valor))], className="indicador")
        for etiqueta, valor in [
            ("Consumo total (MWh)", datos.consumo_mwh.sum()),
            ("Regiones", datos.region.nunique()),
            ("Registros", len(datos)),
        ]
    ]
    return indicadores, *graficos(datos), tabla(datos)
