import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from utils import get_infos
import plotly.plotly as py
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.layout = html.Div(
    html.Div([
        dcc.Interval(
            id='interval-component',
            interval=3 * 1000,
            n_intervals=0
        ),
        dcc.Graph(id='gpu-graph')
    ])
)

@app.callback(Output('gpu-graph', 'figure'), [Input('interval-component', 'n_intervals')])
def update_graph(n):
    gpu_infos = get_infos()
    x = list(gpu_infos['info'].keys())
    y = [gpu_infos['info'][item]['free'] / (1024. ** 2) for item in x]
    trace = go.Bar(x=x, y=y)
    data = [trace]
    layout = go.Layout(title='GPU 剩余空间')
    fig = go.Figure(data=data, layout=layout)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
