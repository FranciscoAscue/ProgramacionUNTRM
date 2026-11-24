# Lección 5. Una expresión reactiva alimenta cuatro gráficos, indicadores y tabla.
source("r_shiny/dashboard.R", encoding = "UTF-8")
datos <- leer_consumo()
ui <- pagina(ui_dashboard(sort(unique(datos$region)), anios(datos)))

server <- function(input, output, session) {
  # Al leer input, reactive() registra sus dependencias y comparte el resultado.
  visibles <- reactive(filtrar(datos, input$filtro_region, input$filtro_anio))
  servidor_dashboard(output, visibles)
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
