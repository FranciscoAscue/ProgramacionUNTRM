library(shiny)
library(RSQLite)
library(DBI)

ruta_db <- Sys.getenv("INGRESO_DB","datos/consumo_electrico2.sqlite3")

ui <- fluidPage(
  titlePanel("Primer formulario"),
  textInput("region","Region", placeholder = "Amazonas"),
  textInput("periodo","Periodo", placeholder = "2025-01"),
  numericInput("consumo","Consumo (MWh):", value = NA, min = 0, step = 1),
  actionButton("guardar","Guardar"),
  div(role = "status", textOutput("mensaje")),
  h2("Registros en tabla"),
  tableOutput("tabla")
)
  
  
server <- function(input,output,session){
  con <- dbConnect(SQLite(), ruta_db)
  session$onSessionEnded(function() dbDisconnect(con))
  
  dbExecute(con, "
  CREATE TABLE IF NOT EXISTS consumo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        periodo TEXT NOT NULL,
        consumo_mwh INTEGER NOT NULL )         
  ")
  
  datos <- reactiveVal(dbGetQuery(con,"SELECT * FROM consumo ORDER BY id"))
  mensaje <- reactiveVal("")
  
  observeEvent(input$guardar, {
    if (!nchar(input$region) || !nchar(input$periodo) || is.na(input$consumo) ){
      mensaje("Completa correctamente")
      return()
    } 
    
    dbExecute(con,
              "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
              params = list(input$region, input$periodo, input$consumo)
  )
  
    datos(dbGetQuery(con, "SELECT * FROM consumo ORDER BY id"))
    mensaje("Exitoso el ingreso de datos")
  })
  
  output$mensaje <- renderText(mensaje())
  output$tabla <- renderTable({
    validate(need(nrow(datos()) > 0, "La tabla está vacía"))
    datos()
  }, digits = 0)
}
  
  
runApp(shinyApp(ui,server), launch.browser = interactive())