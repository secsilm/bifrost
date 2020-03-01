import socket

import numpy as np
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objs as go
import plotly.plotly as py
from dash.dependencies import Input, Output
from plotly import tools
from utils import get_infos

app = dash.Dash(__name__)
server = app.server

table_columns = [
    "gpu",
    "pid",
    "used_gpu_mem",
    "username",
    "name",
    "create_time",
    "status",
    "cpu_percent",
    "cpu_num",
    "memory_percent",
    "num_threads",
    "cmdline",
]
int_columns = ["gpu", "pid", "cpu_num", "num_threads"]
percent_columns = ["cpu_percent", "memory_percent"]
mb_columns = ["used_gpu_mem"]
bar_colors = ["#33425b", "#5baaec", "#526ed0", "#484cb0"]


def get_host_ip():
    """Get host ip.
    
    Returns:
        str: The obtained ip. UNKNOWN if failed.
    """
    ip = "UNKNOWN"
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
    """Convert gpu infomations to pd.DataFrame for filling table.
    
    Args:
        info (dict): The dict returned by get_infos().
    
    Returns:
        pd.DataFrame: The converted dataframe. The order of the columns is in the order of table_columns.
    """

    device_info = info["devices"]
    result = []
    for d in device_info:
        processes = d.process
        dids = [d.id] * len(processes)
        df = pd.DataFrame(processes)
        df["gpu"] = dids
        result.append(df)
    result = pd.concat(result, sort=False)
    result = result.loc[:, table_columns]
    result.create_time = result.create_time.map(timestamp2datetime)
    for c in int_columns:
        result[c] = result[c].astype(int)
    for c in percent_columns:
        result[c] = np.round(result[c], 2)
    for c in mb_columns:
        result[c] = np.round(result[c] / (1024 ** 2), 2)
    return result


ip = get_host_ip()

app.title = f"{ip} Server"
app.layout = html.Div(
    [
        html.H1(children=f"{ip} Server GPU Usage", style={"margin-left": "20px"}),
        html.Div(
            [
                html.Span("Update time：", style={"margin-left": "20px"}),
                html.Span(id="live-time-text"),
            ]
        ),
        html.Div(html.Span(f"Driver version: {get_infos()['driver_version']}", style={"margin-left": "20px"})),
        dcc.Interval(id="interval-component", interval=10 * 1000, n_intervals=0),
        html.H2(children="How are the GPUs", style={"margin-left": "20px"}),
        dcc.Graph(id="gpu-graph"),
        html.H2(children="Who is using GPUs", style={"margin-left": "20px"}),
        html.Div(
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
                # n_fixed_rows=1, # don't use this for now
                style_cell={"padding": "10px"},
                style_cell_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(248, 248, 248)",
                    },
                    {"if": {"column_id": "cmdline"}, "textAlign": "left"},
                ],
                style_header={"backgroundColor": "white", "fontWeight": "bold"},
            ),
            style={"margin-left": "60px"},
        ),
    ]
)


@app.callback(
    Output("gpu-graph", "figure"), [Input("interval-component", "n_intervals")]
)
def update_graph(n):
    infos = get_infos()
    device_info = infos["devices"]
    fig = tools.make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Memory Utilization",
            "Free Memory (MB)",
            "Temperature",
            "Fan Speed",
        ),
        shared_xaxes=False,
        print_grid=False,
    )
    x = [f"{d.name} {d.id}" for d in device_info]
    free = [d.free / (1024.0 ** 2) for d in device_info]
    used = [d.used / (1024.0 ** 2) for d in device_info]
    total = [d.total / (1024.0 ** 2) for d in device_info]
    used_ratio = [100 * u / t for u, t in zip(used, total)]
    temp = [d.temperature for d in device_info]
    speed = [d.fan_speed for d in device_info]
    hover_text = [f"used={u:.0f}<br>total={t:.0f}" for u, t in zip(used, total)]

    trace_used_ratio = go.Bar(
        x=x,
        y=used_ratio,
        text=hover_text,
        marker=dict(color=bar_colors[0]),
        name="used ratio",
    )
    trace_free = go.Bar(x=x, y=free, marker=dict(color=bar_colors[1]), name="free")
    trace_temp = go.Bar(
        x=x, y=temp, marker=dict(color=bar_colors[2]), name="temperature"
    )
    trace_speed = go.Bar(
        x=x, y=speed, marker=dict(color=bar_colors[3]), name="fan speed"
    )

    fig.append_trace(trace_used_ratio, 1, 1)
    fig.append_trace(trace_free, 1, 2)
    fig.append_trace(trace_temp, 2, 1)
    fig.append_trace(trace_speed, 2, 2)
    margin = go.layout.Margin(l=100, r=100, b=50, t=25, pad=4)
    fig["layout"].update(yaxis=dict(range=[0, 100]), margin=margin, showlegend=False)
    return fig


@app.callback(
    Output("live-time-text", "children"), [Input("interval-component", "n_intervals")]
)
def update_time(n):
    return pd.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@app.callback(Output("table", "data"), [Input("interval-component", "n_intervals")])
def update_table(n):
    infos = get_infos()
    result = convert_to_df(infos)
    return result.to_dict(orient="rows")


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8150, debug=False)
