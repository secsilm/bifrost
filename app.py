import datetime
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from utils import get_infos
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go
import socket

app = dash.Dash(__name__)

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip

ip = get_host_ip()

app.title = f'{ip} Server'
app.layout = html.Div(
    html.Div(
        [
            html.H1(children=f"{ip} 的 GPU 使用情况"),
            html.Div(id="live-time-text"),
            dcc.Interval(id="interval-component", interval=3 * 1000, n_intervals=0),
            dcc.Graph(id="gpu-graph"),
        ]
    )
)


@app.callback(
    Output("gpu-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_graph(n):
    gpu_infos = get_infos()
    fig = tools.make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("显存剩余情况", "显存使用情况", "显卡温度情况", "风扇转速情况"),
        shared_xaxes=True,
    )
    x = list(gpu_infos["info"].keys())
    free = [gpu_infos["info"][item]["free"] / (1024.0 ** 2) for item in x]
    used = [gpu_infos["info"][item]["used"] / (1024.0 ** 2) for item in x]
    total = [gpu_infos["info"][item]["total"] / (1024.0 ** 2) for item in x]
    free_ratio = [100*f/t for f, t in zip(free, total)]
    temp = [gpu_infos["info"][item]["temperature"] for item in x]
    speed = [gpu_infos["info"][item]["fan_speed"] for item in x]
    hover_text = [f"free_ratio={f:.2f}" for f in free_ratio]
    
    trace_free = go.Bar(x=x, y=free, text=hover_text, name="free")
    trace_used = go.Bar(x=x, y=used, name="used")
    trace_temp = go.Bar(x=x, y=temp, name="temperature")
    trace_speed = go.Bar(x=x, y=speed, name="fan speed")

    fig.append_trace(trace_free, 1, 1)
    fig.append_trace(trace_used, 1, 2)
    fig.append_trace(trace_temp, 2, 1)
    fig.append_trace(trace_speed, 2, 2)
    fig["layout"].update(title="GPU 实时监控")
    return fig


@app.callback(
    Output("live-time-text", "children"), [Input("interval-component", "n_intervals")]
)
def update_time(n):
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8590, debug=False)
