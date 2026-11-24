# Lección 7. Separar la vista de ingreso y el dashboard, con SQLite detrás.
source("r_shiny/dashboard.R", encoding = "UTF-8")
source("r_shiny/sqlite_consumo.R", encoding = "UTF-8")

datos_iniciales <- leer_consumo()
regiones <- sort(unique(datos_iniciales$region))
ruta <- Sys.getenv("CONSUMO_DB", "r_shiny/consumo_shiny.sqlite3")
inicializar(ruta, datos_iniciales)

ui <- pagina(
  tabsetPanel(
    tabPanel("Dashboard", ui_dashboard(regiones)),
    tabPanel("Ingreso de datos",
      h2("Formulario"),
      textOutput("modo"),
      selectInput("region", "Región", c("Selecciona una región" = "", regiones)),
      textInput("periodo", "Mes (AAAA-MM)", placeholder = "2025-01"),
      textInput("mwh", "Consumo (MWh)"),
      actionButton("nuevo", "Nuevo"),
      actionButton("guardar", "Guardar"),
      div(role = "status", textOutput("mensaje")),
      h2("Registros mensuales"),
      selectInput("region_registros", "Filtrar registros por región",
                  c("Todas las regiones" = "", regiones)),
      numericInput("pagina_registros", "Página", 1, min = 1, step = 1),
      textOutput("total_registros"),
      uiOutput("tabla_registros")
    )
  )
)

# Cada botón envía un evento con el ID estable de la fila, no su posición.
# El ID proviene de SQLite y se convierte a entero al crear el atributo JS.
boton_fila <- function(accion, fila) {
  evento <- sprintf("Shiny.setInputValue('accion_fila', {tipo: '%s', id: %d}, {priority: 'event'})",
                    accion, fila$id)
  tags$button(type = "button", onclick = evento,
              `aria-label` = paste(accion, fila$region, "·", fila$periodo),
              accion)
}

server <- function(input, output, session) {
  # Cada sesión conserva el registro seleccionado y su propio contador de cambios.
  revision <- reactiveVal(0L)
  editando <- reactiveVal(NULL)
  confirmar_id <- reactiveVal(NULL)
  mensaje <- reactiveVal("")

  filas <- reactive({
    revision()
    listar(ruta)
  })
  visibles <- reactive(filtrar(filas(), input$filtro_region, input$filtro_anio))
  servidor_dashboard(output, visibles)

  output$modo <- renderText({
    if (is.null(editando())) "Nuevo registro" else paste("Editando", editando()$titulo)
  })
  output$mensaje <- renderText(mensaje())

  limpiar <- function() {
    editando(NULL)
    updateSelectInput(session, "region", selected = "")
    updateTextInput(session, "periodo", value = "")
    updateTextInput(session, "mwh", value = "")
  }

  observeEvent(filas(), {
    datos <- filas()
    disponibles <- anios(datos)
    actual <- input$filtro_anio
    updateSelectInput(session, "filtro_anio", choices = c("Todos los años" = "", disponibles),
                      selected = if (isTRUE(actual %in% disponibles)) actual else "")
  })

  pagina_registros <- reactive({
    datos <- filtrar(filas(), input$region_registros, "")
    datos <- datos[order(datos$periodo, decreasing = TRUE, method = "radix"), ]
    paginas <- max(1L, ceiling(nrow(datos) / 20))
    solicitada <- input$pagina_registros
    pagina <- if (is.null(solicitada) || !is.finite(solicitada)) 1L else
      min(max(1L, floor(solicitada)), paginas)
    inicio <- (pagina - 1) * 20
    indices <- seq_len(min(20L, nrow(datos) - inicio)) + inicio
    list(filas = datos[indices, ], texto = sprintf("%d registros · Página %d de %d",
                                                   nrow(datos), pagina, paginas))
  })

  output$total_registros <- renderText(pagina_registros()$texto)
  output$tabla_registros <- renderUI({
    # renderUI permite incluir botones interactivos en la columna Acciones.
    datos <- pagina_registros()$filas
    if (!nrow(datos)) return(p("No hay filas para los filtros actuales."))
    tags$table(
      tags$thead(tags$tr(lapply(c("Región", "Mes", "Consumo (MWh)", "Acciones"),
                                 tags$th, scope = "col"))),
      tags$tbody(lapply(seq_len(nrow(datos)), function(i) {
        fila <- datos[i, ]
        tags$tr(tags$td(fila$region), tags$td(fila$periodo),
                tags$td(numero(fila$consumo_mwh)),
                tags$td(
                  boton_fila("Editar", fila), " ",
                  boton_fila("Eliminar", fila)
                ))
      }))
    )
  })

  observeEvent(input$accion_fila, {
    accion <- input$accion_fila
    fila <- consultar(ruta, accion$id)
    if (nrow(fila) == 0L) {
      mensaje("El registro ya no existe.")
      return()
    }
    titulo <- paste(fila$region, fila$periodo, sep = " · ")
    if (identical(accion$tipo, "Eliminar")) {
      confirmar_id(as.character(fila$id))
      showModal(modalDialog(
        title = "Eliminar registro", paste0("¿Eliminar ", titulo, "?"),
        footer = tagList(modalButton("Cancelar"), actionButton("confirmar", "Confirmar"))
      ))
      return()
    }
    editando(list(id = as.character(fila$id), titulo = titulo))
    updateSelectInput(session, "region", selected = fila$region)
    updateTextInput(session, "periodo", value = fila$periodo)
    updateTextInput(session, "mwh", value = as.character(fila$consumo_mwh))
    mensaje("")
  })

  observeEvent(input$nuevo, {
    limpiar()
    mensaje("")
  })

  # observeEvent ejecuta la escritura al pulsar el botón, el equivalente a
  # usar el botón como Input y los campos como State en el ejemplo Dash.
  observeEvent(input$guardar, {
    tryCatch({
      periodo <- trimws(input$periodo)
      mwh <- validar_campos(regiones, input$region, periodo, input$mwh)
      id <- editando()$id
      guardar(ruta, id, input$region, periodo, mwh)
      limpiar()
      mensaje(if (is.null(id)) "Registro creado." else "Registro actualizado.")
      revision(revision() + 1L)
    }, error = function(e) {
      texto <- conditionMessage(e)
      mensaje(if (grepl("UNIQUE constraint failed", texto, fixed = TRUE))
        "Ya existe un registro para esa región y mes." else texto)
    })
  })

  observeEvent(input$confirmar, {
    id <- confirmar_id()
    req(!is.null(id))
    confirmar_id(NULL)
    removeModal()
    tryCatch({
      eliminar(ruta, id)
      if (identical(editando()$id, id)) limpiar()
      mensaje("Registro eliminado.")
      revision(revision() + 1L)
    }, error = function(e) mensaje(conditionMessage(e)))
  }, ignoreInit = TRUE)
}

runApp(shinyApp(ui, server), host = "127.0.0.1",
       port = getOption("shiny.port", 3838), launch.browser = interactive())
