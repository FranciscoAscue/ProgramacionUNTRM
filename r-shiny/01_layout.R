library(shiny)
source("r-shiny/dashboard.R")

datos <- read.csv("datos/consumo_electrico.csv")

ui <- fluidPage(
  titlePanel("Primera aplicacion shiny"),
  plotOutput("evolucion")
)
  
server <- function(input, output, session){
  output$evolucion <- renderPlot(evolucion(datos))
}


runApp(shinyApp(ui,server), launch.browser = interactive())


