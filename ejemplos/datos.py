"""La misma tabla CSV de datos ficticios que usa R Shiny."""

from pathlib import Path
import re

import pandas as pd

RUTA_CSV = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
COLUMNAS = ["region", "periodo", "consumo_mwh"]


def leer_consumo():
    return pd.read_csv(RUTA_CSV, dtype={"region": str, "periodo": str})


def validar_consumo(regiones, region, periodo, mwh):
    """Validación compartida por la práctica de formulario y el CRUD."""

    periodo, mwh = (periodo or "").strip(), (mwh or "").strip()
    if region not in regiones:
        raise ValueError("Selecciona una región del listado.")
    if not re.fullmatch(r"(?!0000)[0-9]{4}-(0[1-9]|1[0-2])", periodo):
        raise ValueError("Ingresa el mes en formato AAAA-MM, por ejemplo 2025-01.")
    if not re.fullmatch(r"[0-9]{1,10}", mwh) or int(mwh) > 10**9:
        raise ValueError("Ingresa un consumo entero entre 0 y 1 000 000 000 MWh.")
    return region, periodo, int(mwh)
