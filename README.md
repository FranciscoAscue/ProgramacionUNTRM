# Taller de consumo eléctrico con Dash y R Shiny

Dos recorridos de siete lecciones sobre el mismo [CSV de consumo eléctrico](datos/consumo_electrico.csv). Contiene 432 observaciones ficticias de 12 regiones del Perú, de enero de 2022 a diciembre de 2024. Cada fila representa una región y un mes. La columna `consumo_mwh` usa megavatios hora.

- [Tutorial de Dash con Python](TUTORIAL_DASH.md)
- [Tutorial de Shiny con R](TUTORIAL_SHINY.md)

| Lección | Dash | Shiny |
| --- | --- | --- |
| 1. Tabla, layout y gráfico inicial | [Python](ejemplos/01_layout.py) | [R](r_shiny/01_layout.R) |
| 2. Un selector y una salida reactiva | [Python](ejemplos/02_callback.py) | [R](r_shiny/02_reactividad.R) |
| 3. Agregaciones y cuatro gráficos | [Python](ejemplos/03_graficos.py) | [R](r_shiny/03_graficos.R) |
| 4. Formulario y lectura al pulsar un botón | [Python](ejemplos/04_formulario.py) | [R](r_shiny/04_formulario.R) |
| 5. Dashboard con filtros y múltiples salidas | [Python](ejemplos/05_dashboard.py) | [R](r_shiny/05_dashboard.R) |
| 6. Consultas parametrizadas en SQLite | [Python](ejemplos/06_sqlite_lectura.py) | [R](r_shiny/06_sqlite_lectura.R) |
| 7. CRUD con pestañas y acciones por fila | [Python](ejemplos/07_sqlite_crud.py) | [R](r_shiny/07_sqlite_crud.R) |

## Abrir las versiones finales

Desde la raíz del proyecto, para Dash:

```bash
conda activate dash
python -B ejemplos/07_sqlite_crud.py
```

Abre `http://127.0.0.1:8050`. Para Shiny, usa R desde la misma carpeta:

```bash
Rscript r_shiny/07_sqlite_crud.R
```

Shiny usa el puerto 3838 para el CRUD e imprime la URL. Los paquetes necesarios son `shiny`, `ggplot2`, `DBI` y `RSQLite`. Para instalarlos en otra máquina, ejecuta `install.packages(c("shiny", "ggplot2", "DBI", "RSQLite"))`.

En **Ingreso de datos**, el botón **Nuevo** prepara el formulario. La última columna de la tabla contiene **Editar** y **Eliminar** para cada fila. Usa el filtro de región y el número de página para localizar registros. El **Dashboard** presenta evolución mensual, barras por región, barras por año y mapa de calor, con filtros de región y año.

Las versiones finales conservan los cambios en sus bases SQLite independientes. Dash usa `ejemplos/consumo_dash.sqlite3` y Shiny usa `r_shiny/consumo_shiny.sqlite3`. Para una práctica con datos nuevos, indica una ruta diferente mediante `CONSUMO_DB`. La app original de Gapminder sigue disponible con `python -B app.py`.
