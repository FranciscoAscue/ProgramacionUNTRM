# Lección 6. Crear una tabla vacía y guardar filas desde un formulario.
library(shiny)
library(DBI)
library(RSQLite)

ruta_db <- Sys.getenv("INGRESO_DB", "r_shiny/ingreso_shiny.sqlite3")

ui <- fluidPage(
  titlePanel("Primeros registros en SQLite"),
  textInput("region", "Región", placeholder = "Piura"),
  textInput("periodo", "Mes (AAAA-MM)", placeholder = "2025-01"),
  numericInput("mwh", "Consumo (MWh)", value = NA, min = 0, step = 1),
  actionButton("guardar", "Guardar"),
  div(role = "status", textOutput("mensaje")),
  h2("Registros guardados"),
  tableOutput("tabla")
)

server <- function(input, output, session) {
  con <- dbConnect(SQLite(), ruta_db)
  session$onSessionEnded(function() dbDisconnect(con))

  # CREATE TABLE define las columnas. Aún no hay filas en una base nueva.
  dbExecute(con, "
    CREATE TABLE IF NOT EXISTS consumo (
      id INTEGER PRIMARY KEY,
      region TEXT NOT NULL,
      periodo TEXT NOT NULL,
      consumo_mwh INTEGER NOT NULL
    )
  ")

  datos <- reactiveVal(dbGetQuery(con, "SELECT * FROM consumo ORDER BY id"))
  mensaje <- reactiveVal("")

  observeEvent(input$guardar, {
    if (!nzchar(input$region) || !nzchar(input$periodo) || is.na(input$mwh) ||
        input$mwh < 0 || input$mwh %% 1 != 0) {
      mensaje("Completa la región, el mes y un consumo entero no negativo.")
      return()
    }

    dbExecute(con,
      "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
      params = list(input$region, input$periodo, input$mwh)
    )
    datos(dbGetQuery(con, "SELECT * FROM consumo ORDER BY id"))
    mensaje("Registro guardado.")
  })

  output$mensaje <- renderText(mensaje())
  output$tabla <- renderTable({
    validate(need(nrow(datos()) > 0, "La tabla está vacía. Guarda tu primer registro."))
    datos()
  }, digits = 0)
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
