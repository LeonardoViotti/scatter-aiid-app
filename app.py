""" 
Iteractive scatter plot to inspect spectrograms

python app/scatter-interactive.py

References:
    https://dash.plotly.com/dash-core-components/tooltip

"""

from dash import Dash, dcc, html, Input, Output, no_update, callback
import plotly.graph_objects as go
import csv
import os
# import matplotlib.colors as mcolors
import plotly.express as px
from collections import defaultdict

# Configuration
FROM_URL = True  # If True, use URLs from 'img_url' column instead of local file paths

# Load UMAP data from CSV
data_path = './umap-BirdNet-app.csv'
# data_path = '/home/lviotti/scatter-aiid-app/umap-BirdNet-app.csv'

data = []
bird_ids = set()

with open(data_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row["x"] = float(row["x"])
        row["y"] = float(row["y"])
        data.append(row)
        bird_ids.add(row["bird_id"])

# Assign each unique bird_id a color
unique_birds = list(bird_ids)

# Get a list of XKCD colors from matplotlib
# xkcd_colors = list(mcolors.XKCD_COLORS.values())

# # Assign each bird_id a unique XKCD color
# color_map = {bird: xkcd_colors[i % len(xkcd_colors)] for i, bird in enumerate(unique_birds)}

high_contrast_colors = px.colors.qualitative.Dark24  # Other options: Plotly, Set3, Bold

# Assign each bird_id a unique color from the palette
color_map = {bird: high_contrast_colors[i % len(high_contrast_colors)] for i, bird in enumerate(unique_birds)}

data_by_bird = defaultdict(list)
for row in data:
    row["color"] = color_map[row["bird_id"]]
    data_by_bird[row["bird_id"]].append(row)

# Create scatter plot with categorical colors
fig = go.Figure()

# Create a separate scatter trace for each bird_id
for bird_id, bird_data in data_by_bird.items():
    fig.add_trace(go.Scatter(
        x=[row["x"] for row in bird_data],
        y=[row["y"] for row in bird_data],
        mode="markers",
        name=bird_id,  # Legend entry
        text=[row["img_idx"] for row in bird_data],
        marker=dict(
            color=color_map[bird_id],
            size=10,
            opacity=0.8,
        ),
        showlegend=True
    ))

fig.update_layout(
    xaxis=dict(title='UMAP Dimension 1'),
    yaxis=dict(title='UMAP Dimension 2'),
    legend=dict(
        title=dict(
            text="Bird ID<br><span style='font-size:12px;'>(double click to select a single bird)</span>",
            side="top"  # Places the legend title above the entries
        ),
        orientation="h",  # Horizontal legend
        yanchor="bottom",
        y=-0.3,  # Moves legend entries below the plot
        xanchor="center",
        x=0.5,
        # tracegroupgap=15,  # Space between groups
        itemwidth=30  # Forces text wrapping into multiple lines
    ),
    plot_bgcolor='rgba(255,255,255,0.1)',
    autosize=True,
    height=None,
)

app = Dash()

app.layout = html.Div([
    dcc.Graph(id="graph-basic", figure=fig, clear_on_unhover=True, 
              style={"height": "100%", "width": "100%"}),  # Full-screen plot
    dcc.Tooltip(id="graph-tooltip"),
], style={"height": "100vh", "width": "100vw", "display": "flex", "flexDirection": "column"})

@callback(
    Output("graph-tooltip", "show"),
    Output("graph-tooltip", "bbox"),
    Output("graph-tooltip", "children"),
    Input("graph-basic", "hoverData"),
)
def display_hover(hoverData):
    if hoverData is None:
        return False, no_update, no_update

    pt = hoverData["points"][0]
    bbox = pt["bbox"]
    num = pt["pointNumber"]

    df_row = data[num]
    img_path = df_row['img_url'] if FROM_URL else df_row['img_path']
    img_idx = df_row['img_idx']

    if not FROM_URL and not os.path.exists(img_path):
        return False, no_update, no_update  # Hide tooltip if image is missing
    
    # Shift tooltip left by 50 pixels (adjust as needed)
    bbox["x0"] += 150
    bbox["x1"] += 130
    
    children = [
    html.Div([
        html.Img(
            src=img_path if FROM_URL else app.get_asset_url(os.path.basename(img_path)), 
            style={"width": "500px", "height": "auto"}
        ),
        html.P(
            f"{img_idx}", 
            style={
                "text-align": "center", 
                "font-family": "Arial",
                "overflow-wrap": "break-word",
                "margin-top": "10px"
            }
        ),
        html.P(
            f"Bird ID: {df_row['bird_id']}", 
            style={
                "text-align": "center", 
                "font-family": "Arial",
                "overflow-wrap": "break-word",
                "margin-top": "10px"
            }
        )
    ], style={
        "width": "200px", 
        "white-space": "normal", 
        "display": "flex", 
        "flex-direction": "column", 
        "align-items": "center"
    })
]

    return True, bbox, children

if __name__ == "__main__":
    app.run(debug=True)
