from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

# 1. Cargar datos de ejemplo
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

# 2. Inicializar la app
app = Dash(__name__)

# 3. Definir el diseño (Layout)
app.layout = html.Div([
    html.H1("Evolución de Población por País", style={'textAlign': 'center', 'fontFamily': 'sans-serif'}),
    
    # Selector desplegable
    dcc.Dropdown(
        options=df['country'].unique(),
        value='Peru',
        id='dropdown-pais',
        style={'width': '50%', 'margin': '0 auto'}
    ),
    
    # Contenedor del gráfico
    dcc.Graph(id='grafico-poblacion')
])

# 4. Definir la interactividad (Callback)
@callback(
    Output('grafico-poblacion', 'figure'),
    Input('dropdown-pais', 'value')
)
def actualizar_grafico(pais_seleccionado):
    df_filtrado = df[df['country'] == pais_seleccionado]
    fig = px.line(
        df_filtrado, 
        x='year', 
        y='pop', 
        title=f'Crecimiento poblacional: {pais_seleccionado}',
        markers=True
    )
    return fig

# 5. Ejecutar el servidor local
if __name__ == '__main__':
    app.run(debug=True)
