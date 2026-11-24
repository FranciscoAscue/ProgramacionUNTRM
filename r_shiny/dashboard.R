# Funciones compartidas por las tres lecciones de Shiny.
library(shiny)
library(ggplot2)

leer_consumo <- function() {
  read.csv("datos/consumo_electrico.csv", fileEncoding = "UTF-8",
           colClasses = c("character", "character", "integer"))
}

numero <- function(x) format(x, big.mark = " ", scientific = FALSE, trim = TRUE)
anios <- function(datos) sort(unique(substr(datos$periodo, 1, 4)))

filtrar <- function(datos, region, anio) {
  if (nzchar(region)) datos <- datos[datos$region == region, , drop = FALSE]
  if (nzchar(anio)) datos <- datos[startsWith(datos$periodo, paste0(anio, "-")), , drop = FALSE]
  datos
}

tabla_visible <- function(datos) {
  data.frame("Región" = datos$region, "Mes" = datos$periodo,
             "Consumo (MWh)" = numero(datos$consumo_mwh), check.names = FALSE)
}

tema_consumo <- function() {
  theme_minimal(base_size = 13) +
    theme(panel.grid.minor = element_blank(), plot.title.position = "plot")
}

evolucion <- function(datos) {
  mensual <- aggregate(consumo_mwh ~ periodo, datos, sum)
  mensual$mes <- as.Date(paste0(mensual$periodo, "-01"))
  ggplot(mensual, aes(mes, consumo_mwh)) +
    geom_line(color = "#007e80", linewidth = 1) +
    geom_point(color = "#007e80", size = 2) +
    scale_x_date(date_labels = "%Y-%m", breaks = scales::breaks_pretty(n = 6)) +
    scale_y_continuous(labels = numero) +
    labs(title = "Evolución mensual", x = "Mes", y = "Consumo (MWh)") +
    tema_consumo()
}

por_region <- function(datos) {
  totales <- aggregate(consumo_mwh ~ region, datos, sum)
  ggplot(totales, aes(consumo_mwh, reorder(region, consumo_mwh))) +
    geom_col(fill = "#007e80") + scale_x_continuous(labels = numero) +
    labs(title = "Consumo por región", x = "Consumo (MWh)", y = NULL) +
    tema_consumo()
}

por_anio <- function(datos) {
  datos$anio <- substr(datos$periodo, 1, 4)
  totales <- aggregate(consumo_mwh ~ anio, datos, sum)
  ggplot(totales, aes(anio, consumo_mwh)) +
    geom_col(fill = "#3857a6", width = .65) + scale_y_continuous(labels = numero) +
    labs(title = "Consumo por año", x = "Año", y = "Consumo (MWh)") +
    tema_consumo()
}

mapa_calor <- function(datos) {
  datos$mes <- as.Date(paste0(datos$periodo, "-01"))
  ggplot(datos, aes(mes, region, fill = consumo_mwh)) +
    geom_tile(width = 27) + scale_fill_viridis_c(option = "C", labels = numero) +
    scale_x_date(date_labels = "%Y-%m", breaks = scales::breaks_pretty(n = 5)) +
    labs(title = "Consumo por región y mes", x = "Mes", y = NULL, fill = "MWh") +
    tema_consumo()
}

pagina <- function(...) {
  fluidPage(
    tags$head(tags$style(HTML("
      body { background: #edf3f7; color: #182b3a; }
      .container-fluid { max-width: 1200px; padding: 20px; }
      h1 { margin-bottom: 8px; }
      .panel-consumo { background: white; border: 1px solid #d5e0e9;
        border-radius: 10px; padding: 16px; margin: 12px 0; }
      .tabla-scroll { max-height: 360px; overflow: auto; }
      .formulario-consumo { max-width: 660px; }
      .indicador-shiny { background: #edf5f7; border-radius: 6px;
        margin: 0 0 12px; padding: 10px; }
      .indicador-shiny strong { display: block; font-size: 20px; }
      .gestion-registros { display: grid; grid-template-columns: minmax(0, 2fr) minmax(240px, 1fr);
        gap: 20px; align-items: start; }
      @media (max-width: 780px) { .gestion-registros { grid-template-columns: 1fr; } }
      #tabla_registros th:last-child, #tabla_registros td:last-child { text-align: right; }
      .botones { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
    "))),
    titlePanel("Consumo eléctrico por región"),
    p("Datos ficticios del Perú · MWh"),
    ...
  )
}

ui_dashboard <- function(regiones, opciones_anio = character()) {
  div(class = "panel-consumo",
    fluidRow(
      column(6, selectInput("filtro_region", "Región",
                            c("Todas las regiones" = "", regiones))),
      column(6, selectInput("filtro_anio", "Año",
                            c("Todos los años" = "", opciones_anio)))
    ),
    uiOutput("resumen"),
    fluidRow(
      column(6, plotOutput("evolucion", height = 340)),
      column(6, plotOutput("por_region", height = 340))
    ),
    fluidRow(
      column(6, plotOutput("por_anio", height = 340)),
      column(6, plotOutput("calor", height = 340))
    ),
    h3("Tabla de consumo"),
    div(class = "tabla-scroll", tableOutput("tabla"))
  )
}

servidor_dashboard <- function(output, visibles) {
  # Cualquier salida que llame a visibles() se vuelve a calcular si cambia el filtro.
  output$resumen <- renderUI({
    datos <- visibles()
    tarjeta <- function(etiqueta, valor) {
      column(4, div(class = "indicador-shiny", span(etiqueta), strong(numero(valor))))
    }
    fluidRow(
      tarjeta("Consumo total (MWh)", sum(datos$consumo_mwh)),
      tarjeta("Regiones", length(unique(datos$region))),
      tarjeta("Registros", nrow(datos))
    )
  })

  con_datos <- function() {
    datos <- visibles()
    validate(need(nrow(datos) > 0L, "Sin registros para este filtro"))
    datos
  }

  output$evolucion <- renderPlot(evolucion(con_datos()), alt = "Evolución mensual")
  output$por_region <- renderPlot(por_region(con_datos()), alt = "Consumo por región")
  output$por_anio <- renderPlot(por_anio(con_datos()), alt = "Consumo por año")
  output$calor <- renderPlot(mapa_calor(con_datos()), alt = "Consumo por región y mes")
  output$tabla <- renderTable(tabla_visible(con_datos()), digits = 0)
}


# Validación compartida por la práctica de formulario y el CRUD.
validar_campos <- function(regiones, region, periodo, mwh) {
  periodo <- trimws(periodo)
  mwh <- trimws(mwh)
  if (!(region %in% regiones)) stop("Selecciona una región del listado.", call. = FALSE)
  if (!grepl("^(?!0000)[0-9]{4}-(0[1-9]|1[0-2])$", periodo, perl = TRUE)) {
    stop("Ingresa el mes en formato AAAA-MM, por ejemplo 2025-01.", call. = FALSE)
  }
  if (!grepl("^[0-9]{1,10}$", mwh) || as.numeric(mwh) > 1e9) {
    stop("Ingresa un consumo entero entre 0 y 1 000 000 000 MWh.", call. = FALSE)
  }
  as.integer(mwh)
}
