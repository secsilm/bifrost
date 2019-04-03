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
import dash_table
import pandas as pd
import numpy as np

app = dash.Dash(__name__)
table_columns = ['gpu', 'pid', 'used_gpu_mem', 'username', 'name', 'create_time', 'status', 'cpu_percent', 'cpu_num', 'memory_percent', 'num_threads', 'cmdline']
int_columns = ['gpu', 'pid', 'cpu_num', 'num_threads']
percent_columns = ['cpu_percent', 'memory_percent']

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def timestamp2datetime(t):
    return pd.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def convert_to_df(info):
    device_info = info["info"]
    result = []
    for d in device_info:
        processes = d.process
        dids = [d.id] * len(processes)
        df = pd.DataFrame(processes)
        df["gpu"] = dids
        result.append(df)
    result = pd.concat(result)
    result = result[table_columns]
    result.create_time = result.create_time.map(timestamp2datetime)
    for c in int_columns:
        result[c] = result[c].astype(int)
    for c in percent_columns:
        result[c] = np.round(result[c]*100, 2)
    return result




ip = get_host_ip()
# infos = get_infos()
# result = convert_to_df(infos)

app.title = f"{ip} Server"
app.layout = html.Div(
    html.Div(
        [
            html.H1(children=f"{ip} 的 GPU 使用情况"),
            html.Div(id="live-time-text"),
            dcc.Interval(id="interval-component", interval=3 * 1000, n_intervals=0),
            dcc.Graph(id="gpu-graph"),
            dash_table.DataTable(
                id="table",
                columns=[{"name": i, "id": i} for i in table_columns],
                css=[
                    {
                        "selector": ".dash-cell div.dash-cell-value",
                        "rule": "display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;",
                    }
                ],
                style_data={"whiteSpace": "normal"},
                # style_cell={"width": "200px"},
                # style_cell_conditional=[
                #     {"if": {'column_id': 'cmdline'}, "width": "50%"}
                # ]
            ),
        ]
    )
)


@app.callback(
    Output("gpu-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_graph(n):
    infos = get_infos()
    device_info = infos["info"]
    fig = tools.make_subplots(
        rows=2,
        cols=2,
        subplot_titles=("显存剩余情况", "显存使用情况", "显卡温度情况", "风扇转速情况"),
        shared_xaxes=True,
    )
    x = [d.id for d in device_info]
    free = [d.free / (1024.0 ** 2) for d in device_info]
    used = [d.used / (1024.0 ** 2) for d in device_info]
    total = [d.total / (1024.0 ** 2) for d in device_info]
    free_ratio = [100 * f / t for f, t in zip(free, total)]
    temp = [d.temperature for d in device_info]
    speed = [d.fan_speed for d in device_info]
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


@app.callback(Output("table", "data"), [Input("interval-component", "n_intervals")])
def update_table(n):
    infos = get_infos()
    result = convert_to_df(infos)
    return result.to_dict(orient="rows")


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8590, debug=False)
