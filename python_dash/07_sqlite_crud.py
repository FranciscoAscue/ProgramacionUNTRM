"""Lección 7. Dos pestañas y una sola fuente de verdad: SQLite."""

import os
import re
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update
from dash.exceptions import PreventUpdate

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)
regiones = sorted(datos.region.unique())
RUTA_DB = Path(os.environ.get("CONSUMO_DB", Path(__file__).with_name("consumo_dash.sqlite3")))

# El CSV se importa una sola vez. La misma transacción crea y llena la tabla.
with closing(sqlite3.connect(RUTA_DB)) as con, con:
    con.execute("BEGIN IMMEDIATE")
    if con.execute("PRAGMA user_version").fetchone()[0] == 0:
        con.execute("""
            CREATE TABLE consumo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                region TEXT NOT NULL,
                periodo TEXT NOT NULL,
                consumo_mwh INTEGER NOT NULL CHECK (consumo_mwh BETWEEN 0 AND 1000000000),
                UNIQUE (region, periodo)
            )
        """)
        con.executemany(
            "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
            datos[["region", "periodo", "consumo_mwh"]].itertuples(index=False, name=None),
        )
        con.execute("PRAGMA user_version = 1")

app = Dash(__name__, title="Consumo eléctrico · CRUD")
app.layout = html.Main([
    html.H1("Consumo eléctrico por región"),
    html.P("Datos ficticios del Perú · MWh"),
    # Store comunica una escritura exitosa al callback que vuelve a leer SQLite.
    dcc.Store(id="revision", data=0),
    dcc.Store(id="registro"),
    dcc.Tabs(id="pestana", value="dashboard", children=[
        dcc.Tab(label="Dashboard", value="dashboard"),
        dcc.Tab(label="Ingreso de datos", value="ingreso"),
    ]),
    html.Section([
        html.Label("Región", htmlFor="filtro-region"),
        dcc.Dropdown(regiones, id="filtro-region", placeholder="Todas las regiones"),
        html.Label("Año", htmlFor="filtro-anio"),
        dcc.Dropdown([], id="filtro-anio", placeholder="Todos los años"),
        html.Ul(id="resumen"),
        dcc.Graph(id="evolucion"),
        dcc.Graph(id="por-region"),
        dcc.Graph(id="por-anio"),
        dcc.Graph(id="mapa-calor"),
        html.H2("Tabla de consumo"),
        html.Div(id="tabla"),
    ], id="panel-dashboard"),
    html.Section([
        html.H2("Formulario"),
        html.P("Nuevo registro", id="modo"),
        html.Label("Región", htmlFor="region"),
        dcc.Dropdown(regiones, id="region", placeholder="Selecciona una región"),
        html.P([
            html.Label("Mes (AAAA-MM)", htmlFor="periodo"),
            dcc.Input(id="periodo", type="text", placeholder="2025-01", maxLength=7),
        ]),
        html.P([
            html.Label("Consumo (MWh)", htmlFor="mwh"),
            dcc.Input(id="mwh", type="text", inputMode="numeric", maxLength=10),
        ]),
        html.Button("Nuevo", id="nuevo"),
        html.Button("Guardar", id="guardar"),
        html.P(id="mensaje", role="status"),
        html.H2("Registros mensuales"),
        html.Label("Filtrar registros por región", htmlFor="region-registros"),
        dcc.Dropdown(regiones, id="region-registros", placeholder="Todas las regiones"),
        html.P([
            html.Label("Página", htmlFor="pagina-registros"),
            dcc.Input(id="pagina-registros", type="number", value=1, min=1, step=1,
                      debounce=True),
        ]),
        html.P(id="total-registros"),
        html.Div(id="tabla-registros"),
    ], id="panel-ingreso", hidden=True),
])


# Ambas secciones conservan sus componentes y valores al cambiar de pestaña.
@app.callback(
    Output("panel-dashboard", "hidden"), Output("panel-ingreso", "hidden"),
    Input("pestana", "value"),
)
def mostrar_pestana(pestana):
    return pestana != "dashboard", pestana != "ingreso"


# Input dispara la llamada. State lee los valores de los campos cuando se pulsa
# un botón. El id de la fila distingue una creación de una actualización.
@app.callback(
    Output("registro", "data"), Output("region", "value"),
    Output("periodo", "value"), Output("mwh", "value"),
    Output("modo", "children"), Output("mensaje", "children"),
    Output("revision", "data"),
    Input("nuevo", "n_clicks"), Input("guardar", "n_clicks"),
    Input({"accion": "editar", "id": ALL}, "n_clicks"),
    Input({"accion": "eliminar", "id": ALL}, "submit_n_clicks"),
    State("registro", "data"),
    State("region", "value"), State("periodo", "value"),
    State("mwh", "value"), State("revision", "data"),
    prevent_initial_call=True,
)
def gestionar(_nuevo, _guardar, _ediciones, _borrados, registro_id,
              region, periodo, mwh, revision):
    limpio = (None, None, "", "", "Nuevo registro")
    evento = ctx.triggered_id
    # ALL escucha los botones visibles. Montar una nueva página genera
    # valores iniciales de cero, que no representan acciones del usuario.
    if not evento or not ctx.triggered[0]["value"]:
        raise PreventUpdate
    try:
        if evento == "nuevo":
            return *limpio, "", no_update

        if isinstance(evento, dict):
            fila_id = evento["id"]
            if evento["accion"] == "eliminar":
                with closing(sqlite3.connect(RUTA_DB)) as con, con:
                    cursor = con.execute("DELETE FROM consumo WHERE id = ?", (fila_id,))
                    if cursor.rowcount == 0:
                        raise LookupError("El registro ya no existe.")
                formulario = limpio if registro_id == fila_id else (no_update,) * 5
                return *formulario, "Registro eliminado.", revision + 1

            with closing(sqlite3.connect(RUTA_DB)) as con:
                con.row_factory = sqlite3.Row
                fila = con.execute("SELECT * FROM consumo WHERE id = ?", (fila_id,)).fetchone()
            if fila is None:
                raise LookupError("El registro ya no existe.")
            modo = f'Editando {fila["region"]} · {fila["periodo"]}'
            return fila_id, fila["region"], fila["periodo"], str(fila["consumo_mwh"]), modo, "", no_update

        if not region or not periodo or not mwh:
            raise ValueError("Completa los tres campos.")
        if not re.fullmatch(r"(?!0000)[0-9]{4}-(0[1-9]|1[0-2])", periodo) or not mwh.isdecimal():
            raise ValueError("Usa AAAA-MM y un consumo entero en MWh.")

        # Los signos ? reciben los valores del formulario como parámetros.
        with closing(sqlite3.connect(RUTA_DB)) as con, con:
            if registro_id is None:
                con.execute(
                    "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
                    (region, periodo, int(mwh)),
                )
            else:
                cursor = con.execute(
                    "UPDATE consumo SET region = ?, periodo = ?, consumo_mwh = ? WHERE id = ?",
                    (region, periodo, int(mwh), registro_id),
                )
                if cursor.rowcount == 0:
                    raise LookupError("El registro ya no existe.")
        mensaje = "Registro creado." if registro_id is None else "Registro actualizado."
        return *limpio, mensaje, revision + 1
    except (ValueError, LookupError) as error:
        mensaje = str(error)
    except sqlite3.IntegrityError as error:
        mensaje = ("Ya existe un registro para esa región y mes."
                   if error.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_UNIQUE
                   else "El consumo debe estar entre 0 y 1 000 000 000 MWh.")
    except sqlite3.OperationalError:
        app.logger.exception("Error de SQLite")
        mensaje = "No se pudo acceder a SQLite. Intenta de nuevo."

    # Tras un error, conservar lo escrito para que pueda corregirse.
    return no_update, no_update, no_update, no_update, no_update, mensaje, no_update


@app.callback(
    Output("tabla-registros", "children"), Output("total-registros", "children"),
    Output("pagina-registros", "max"),
    Input("revision", "data"), Input("region-registros", "value"),
    Input("pagina-registros", "value"),
)
def actualizar_registros(_revision, region, pagina):
    with closing(sqlite3.connect(RUTA_DB)) as con:
        filas = pd.read_sql_query("""
            SELECT * FROM consumo WHERE (? IS NULL OR region = ?)
            ORDER BY periodo DESC, region
        """, con, params=(region, region))

    paginas = max(1, (len(filas) + 19) // 20)
    pagina = min(max(1, int(pagina or 1)), paginas)
    inicio = (pagina - 1) * 20

    # Cada botón lleva la clave primaria de su fila.
    renglones = []
    for fila in filas.iloc[inicio:inicio + 20].itertuples(index=False):
        titulo = f"{fila.region} · {fila.periodo}"
        editar = html.Button("Editar", id={"accion": "editar", "id": fila.id}, n_clicks=0,
                             **{"aria-label": f"Editar {titulo}"})
        eliminar = dcc.ConfirmDialogProvider(
            html.Button("Eliminar", **{"aria-label": f"Eliminar {titulo}"}),
            id={"accion": "eliminar", "id": fila.id}, submit_n_clicks=0,
            message=f"¿Eliminar {titulo}?",
        )
        renglones.append(html.Tr([
            html.Td(fila.region), html.Td(fila.periodo), html.Td(fila.consumo_mwh),
            html.Td([editar, eliminar]),
        ]))

    tabla = html.Table([
        html.Thead(html.Tr([
            html.Th(columna) for columna in ("Región", "Mes", "Consumo (MWh)", "Acciones")
        ])),
        html.Tbody(renglones),
    ])
    return tabla, f"{len(filas)} registros · Página {pagina} de {paginas}", paginas


@app.callback(Output("filtro-anio", "options"), Input("revision", "data"))
def actualizar_anios(_revision):
    with closing(sqlite3.connect(RUTA_DB)) as con:
        return [anio for (anio,) in con.execute(
            "SELECT DISTINCT substr(periodo, 1, 4) FROM consumo ORDER BY 1"
        )]


@app.callback(
    Output("resumen", "children"),
    Output("evolucion", "figure"),
    Output("por-region", "figure"),
    Output("por-anio", "figure"),
    Output("mapa-calor", "figure"),
    Output("tabla", "children"),
    Input("filtro-region", "value"),
    Input("filtro-anio", "value"),
    Input("revision", "data"),
)
def actualizar_dashboard(region, anio, _revision):
    with closing(sqlite3.connect(RUTA_DB)) as con:
        visibles = pd.read_sql_query("SELECT * FROM consumo", con)
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
        html.Li(f"{etiqueta}: {valor}")
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
