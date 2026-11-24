"""Lección 7. Dos pestañas y una sola fuente de verdad: SQLite."""

import os
import sqlite3
from pathlib import Path

from dash import ALL, Dash, Input, Output, State, ctx, dcc, html, no_update

import sqlite_consumo as db
from dashboard import IDS_GRAFICOS, contenido_dashboard, filtrar, tabla, vista
from datos import leer_consumo, validar_consumo
from dash.exceptions import PreventUpdate

datos_iniciales = leer_consumo()
REGIONES = sorted(datos_iniciales.region.unique())
RUTA_DB = Path(os.environ.get("CONSUMO_DB", Path(__file__).with_name("consumo_dash.sqlite3")))
db.inicializar(RUTA_DB, datos_iniciales)

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
    html.Section(contenido_dashboard(REGIONES), id="panel-dashboard", className="panel"),
    html.Section([
        html.H2("Registros mensuales"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Label("Filtrar registros por región", htmlFor="region-registros"),
                        dcc.Dropdown(REGIONES, id="region-registros", placeholder="Todas las regiones"),
                    ]),
                    html.Div([
                        html.Label("Página", htmlFor="pagina-registros"),
                        dcc.Input(id="pagina-registros", type="number", value=1, min=1, step=1,
                                  debounce=True),
                    ]),
                ], className="filtros"),
                html.P(id="total-registros"),
                html.Div(id="tabla-registros", className="tabla"),
            ]),
            html.Div([
                html.H3("Formulario"),
                html.P(id="modo", children="Nuevo registro", className="modo"),
                html.Label("Región", htmlFor="region"),
                dcc.Dropdown(REGIONES, id="region", placeholder="Selecciona una región"),
                html.Label("Mes (AAAA-MM)", htmlFor="periodo"),
                dcc.Input(id="periodo", type="text", placeholder="2025-01", maxLength=7),
                html.Label("Consumo (MWh)", htmlFor="mwh"),
                dcc.Input(id="mwh", type="text", inputMode="numeric", maxLength=10),
                html.Div([
                    html.Button("Nuevo", id="nuevo", className="secundario"),
                    html.Button("Guardar", id="guardar"),
                ], className="acciones"),
                html.P(id="mensaje", role="status"),
            ], className="formulario"),
        ], className="gestion-registros"),
    ], id="panel-ingreso", className="panel", hidden=True),
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
                db.eliminar(RUTA_DB, fila_id)
                formulario = limpio if registro_id == fila_id else (no_update,) * 5
                return *formulario, "Registro eliminado.", revision + 1

            fila = db.consultar(RUTA_DB, fila_id)
            if fila is None:
                raise LookupError("El registro ya no existe.")
            modo = f'Editando {fila["region"]} · {fila["periodo"]}'
            return fila_id, fila["region"], fila["periodo"], str(fila["consumo_mwh"]), modo, "", no_update

        valores = validar_consumo(REGIONES, region, periodo, mwh)
        db.guardar(RUTA_DB, registro_id, *valores)
        mensaje = "Registro creado." if registro_id is None else "Registro actualizado."
        return *limpio, mensaje, revision + 1
    except (ValueError, LookupError) as error:
        mensaje = str(error)
    except sqlite3.IntegrityError:
        mensaje = "Ya existe un registro para esa región y mes."
    except sqlite3.OperationalError:
        app.logger.exception("Error de SQLite")
        mensaje = "No se pudo acceder a SQLite. Intenta de nuevo."

    # Tras un error, conservar lo escrito para que pueda corregirse.
    return no_update, no_update, no_update, no_update, no_update, mensaje, no_update


def acciones_fila(fila):
    # Cada ID combina el tipo de acción con la clave primaria de SQLite.
    titulo = f"{fila.region} · {fila.periodo}"
    return [
        html.Button("Editar", id={"accion": "editar", "id": fila.id},
                    className="secundario", n_clicks=0,
                    **{"aria-label": f"Editar {titulo}"}),
        dcc.ConfirmDialogProvider(
            html.Button("Eliminar", className="peligro",
                        **{"aria-label": f"Eliminar {titulo}"}),
            id={"accion": "eliminar", "id": fila.id}, submit_n_clicks=0,
            message=f"¿Eliminar {titulo}?",
        ),
    ]


@app.callback(
    Output("tabla-registros", "children"), Output("total-registros", "children"),
    Output("pagina-registros", "max"),
    Input("revision", "data"), Input("region-registros", "value"),
    Input("pagina-registros", "value"),
)
def actualizar_registros(_revision, region, pagina):
    filas = filtrar(db.listar(RUTA_DB), region, None).sort_values(
        ["periodo", "region"], ascending=[False, True],
    )
    paginas = max(1, (len(filas) + 19) // 20)
    pagina = min(max(1, int(pagina or 1)), paginas)
    inicio = (pagina - 1) * 20
    detalle = f"{len(filas)} registros · Página {pagina} de {paginas}"
    return tabla(filas.iloc[inicio:inicio + 20], acciones_fila), detalle, paginas


@app.callback(Output("filtro-anio", "options"), Input("revision", "data"))
def actualizar_anios(_revision):
    return sorted(db.listar(RUTA_DB).periodo.str[:4].unique())


@app.callback(
    Output("resumen", "children"),
    *[Output(id_grafico, "figure") for id_grafico in IDS_GRAFICOS],
    Output("tabla", "children"),
    Input("filtro-region", "value"), Input("filtro-anio", "value"),
    Input("revision", "data"),
)
def actualizar_dashboard(region, anio, _revision):
    # La revisión invalida el dashboard aunque el formulario esté visible.
    return vista(filtrar(db.listar(RUTA_DB), region, anio))


if __name__ == "__main__":
    app.run()
