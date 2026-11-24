# Lección 2. Un selector invalida la expresión que dibuja la figura.
source("r_shiny/dashboard.R", encoding = "UTF-8")
datos <- leer_consumo()

ui <- pagina(
  selectInput("region", "Región", sort(unique(datos$region)), selected = "Lima"),
  plotOutput("grafico")
)

server <- function(input, output, session) {
  # Shiny detecta la dependencia al leer input$region dentro de renderPlot.
  output$grafico <- renderPlot({
    evolucion(filtrar(datos, input$region, ""))
  }, alt = "Consumo eléctrico por mes")
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
