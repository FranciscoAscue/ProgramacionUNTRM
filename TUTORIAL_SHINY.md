# Tutorial de Shiny con R

Construirás una app de consumo eléctrico mensual en siete lecciones. Usa el [CSV compartido](datos/consumo_electrico.csv), con valores ficticios en MWh para 12 regiones del Perú. Ejecuta los comandos con `Rscript` desde la raíz del proyecto. Abre la URL impresa en la terminal y detén cada servidor con Ctrl+C antes de abrir el siguiente. Los paquetes son `shiny`, `ggplot2`, `DBI` y `RSQLite`.

Los ejemplos usan los componentes y la apariencia predeterminada del framework.

## 1. Separar la interfaz del servidor

Ejecuta `Rscript r_shiny/01_layout.R`. En [01_layout.R](r_shiny/01_layout.R), la UI reserva espacios con `plotOutput()` y `tableOutput()`. `server` los llena con `renderPlot()` y `renderTable()`. Cada identificador conecta el espacio de la UI con su salida.

```r
output$evolucion <- renderPlot(evolucion(datos), alt = "Evolución mensual en Lima")
output$tabla <- renderTable(tabla_visible(head(datos, 12)), digits = 0)
```

**Práctica.** Muestra solo seis filas de Lima y cambia el título de la tabla. Identifica qué cambio va en la UI y cuál en el servidor.

## 2. Hacer reactivo un gráfico

Ejecuta `Rscript r_shiny/02_reactividad.R`. En [02_reactividad.R](r_shiny/02_reactividad.R), `selectInput()` define el selector. Leer `input$region` dentro de `renderPlot()` registra una dependencia. Cuando cambia la región, Shiny vuelve a calcular el gráfico.

```r
output$grafico <- renderPlot({
  evolucion(filtrar(datos, input$region, ""))
}, alt = "Consumo eléctrico por mes")
```

**Práctica.** Selecciona Piura como valor inicial. Compara qué ocurre cuando cambias el selector y cuando solo mueves el puntero sobre la figura.

## 3. Construir cuatro gráficos con ggplot2

Ejecuta `Rscript r_shiny/03_graficos.R`. Lee [03_graficos.R](r_shiny/03_graficos.R) y las funciones de [dashboard.R](r_shiny/dashboard.R). `aggregate()` prepara sumas por periodo, región o año. Las capas `geom_line()`, `geom_col()` y `geom_tile()` representan la evolución, las comparaciones y el mapa de calor.

```r
output$mensual <- renderPlot(evolucion(datos))
output$regional <- renderPlot(por_region(datos))
output$anual <- renderPlot(por_anio(datos))
output$calor <- renderPlot(mapa_calor(datos))
```

**Práctica.** Limita los datos a 2023 antes de llamar a las funciones. Explica qué sigue mostrando cada gráfico y qué comparación se reduce a una barra.

## 4. Esperar un evento antes de validar

Ejecuta `Rscript r_shiny/04_formulario.R`. En [04_formulario.R](r_shiny/04_formulario.R), `bindEvent()` hace que la expresión reactiva lea el formulario cuando se pulsa **Validar**. `ignoreInit = TRUE` evita que se valide al abrir la página. El resultado se muestra mediante `renderText()`.

```r
resultado <- bindEvent(reactive({
  tryCatch({
    consumo <- validar_campos(regiones, input$region, input$periodo, input$mwh)
    paste0("Registro válido: ", input$region, " · ", trimws(input$periodo), " · ", consumo, " MWh.")
  }, error = function(error) conditionMessage(error))
}), input$validar, ignoreInit = TRUE)
output$mensaje <- renderText(resultado())
```

**Práctica.** Prueba `2025-13`, un consumo negativo y un cero. Después de validar, cambia un campo sin volver a pulsar el botón y explica el resultado.

## 5. Compartir un conjunto de datos reactivo

Ejecuta `Rscript r_shiny/05_dashboard.R`. Revisa [05_dashboard.R](r_shiny/05_dashboard.R). La expresión `reactive()` filtra por región y año. Los indicadores, las cuatro figuras y la tabla leen `visibles()`. Si cambia un filtro, Shiny vuelve a calcular las salidas dependientes.

```r
visibles <- reactive(filtrar(datos, input$filtro_region, input$filtro_anio))
servidor_dashboard(output, visibles)
```

**Práctica.** Filtra por Áncash y 2023. Comprueba que aparecen 12 registros y explica qué elimina cada filtro.

## 6. Guardar el primer registro en SQLite

Ejecuta `Rscript r_shiny/06_sqlite_ingreso.R`. En [06_sqlite_ingreso.R](r_shiny/06_sqlite_ingreso.R), `CREATE TABLE IF NOT EXISTS` define las columnas para una base nueva. La primera consulta devuelve cero filas. Los ejemplos escritos en los campos son solo sugerencias visibles.

`observeEvent(input$guardar, ...)` espera el clic y lee, en ese momento, los valores del formulario de la lección 4.

```r
dbExecute(con,
  "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
  params = list(input$region, input$periodo, input$mwh)
)
datos(dbGetQuery(con, "SELECT * FROM consumo ORDER BY id"))
mensaje("Registro guardado.")
```

`dbExecute()` inserta la fila usando los valores de `params`. `dbGetQuery()` vuelve a consultar SQLite y actualiza `datos()`, que alimenta `renderTable()`.

**Práctica.** Comprueba que la tabla está vacía. Escribe Piura, `2025-01` y `190000`, guarda y observa el ID asignado. Añade otra fila y reinicia para comprobar la persistencia.

La base de esta práctica es `r_shiny/ingreso_shiny.sqlite3`. Usa `INGRESO_DB` con una ruta nueva para empezar de nuevo. La lección 7 usa una base preparada con datos de ejemplo para practicar el CRUD y el dashboard.

## 7. Crear un CRUD con acciones por fila

Ejecuta `Rscript r_shiny/07_sqlite_crud.R`. Revisa [07_sqlite_crud.R](r_shiny/07_sqlite_crud.R) y [sqlite_consumo.R](r_shiny/sqlite_consumo.R). `tabsetPanel()` separa el dashboard del ingreso de datos.

1. **Nuevo** limpia el formulario. **Editar**, a la derecha de cada fila, carga el registro mediante su clave primaria. **Guardar** llama a un `INSERT` o `UPDATE` según el modo del formulario.
2. `renderUI()` construye la tabla con botones. Cada botón usa `Shiny.setInputValue()` para enviar la acción y el ID. `observeEvent()` procesa el evento aunque la tabla esté filtrada o paginada.
3. **Eliminar** abre un modal. Solo la confirmación ejecuta el `DELETE`. Un `reactiveVal()` incrementa la revisión después de una escritura, por lo que el dashboard y la tabla vuelven a leer SQLite.
4. DBI enlaza los parámetros de las consultas y SQLite impide duplicados para una misma región y mes.

```r
filas <- reactive({
  revision()
  listar(ruta)
})
visibles <- reactive(filtrar(filas(), input$filtro_region, input$filtro_anio))
servidor_dashboard(output, visibles)
```

**Práctica.** Crea Piura, `2025-01`, con 190000 MWh. Pulsa **Editar** en la fila y cambia el consumo a 195000. Reinicia para comprobar que el dato sigue disponible. Prueba **Eliminar** primero cancelando y luego confirmando.

La base predeterminada es `r_shiny/consumo_shiny.sqlite3`. Para repetir la práctica desde la semilla, usa otra ruta mediante `CONSUMO_DB`. Consulta el [índice general](README.md) o el [tutorial equivalente de Dash](TUTORIAL_DASH.md).
