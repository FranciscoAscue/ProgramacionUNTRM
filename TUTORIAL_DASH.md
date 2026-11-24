# Tutorial de Dash con Python

Siete lecciones sobre el [CSV de consumo eléctrico](datos/consumo_electrico.csv). Contiene datos mensuales ficticios de 12 regiones del Perú. Cada ejemplo tiene su propio código de carga, layout y callbacks. Ejecuta los comandos desde la raíz del proyecto con `conda activate dash`, abre `http://127.0.0.1:8050` y detén el servidor con Ctrl+C antes de iniciar otra lección.

Los ejemplos usan los componentes y la apariencia predeterminada del framework.

## 1. Leer el CSV y mostrar un gráfico

Ejecuta `python -B python_dash/01_layout.py`. Este es el bloque de carga y preparación del gráfico en [01_layout.py](python_dash/01_layout.py).

```python
ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)

mensual = datos.groupby("periodo", as_index=False)["consumo_mwh"].sum()
figura = px.line(mensual, x="periodo", y="consumo_mwh", markers=True,
                 labels={"periodo": "Mes", "consumo_mwh": "Consumo (MWh)"})
```

`read_csv` carga todas las filas. `groupby` suma el consumo de las regiones para cada mes. En el layout, `dcc.Graph(figure=figura)` muestra el resultado y `datos.head(12)` limita solo la vista previa de la tabla.

**Práctica.** Cambia 12 por 6 y observa cuál de las dos vistas cambia.

## 2. Conectar un selector al gráfico

Ejecuta `python -B python_dash/02_callback.py`. En [02_callback.py](python_dash/02_callback.py), el selector empieza vacío. El filtro se aplica dentro del callback al elegir una región.

```python
@app.callback(Output("grafico", "figure"), Input("region", "value"))
def actualizar(region):
    visibles = datos[datos.region == region] if region else datos
    mensual = visibles.groupby("periodo", as_index=False)["consumo_mwh"].sum()
    return px.line(mensual, x="periodo", y="consumo_mwh", markers=True,
                   labels={"periodo": "Mes", "consumo_mwh": "Consumo (MWh)"})
```

`Input` escucha el valor de `region`. `Output` coloca la figura devuelta en el gráfico que tiene ID `grafico`.

**Práctica.** Selecciona Piura y después borra la selección. Compara los valores mensuales.

## 3. Construir cuatro gráficos

Ejecuta `python -B python_dash/03_graficos.py`. En [03_graficos.py](python_dash/03_graficos.py), cada agregación prepara una vista distinta. La matriz se usa para el mapa de calor.

```python
mensual = datos.groupby("periodo", as_index=False)["consumo_mwh"].sum()
regional = datos.groupby("region", as_index=False)["consumo_mwh"].sum()
con_anio = datos.assign(anio=datos.periodo.str[:4])
anual = con_anio.groupby("anio", as_index=False)["consumo_mwh"].sum()
matriz = datos.pivot(index="region", columns="periodo", values="consumo_mwh")
```

La línea usa `mensual`, las barras usan `regional` y `anual`, y cada celda del mapa representa una combinación de región y mes.

**Práctica.** Cambia `sum()` por `mean()` en el cálculo regional y ajusta el título de sus barras.

## 4. Leer los campos al pulsar un botón

Ejecuta `python -B python_dash/04_formulario.py`. Este callback de [04_formulario.py](python_dash/04_formulario.py) muestra una vista previa del registro.

```python
@app.callback(
    Output("mensaje", "children"), Input("previsualizar", "n_clicks"),
    State("region", "value"), State("periodo", "value"), State("mwh", "value"),
    prevent_initial_call=True,
)
def revisar(_clics, region, periodo, mwh):
    if not region or not periodo or not mwh:
        return "Completa los tres campos."
    return f"{region} · {periodo} · {mwh} MWh."
```

El botón dispara el callback. Los campos declarados como `State` entregan sus valores en ese momento. `prevent_initial_call` espera al primer clic.

**Práctica.** Previsualiza Piura, `2025-01` y `0`. Cambia el consumo y observa cuándo se actualiza el mensaje.

## 5. Actualizar varias salidas con dos filtros

Ejecuta `python -B python_dash/05_dashboard.py`. En [05_dashboard.py](python_dash/05_dashboard.py), los filtros empiezan vacíos. El callback crea un conjunto de filas común para la tabla, los indicadores y los cuatro gráficos.

```python
visibles = datos
if region:
    visibles = visibles[visibles.region == region]
if anio:
    visibles = visibles[visibles.periodo.str.startswith(anio)]
```

El orden del `return` es el mismo que el de los seis `Output`.

```python
return indicadores, linea, barras, por_anio, calor, tabla
```

**Práctica.** Filtra por Áncash y 2023. Comprueba que el indicador y la tabla muestran los mismos 12 registros.

## 6. Guardar el primer registro en SQLite

Ejecuta `python -B python_dash/06_sqlite_ingreso.py`. En [06_sqlite_ingreso.py](python_dash/06_sqlite_ingreso.py), `CREATE TABLE IF NOT EXISTS` define las columnas. La primera vez, el `SELECT` devuelve cero filas. Los ejemplos escritos en los campos son solo sugerencias visibles.

Al pulsar **Guardar**, el callback recibe los campos como `State`, igual que en la lección 4. `INSERT` añade una fila y `commit()` la guarda en el archivo.

```python
con.execute(
    "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
    (region, periodo, int(mwh)),
)
con.commit()
```

Después, el mismo callback consulta la tabla y devuelve sus filas al layout.

```python
datos = pd.read_sql_query("SELECT * FROM consumo ORDER BY id", con)
```

**Práctica.** Comprueba que la tabla está vacía. Escribe Piura, `2025-01` y `190000`, pulsa **Guardar** y observa el ID generado por SQLite. Agrega otra fila, reinicia el servidor y comprueba que las dos filas siguen allí.

La base de esta práctica es `python_dash/ingreso_dash.sqlite3`. Usa `INGRESO_DB` con una ruta que todavía no exista para volver a empezar con cero filas. En la lección 7, la base se prepara con registros de ejemplo para practicar la edición, el borrado y el dashboard.

## 7. Editar y borrar filas con SQLite

Ejecuta `python -B python_dash/07_sqlite_crud.py`. En [07_sqlite_crud.py](python_dash/07_sqlite_crud.py), las pestañas separan el dashboard del formulario y su tabla. Cada botón de fila incluye la clave primaria de SQLite.

```python
Input({"accion": "editar", "id": ALL}, "n_clicks"),
Input({"accion": "eliminar", "id": ALL}, "submit_n_clicks"),
State("registro", "data"),
```

`ALL` escucha los botones de todas las filas visibles. `ctx.triggered_id` indica qué fila disparó el callback. **Editar** consulta sus campos y guarda su ID en `dcc.Store`. **Nuevo** deja el ID vacío. Al guardar, esa diferencia determina qué sentencia SQL se ejecuta.

```python
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
```

**Eliminar** requiere confirmación. Tras guardar o borrar, cambia la revisión en `dcc.Store` y ambas vistas vuelven a consultar SQLite. La base predeterminada es `python_dash/consumo_dash.sqlite3`. Usa `CONSUMO_DB` con otra ruta para repetir la práctica desde el CSV.

**Práctica.** Crea Piura, `2025-01`, con 190000 MWh. Edita la fila a 195000, reinicia la app y comprueba el cambio. Cancela un intento de borrado y confirma el siguiente.

[Índice general](README.md) · [Tutorial de Shiny](TUTORIAL_SHINY.md)
