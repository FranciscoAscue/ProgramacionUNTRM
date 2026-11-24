# Tutorial de Dash con Python

Construirás una app de consumo eléctrico mensual en siete lecciones. Todas usan el [CSV compartido](datos/consumo_electrico.csv), con valores ficticios en MWh para 12 regiones del Perú. Ejecuta los comandos desde la raíz del proyecto y detén cada servidor con Ctrl+C antes de abrir el siguiente. Usa `conda activate dash` y abre `http://127.0.0.1:8050`.

## 1. Cargar la tabla y construir el layout

Ejecuta `python -B ejemplos/01_layout.py`. Abre [01_layout.py](ejemplos/01_layout.py) y sigue la lectura del CSV, el filtro fijo de Lima y la construcción de `app.layout`. Los elementos `html.*` organizan la página y `dcc.Graph` recibe una figura de Plotly.

**Práctica.** Cambia Lima por Cusco en el filtro y en el título. Identifica qué código se ejecuta al arrancar.

## 2. Conectar un selector a un gráfico

Ejecuta `python -B ejemplos/02_callback.py`. En [02_callback.py](ejemplos/02_callback.py), `Input("region", "value")` observa el selector y `Output("grafico", "figure")` recibe el valor devuelto. Los identificadores del decorador coinciden con los del layout. Dash ejecuta el callback con el valor inicial y cada vez que cambia la región.

**Práctica.** Cambia la región inicial a Piura. Explica qué recibe el callback cuando eliges Arequipa.

## 3. Preparar cuatro gráficos

Ejecuta `python -B ejemplos/03_graficos.py`. Revisa [03_graficos.py](ejemplos/03_graficos.py) y las funciones de [dashboard.py](ejemplos/dashboard.py). `groupby().sum()` agrega regiones por mes, meses por región o meses por año. `pivot()` convierte la tabla en una matriz para el mapa de calor. Contrasta las figuras creadas con Plotly Express y la traza `go.Heatmap`.

**Práctica.** Filtra el CSV a dos regiones antes de llamar a `graficos()`. Predice qué barras y qué filas del mapa de calor aparecerán.

## 4. Leer y validar un formulario

Ejecuta `python -B ejemplos/04_formulario.py`. En [04_formulario.py](ejemplos/04_formulario.py), el clic es el `Input` y los valores de los campos son `State`. Escribir en un campo no ejecuta la validación hasta pulsar **Validar**. `prevent_initial_call=True` evita la ejecución inicial del callback.

**Práctica.** Prueba `2025-13`, un consumo negativo y un cero. Revisa cómo [datos.py](ejemplos/datos.py) convierte el texto a un entero después de validarlo.

## 5. Unificar filtros, indicadores, gráficos y tabla

Ejecuta `python -B ejemplos/05_dashboard.py`. En [05_dashboard.py](ejemplos/05_dashboard.py), el callback recibe dos filtros y produce los indicadores, cuatro figuras y una tabla. El orden del resultado coincide con el de las salidas del decorador. Todas las salidas usan el mismo subconjunto de datos.

**Práctica.** Filtra por Áncash y 2023. Comprueba que los 12 meses de la tabla coinciden con el indicador de registros. Quita el filtro de región y explica cómo cambian ambos.

## 6. Obtener datos con una consulta SQLite

Ejecuta `python -B ejemplos/06_sqlite_lectura.py`. En [06_sqlite_lectura.py](ejemplos/06_sqlite_lectura.py), SQLite carga el CSV en memoria. `WHERE region = ?` aplica el filtro con un parámetro. `GROUP BY` calcula los totales anuales antes de que Plotly construya la figura. Cerrar la conexión elimina la base temporal.

**Práctica.** Compara un total anual con el de la lección 5 usando la misma región y año. Reemplaza `SUM` por `AVG` y actualiza las etiquetas para representar el promedio mensual.

## 7. Construir un CRUD persistente con acciones por fila

Ejecuta `python -B ejemplos/07_sqlite_crud.py`. Abre [07_sqlite_crud.py](ejemplos/07_sqlite_crud.py) y [sqlite_consumo.py](ejemplos/sqlite_consumo.py). Las pestañas **Dashboard** e **Ingreso de datos** conservan sus componentes al cambiar de vista.

1. **Nuevo** prepara el formulario para un `INSERT`. **Editar**, a la derecha de una fila, carga sus campos usando su ID y prepara un `UPDATE`.
2. Cada botón de fila tiene un ID de diccionario con la acción y la clave primaria. `ALL` escucha los botones generados y `ctx.triggered_id` identifica la fila pulsada, incluso si cambia el filtro o la página.
3. **Eliminar**, en la misma columna, requiere confirmación antes del `DELETE`. `dcc.Store` guarda el ID en edición y otro Store guarda la revisión que activa la recarga de datos después de una escritura exitosa.
4. SQLite impide duplicados de región y mes. El dashboard y la tabla administrativa vuelven a consultar la base.

**Práctica.** Crea Piura, `2025-01`, con 190000 MWh. Localiza la fila al inicio de la tabla, pulsa **Editar** y guarda 195000. Reinicia la app y comprueba el cambio. Pulsa **Eliminar**, cancela una vez y luego confirma. Revisa el dashboard después de cada escritura.

La base predeterminada es `ejemplos/consumo_dash.sqlite3`. Para repetir la práctica desde la semilla, usa otra ruta mediante `CONSUMO_DB`. Consulta el [índice general](README.md) o el [tutorial equivalente de Shiny](TUTORIAL_SHINY.md).
