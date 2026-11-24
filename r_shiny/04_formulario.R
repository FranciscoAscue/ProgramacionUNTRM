# Lección 4. Esperar un clic antes de validar los campos del formulario.
source("r_shiny/dashboard.R", encoding = "UTF-8")
regiones <- sort(unique(leer_consumo()$region))
ui <- pagina(
  div(class = "panel-consumo formulario-consumo",
    h2("Validar un registro de consumo"),
    selectInput("region", "Región", c("Selecciona una región" = "", regiones)),
    textInput("periodo", "Mes (AAAA-MM)", placeholder = "2025-01"),
    textInput("mwh", "Consumo (MWh)"),
    actionButton("validar", "Validar"),
    div(role = "status", textOutput("mensaje"))
  )
)

server <- function(input, output, session) {
  # bindEvent limita la ejecución al clic. Cambiar un campo por sí solo
  # no vuelve a evaluar la expresión. Aquí solo se presenta el resultado.
  resultado <- bindEvent(reactive({
    tryCatch({
      consumo <- validar_campos(regiones, input$region, input$periodo, input$mwh)
      paste0("Registro válido: ", input$region, " · ", trimws(input$periodo), " · ", consumo, " MWh.")
    }, error = function(error) conditionMessage(error))
  }), input$validar, ignoreInit = TRUE)
  output$mensaje <- renderText(resultado())
}

runApp(shinyApp(ui, server), host = "127.0.0.1", launch.browser = interactive())
