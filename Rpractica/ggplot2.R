library(ggplot2)
library(ggthemes)
library(dplyr)


plot <- ggplot(mtcars, aes(x= wt, y = mpg))+
  geom_point(color="skyblue", size = 2)+
  labs(
    x = "Peso (1000 lb)",
    y = "Rendimiento (millas/galón US)",
    title="mtcars: peso y rendimiento"
  ) + theme_calc()

print(plot)

### Colocar color segun Cyl 

plot2 <- ggplot(mtcars, aes(x= wt, y = mpg, color = factor(cyl)))+
  geom_point( size = 2)+
  labs(
    x = "Peso (1000 lb)",
    y = "Rendimiento (millas/galón US)",
    title ="mtcars: peso y rendimiento",
    color ="Cilindros"
  ) + theme_calc()

print(plot2)


### Diferentes formas de los points()

colores <- c("4" = "#0072B2", "6" = "#D55E00", "8" = "#009E73")


plot3 <- ggplot(mtcars, aes(
  x= wt, y = mpg, 
  color = factor(cyl), 
  shape = factor(cyl)))+
  geom_point( size = 2)+
  scale_color_manual(values = colores)+
  scale_shape_manual(values = c("4" = 16, "6" = 15, "8" = 17)) +
  labs(
    x = "Peso (1000 lb)",
    y = "Rendimiento (millas/galón US)",
    title ="mtcars: peso y rendimiento",
    color ="Cilindros",
    shape = "Cilindros"
  ) + theme_calc()

print(plot3)


### plot de histogramas

bordess <- seq(1, 5.5, by = .5)

plot4 <- ggplot(mtcars, aes(x= wt) )+
  geom_histogram(
    breaks = bordess, fill = "#0072B2",
    color = "white"
  )+
  labs(
    x = "Peso (1000 lb)",
    y = "Cantidad de Vehiculos",
    title ="Distribucion de pesos"
  ) + theme_calc()

print(plot4)

### plot de diagrama de barras

plot5 <- ggplot(mtcars, aes(x= factor(cyl), fill = factor(cyl)))+
  geom_bar(color = "white")+
  labs(
    x = "Cilindros",
    y = "Cantidad de Vehiculos",
    title ="Distribución del rendimiento",
    fill = "Cilindros"
  ) + theme_calc()

print(plot5)

### plot de diagrama de cajas (boxplot)

plot6 <- ggplot(mtcars, aes(x = factor(cyl), y = mpg, 
                            fill =  factor(cyl)))+
          geom_boxplot()+
          labs(
            x = "Cilindros",
            y = "Cantidad de Vehiculos",
            title ="Distribución del rendimiento",
            fill = "Cilindros"
          )

print(plot6)


plot6 <- ggplot(mtcars, aes(x = factor(cyl), y = mpg, 
                            fill =  factor(cyl)))+
  geom_violin()+
  geom_jitter(size = 0.5 )
  labs(
    x = "Cilindros",
    y = "Cantidad de Vehiculos",
    title ="Distribución del rendimiento",
    fill = "Cilindros"
  )

print(plot6)



#### Facetas 


plot7 <- ggplot(mtcars, aes(
  x= wt, y = mpg, 
  color = factor(cyl), 
  shape = factor(cyl)))+
  geom_point( size = 2)+
  facet_grid(~cyl)+ # con se separan los plots
  scale_color_manual(values = colores)+
  scale_shape_manual(values = c("4" = 16, "6" = 15, "8" = 17)) +
  labs(
    x = "Peso (1000 lb)",
    y = "Rendimiento (millas/galón US)",
    title ="mtcars: peso y rendimiento",
    color ="Cilindros",
    shape = "Cilindros"
  ) + theme_clean()

print(plot7)



### Usando Dplyr


seleccion <- mtcars |>
  filter(cyl > 4, vs == 0) |>
  select(wt, mpg, cyl)

seleccion |> count(cyl)
# 6 cilindros: 3; 8 cilindros: 14.
ggplot(seleccion, aes(wt, mpg, color = factor(cyl))) +
  geom_point() + labs(color = "Cilindros")
