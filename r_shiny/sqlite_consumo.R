# Acceso a SQLite con DBI. Cada operación abre y cierra su conexión.
library(DBI)
library(RSQLite)

conectar <- function(ruta) {
  con <- dbConnect(SQLite(), ruta)
  sqliteSetBusyHandler(con, 5000L)
  con
}

inicializar <- function(ruta, datos) {
  con <- conectar(ruta)
  on.exit(dbDisconnect(con))
  # Crear el esquema y cargar el CSV en una sola transacción.
  dbWithTransaction(con, {
    dbExecute(con, "
      CREATE TABLE IF NOT EXISTS consumo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT NOT NULL,
        periodo TEXT NOT NULL,
        consumo_mwh INTEGER NOT NULL CHECK (consumo_mwh BETWEEN 0 AND 1000000000),
        UNIQUE (region, periodo)
      )")
    if (dbGetQuery(con, "PRAGMA user_version")[[1L]] == 0L) {
      dbAppendTable(con, "consumo", datos)
      dbExecute(con, "PRAGMA user_version = 1")
    }
  })
}

listar <- function(ruta) {
  con <- conectar(ruta)
  on.exit(dbDisconnect(con))
  dbGetQuery(con, "SELECT * FROM consumo ORDER BY region, periodo")
}

consultar <- function(ruta, id) {
  con <- conectar(ruta)
  on.exit(dbDisconnect(con))
  dbGetQuery(con, "SELECT * FROM consumo WHERE id = ?", params = list(id))
}

guardar <- function(ruta, id, region, periodo, mwh) {
  con <- conectar(ruta)
  on.exit(dbDisconnect(con))
  # Los argumentos params corresponden a los signos ? del SQL, por orden.
  if (is.null(id)) {
    dbExecute(con, "INSERT INTO consumo (region, periodo, consumo_mwh) VALUES (?, ?, ?)",
              params = list(region, periodo, mwh))
  } else {
    n <- dbExecute(con, "UPDATE consumo SET region = ?, periodo = ?, consumo_mwh = ? WHERE id = ?",
                   params = list(region, periodo, mwh, id))
    if (n != 1L) stop("El registro ya no existe.", call. = FALSE)
  }
  invisible(NULL)
}

eliminar <- function(ruta, id) {
  con <- conectar(ruta)
  on.exit(dbDisconnect(con))
  n <- dbExecute(con, "DELETE FROM consumo WHERE id = ?", params = list(id))
  if (n != 1L) stop("El registro ya no existe.", call. = FALSE)
}
