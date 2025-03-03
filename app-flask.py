from flask import Flask, render_template_string, send_from_directory
import plotly.graph_objects as go
import pandas as pd
import os
import matplotlib.colors as mcolors

app = Flask(__name__)

# Load UMAP data
# data_path = '/home/lviotti/scatter-aiid-app/umap-BirdNet-app.csv'
data_path = 'umap-BirdNet-app.csv'

df = pd.read_csv(data_path)

# Ensure images are served from the correct directory
IMAGE_DIR = "/home/lviotti/scatter-aiid-app/images"  # Update this to the correct path

# Assign colors
unique_birds = df["bird_id"].unique()
xkcd_colors = list(mcolors.XKCD_COLORS.values())
color_map = {bird: xkcd_colors[i % len(xkcd_colors)] for i, bird in enumerate(unique_birds)}
df["color"] = df["bird_id"].map(color_map)

# Create scatter plot
fig = go.Figure()
for bird_id in unique_birds:
    bird_df = df[df["bird_id"] == bird_id]
    fig.add_trace(go.Scatter(
        x=bird_df["x"],
        y=bird_df["y"],
        mode="markers",
        name=bird_id,
        text=bird_df["img_idx"],  # Used as a unique identifier
        customdata=bird_df["img_path"],  # Store image path
        marker=dict(
            color=color_map[bird_id],
            size=10,
            opacity=0.8,
        ),
        hoverinfo="text"
    ))

fig.update_layout(
    xaxis=dict(title='UMAP Dimension 1'),
    yaxis=dict(title='UMAP Dimension 2'),
    legend=dict(title="Bird Species"),
    plot_bgcolor='rgba(255,255,255,0.1)',
)

@app.route('/')
def index():
    graph_html = fig.to_html(full_html=False)
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scatter Plot</title>
        <style>
            #tooltip {
                position: absolute;
                display: none;
                pointer-events: none;
                background-color: white;
                border: 1px solid black;
                padding: 10px;
                z-index: 1000;
            }
            #tooltip img {
                max-width: 300px;
                height: auto;
            }
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <div>{{ graph_html | safe }}</div>
        <div id="tooltip"></div>
        
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                var tooltip = document.getElementById("tooltip");
                
                document.getElementById("scatter").on("plotly_hover", function(event) {
                    var point = event.points[0];
                    var imgPath = point.customdata;
                    
                    if (imgPath) {
                        tooltip.innerHTML = "<img src='/static/" + imgPath.split('/').pop() + "'>";
                        tooltip.style.left = (event.event.clientX + 10) + "px";
                        tooltip.style.top = (event.event.clientY + 10) + "px";
                        tooltip.style.display = "block";
                    }
                });

                document.getElementById("scatter").on("plotly_unhover", function(event) {
                    tooltip.style.display = "none";
                });
            });
        </script>
    </body>
    </html>
    """, graph_html=graph_html)

@app.route('/static/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
