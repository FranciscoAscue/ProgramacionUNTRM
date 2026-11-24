# Lección 1. UI, servidor y una tabla que se carga al iniciar.
source("r_shiny/dashboard.R", encoding = "UTF-8")
datos <- subset(leer_consumo(), region == "Lima")

# Los IDs enlazan cada espacio del UI con una salida del servidor.
ui <- pagina(
  h2("Consumo mensual en Lima"),
  plotOutput("evolucion"),
  h3("Primeras 12 filas de Lima"),
  tableOutput("tabla")
)

server <- function(input, output, session) {
  # renderPlot y renderTable convierten objetos de R en salidas para el navegador.
  output$evolucion <- renderPlot(evolucion(datos), alt = "Evolución mensual en Lima")
  output$tabla <- renderTable(tabla_visible(head(datos, 12)), digits = 0)
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
