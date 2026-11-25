import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html


datos = pd.read_csv("datos/consumo_electrico.csv")
mensual = datos.groupby("periodo", as_index=False)["consumo_mwh"].sum()

plot = px.line(mensual, x="periodo", y="consumo_mwh", title="Consumo Eléctrico Mensual")

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(figure=plot)
])

if __name__ == "__main__":
    app.run()