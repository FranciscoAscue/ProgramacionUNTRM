# Funciones compartidas por las lecciones de Shiny.
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

evolucion <- function(datos) {
  mensual <- aggregate(consumo_mwh ~ periodo, datos, sum)
  mensual$mes <- as.Date(paste0(mensual$periodo, "-01"))
  ggplot(mensual, aes(mes, consumo_mwh)) +
    geom_line() +
    geom_point() +
    scale_x_date(date_labels = "%Y-%m", breaks = scales::breaks_pretty(n = 6)) +
    scale_y_continuous(labels = numero) +
    labs(title = "Evolución mensual", x = "Mes", y = "Consumo (MWh)")
}

por_region <- function(datos) {
  totales <- aggregate(consumo_mwh ~ region, datos, sum)
  ggplot(totales, aes(consumo_mwh, reorder(region, consumo_mwh))) +
    geom_col() + scale_x_continuous(labels = numero) +
    labs(title = "Consumo por región", x = "Consumo (MWh)", y = NULL)
}

por_anio <- function(datos) {
  datos$anio <- substr(datos$periodo, 1, 4)
  totales <- aggregate(consumo_mwh ~ anio, datos, sum)
  ggplot(totales, aes(anio, consumo_mwh)) +
    geom_col() + scale_y_continuous(labels = numero) +
    labs(title = "Consumo por año", x = "Año", y = "Consumo (MWh)")
}

mapa_calor <- function(datos) {
  datos$mes <- as.Date(paste0(datos$periodo, "-01"))
  ggplot(datos, aes(mes, region, fill = consumo_mwh)) +
    geom_tile(width = 27) + scale_fill_viridis_c(labels = numero) +
    scale_x_date(date_labels = "%Y-%m", breaks = scales::breaks_pretty(n = 5)) +
    labs(title = "Consumo por región y mes", x = "Mes", y = NULL, fill = "MWh")
}

pagina <- function(...) {
  fluidPage(
    titlePanel("Consumo eléctrico por región"),
    p("Datos ficticios del Perú · MWh"),
    ...
  )
}

ui_dashboard <- function(regiones, opciones_anio = character()) {
  tagList(
    selectInput("filtro_region", "Región", c("Todas las regiones" = "", regiones)),
    selectInput("filtro_anio", "Año", c("Todos los años" = "", opciones_anio)),
    uiOutput("resumen"),
    plotOutput("evolucion"),
    plotOutput("por_region"),
    plotOutput("por_anio"),
    plotOutput("calor"),
    h3("Tabla de consumo"),
    tableOutput("tabla")
  )
}

servidor_dashboard <- function(output, visibles) {
  # Cualquier salida que llame a visibles() se vuelve a calcular si cambia el filtro.
  output$resumen <- renderUI({
    datos <- visibles()
    tags$ul(
      tags$li("Consumo total (MWh): ", numero(sum(datos$consumo_mwh))),
      tags$li("Regiones: ", length(unique(datos$region))),
      tags$li("Registros: ", nrow(datos))
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
