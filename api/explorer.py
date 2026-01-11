from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import json

def load_index():
    with open("semantic-search-index.json", "r") as f:
        return json.load(f)["nodes"]

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def explorer():
    nodes = load_index()

    html = """
    <html>
    <head>
        <title>Semantic Explorer</title>
        <style>
            body { font-family: sans-serif; padding: 20px; }
            .node { margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; }
            .id { font-weight: bold; font-size: 1.1em; }
            .path { color: #555; }
            .tags { color: #888; }
        </style>
    </head><body>
    <h1>EFC Semantic Explorer</h1>
    """

    for n in nodes:
        html += f"""
        <div class="node">
            <div class="id">{n['id']}</div>
            <div class="path">{n['path']}</div>
            <div class="domain"><b>Domain:</b> {n.get('domain')}</div>
            <div class="summary">{n.get('summary')}</div>
            <div class="tags"><b>Tags:</b> {', '.join(n.get('tags', []))}</div>
        </div>
        """

    html += "</body></html>"
    return html
