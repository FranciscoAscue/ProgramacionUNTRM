# Lección 6. Consultar una tabla SQLite con parámetros usando DBI.
source("r_shiny/dashboard.R", encoding = "UTF-8")
library(DBI)
library(RSQLite)
datos <- leer_consumo()

ui <- pagina(
  h2("Consumo anual consultado con SQL"),
  p("Cada sesión usa una base SQLite temporal en memoria."),
  selectInput("region", "Región", sort(unique(datos$region)), selected = "Lima"),
  plotOutput("grafico"),
  tableOutput("resultado")
)

server <- function(input, output, session) {
  # Un SQLite en memoria existe mientras esta conexión siga abierta.
  con <- dbConnect(SQLite(), ":memory:")
  session$onSessionEnded(function() dbDisconnect(con))
  dbWriteTable(con, "consumo", datos)

  resumen <- reactive({
    dbGetQuery(con, "
      SELECT substr(periodo, 1, 4) AS anio, SUM(consumo_mwh) AS total_mwh
      FROM consumo WHERE region = ?
      GROUP BY anio ORDER BY anio
    ", params = list(input$region))
  })

  # Las dos salidas usan la misma consulta reactiva.
  output$grafico <- renderPlot({
    ggplot(resumen(), aes(anio, total_mwh)) +
      geom_col(fill = "#007e80") + scale_y_continuous(labels = numero) +
      labs(x = "Año", y = "Consumo (MWh)") + tema_consumo()
  })
  output$resultado <- renderTable(resumen(), digits = 0)
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
