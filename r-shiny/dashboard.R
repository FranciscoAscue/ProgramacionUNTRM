library(ggplot2)

evolucion <- function(datos){
  mensual <- aggregate(consumo_mwh ~ periodo, datos, sum)
  mensual$mes <- as.Date(paste0(mensual$periodo, "-01"))
  ggplot(data = mensual, aes(x = mes, y=consumo_mwh))+
    geom_line()+
    labs(title = "Consumo mensual")
}



