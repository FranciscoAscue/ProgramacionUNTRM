unzip("large-scale+wave+energy+farm.zip")
source("desviacion_estandar.R")

## Subimos datos de esta forma: 

datos <- read.csv("WEC_Perth_49.csv")
datos_excel <- read.xlsx("documento.xlsx")

#install.packages("dplyr")

desviacion_pearson(mtcars$cyl)
sd(mtcars$cyl)


### Limpieza de datos 

library(dplyr)

## Filtra filas bajo un criterio

mtcars[mtcars$cyl > 4,] ## opcion por defecto de R

filtrado <- mtcars |> filter(cyl > 4) # con dplyr 

mtcars |> filter(cyl > 4, vs == 0)
mtcars %>% filter(cyl > 4, vs == 0)

## filtrar columnas 

mtcars$drat # forma nativa de R


mtcars |> select(drat,cyl)

## Crear una columna 

mtcars$nuevo <- mtcars$mpg*mtcars$carb # Nativa de R

mtcars |> mutate(MedioCarburadores = mtcars$carb/2)


## Agrupar Datos

mtcars |> group_by(cyl) |> summarise(n = n()) 

mtcars |> arrange(desc(drat))

mtcars |> distinct(cyl,am,gear)
