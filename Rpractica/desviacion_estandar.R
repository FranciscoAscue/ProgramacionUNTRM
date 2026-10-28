library(dplyr)
library(ggplot2)
library(openxlsx)

desviacion_pearson <- function(A){
  var = 0
  x = mean(A)
  for(i in 1:length(A)){
    suma <- (A[i] - x)**2
    var = var + suma
  }
  var = var / (length(A) -1)
  sd = var**(1/2)
  return(sd)
}

media = function(){
  
}