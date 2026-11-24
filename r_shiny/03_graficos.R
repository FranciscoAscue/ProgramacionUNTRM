# Lección 3. Comparar líneas, barras y mapa de calor con los mismos datos.
source("r_shiny/dashboard.R", encoding = "UTF-8")
datos <- leer_consumo()
ui <- pagina(
  h2("Cuatro vistas del consumo eléctrico"),
  fluidRow(column(6, plotOutput("mensual")), column(6, plotOutput("regional"))),
  fluidRow(column(6, plotOutput("anual")), column(6, plotOutput("calor")))
)

server <- function(input, output, session) {
  # Las funciones de dashboard.R preparan agregaciones y capas de ggplot2.
  # Aquí las salidas usan los datos completos y no dependen de un input.
  output$mensual <- renderPlot(evolucion(datos))
  output$regional <- renderPlot(por_region(datos))
  output$anual <- renderPlot(por_anio(datos))
  output$calor <- renderPlot(mapa_calor(datos))
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
