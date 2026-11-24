"""Lección 3. Una tabla, cuatro gráficos."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html

ruta_csv = Path(__file__).resolve().parents[1] / "datos" / "consumo_electrico.csv"
datos = pd.read_csv(ruta_csv)

# Los gráficos reutilizan las mismas filas, agrupadas de distintas formas.
mensual = datos.groupby("periodo", as_index=False)["consumo_mwh"].sum()
regional = datos.groupby("region", as_index=False)["consumo_mwh"].sum()
con_anio = datos.assign(anio=datos.periodo.str[:4])
anual = con_anio.groupby("anio", as_index=False)["consumo_mwh"].sum()
matriz = datos.pivot(index="region", columns="periodo", values="consumo_mwh")

linea = px.line(mensual, x="periodo", y="consumo_mwh", title="Evolución mensual", markers=True)
barras = px.bar(regional.sort_values("consumo_mwh"), x="consumo_mwh", y="region",
                orientation="h", title="Consumo por región")
por_anio = px.bar(anual, x="anio", y="consumo_mwh", title="Consumo por año")
calor = go.Figure(go.Heatmap(x=matriz.columns.tolist(), y=matriz.index.tolist(),
                             z=matriz.to_numpy(), colorscale="Teal", colorbar={"title": "MWh"}))
linea.update_xaxes(type="category", nticks=10, title="Mes")
linea.update_yaxes(title="MWh")
barras.update_xaxes(title="MWh")
barras.update_yaxes(title="Región")
por_anio.update_xaxes(title="Año", type="category")
por_anio.update_yaxes(title="MWh")
calor.update_layout(title="Consumo por región y mes")
calor.update_xaxes(type="category", nticks=10, title="Mes")
calor.update_yaxes(type="category", title="Región")

app = Dash(__name__)
app.layout = html.Main([
    html.H1("Cuatro vistas del consumo eléctrico"),
    html.Div([
        dcc.Graph(figure=linea), dcc.Graph(figure=barras),
        dcc.Graph(figure=por_anio), dcc.Graph(figure=calor),
    ], className="graficos"),
])

if __name__ == "__main__":
    app.run()
