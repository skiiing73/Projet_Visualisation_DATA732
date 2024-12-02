import dash
from dash import dcc, html, Input, Output
import pandas as pd
import networkx as nx
import plotly.graph_objs as go
import json
from tqdm import tqdm

# Charger les données à partir du fichier JSON
with open("data/co_occurrence_loc_matrix.json", "r") as f:
    data = json.load(f)

# Convertir les données JSON en data_networkFrame pandas
df = pd.DataFrame(data_network)

# Filtrer les paires de mots-clés dont la co-occurrence est supérieure ou égale à 100
df_filtered = df[df['Co-occurrence'] >= 100]

print("filtrage fait")

# Créer un graphe NetworkX pour les co-occurrences
G = nx.Graph()

# Ajouter des nœuds et des liens (edges) au graphe avec les poids basés sur la co-occurrence
for idx, row in tqdm(df_filtered.iterrows(), desc="Ajout des paires au graphe"):
    G.add_edge(row['Word 1'], row['Word 2'], weight=row['Co-occurrence'])

# Extraire les positions des nœuds à l'aide de spring_layout
pos = nx.spring_layout(G, k=13, seed=42)  # Augmenter k pour écarter les nœuds davantage

# Extraire les coordonnées des arêtes
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.append(x0)
    edge_x.append(x1)
    edge_x.append(None)
    edge_y.append(y0)
    edge_y.append(y1)
    edge_y.append(None)

# Créer le tracé des arêtes
edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none',
    mode='lines')

# Extraire les coordonnées des nœuds et ajuster la taille des nœuds en fonction de la co-occurrence
node_x = []
node_y = []
node_sizes = []  # Pour ajuster la taille des nœuds
node_colors = []  # Pour ajuster la couleur des nœuds
max_node_size = 100  # Taille maximale des nœuds
min_node_size = 25  # Taille minimale des nœuds

# Calculer la somme des poids pour chaque nœud
node_weights = {}
for node in G.nodes():
    weight_sum = sum([G[node][neighbor]['weight'] for neighbor in G.neighbors(node)])
    node_weights[node] = weight_sum

# Normaliser les tailles des nœuds
min_weight = min(node_weights.values())
max_weight = max(node_weights.values())

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    
    # Normalisation : mappez les tailles dans la plage [min_node_size, max_node_size]
    normalized_size = (node_weights[node] - min_weight) / (max_weight - min_weight)  # Normalisation entre 0 et 1
    scaled_size = min_node_size + (normalized_size * (max_node_size - min_node_size))  # Mise à l'échelle à la plage
    node_sizes.append(scaled_size)
    
    # Ajouter la couleur en fonction du nombre total de co-occurrences
    node_colors.append(node_weights[node])

# Créer le tracé des nœuds
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text',
    hoverinfo='text',
    text=list(G.nodes()),
    textfont=dict(size=15, color='white'),  # Afficher les noms en blanc
    marker=dict(
        showscale=True,
        colorscale='Viridis', 
        size=node_sizes,
        color=node_colors,
        colorbar=dict(
            thickness=15,
            title='Nombre de Co-occurrences',
            xanchor='left',
            titleside='right'
        ),
        line_width=2))

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Layout de l'application Dash
app.layout = html.Div([
    html.Div([
        dcc.Graph(
            id='network-graph', 
            figure=go.Figure(
                data=[edge_trace, node_trace],
                layout=dict(
                    plot_bgcolor='rgb(30, 30, 30)',  # Fond sombre
                    paper_bgcolor='rgb(240, 240, 240)',  # Fond clair pour la page
                    height=900,  # Fixe la hauteur à 900px
                    showlegend=False  # Désactive la légende
                )
            ), 
            config={'scrollZoom': True}),
    ], 
    style={'width': '100vw', 'height': '900px', 'margin': '0 auto', 'backgroundColor': '#2c2c2c'}),  # Fond foncé
    html.Div(id='node-info', style={'padding': '20px', 'color': 'white'})
])

# Callback pour gérer l'interaction avec les nœuds (au clic)
@app.callback(
    [Output('network-graph', 'figure'),
     Output('node-info', 'children')],
    [Input('network-graph', 'clickData')]
)
def update_graph(clickData):
    if clickData is None or 'points' not in clickData:
        # Si aucun nœud n'est sélectionné ou le clic est hors d'un nœud, afficher la figure sans surbrillance
        return go.Figure(
            data=[edge_trace, node_trace],
            layout=dict(
                plot_bgcolor='rgb(30, 30, 30)',  # Fond foncé pour le graphique
                paper_bgcolor='rgb(255, 255, 255)',  # Fond blanc pour la page
                height=900,  # Fixe la hauteur à 900px
                showlegend=False  # Désactive la légende
            )
        ), "Cliquez sur un nœud pour voir les informations."

    # Extraire l'information du nœud cliqué
    clicked_node = clickData['points'][0]['text']
    
    # Trouver les voisins du nœud cliqué
    neighbors = list(G.neighbors(clicked_node))
    
    # Mettre en surbrillance les voisins les plus connectés
    highlighted_edges = []
    highlighted_nodes = []
    for neighbor in neighbors:
        if G[clicked_node][neighbor]['weight'] >= 100:
            x0, y0 = pos[clicked_node]
            x1, y1 = pos[neighbor]
            highlighted_edges.append((x0, y0, x1, y1))
            highlighted_nodes.append(neighbor)
    
    # Créer la nouvelle trace des arêtes avec surbrillance
    edge_x_highlight = []
    edge_y_highlight = []
    for (x0, y0, x1, y1) in highlighted_edges:
        edge_x_highlight.append(x0)
        edge_x_highlight.append(x1)
        edge_x_highlight.append(None)
        edge_y_highlight.append(y0)
        edge_y_highlight.append(y1)
        edge_y_highlight.append(None)

    edge_trace_highlight = go.Scatter(
        x=edge_x_highlight, y=edge_y_highlight,
        line=dict(width=2, color='red'),
        hoverinfo='none',
        mode='lines')

    # Créer la nouvelle trace des nœuds avec surbrillance
    node_x_highlight = []
    node_y_highlight = []
    node_sizes_highlight = []  # Utiliser la même taille que les nœuds de base
    node_colors_highlight = []  # Couleur rouge pour la surbrillance

    for node in highlighted_nodes:
        x, y = pos[node]
        node_x_highlight.append(x)
        node_y_highlight.append(y)
        
        # Prendre la même taille que celle des nœuds de base
        index = list(G.nodes()).index(node)
        node_sizes_highlight.append(node_sizes[index])
        
        # Couleur rouge pour la surbrillance
        node_colors_highlight.append(50)  # Couleur rouge pour la surbrillance
    
    node_trace_highlight = go.Scatter(
        x=node_x_highlight, y=node_y_highlight,
        mode='markers',
        hoverinfo='text',
        text=highlighted_nodes,
        textfont=dict(size=20, color='white'),
        marker=dict(
            showscale=False,
            size=node_sizes_highlight,
            color=node_colors_highlight,
            line_width=2))

    # Construire la figure mise à jour
    updated_figure = go.Figure(
        data=[edge_trace, edge_trace_highlight, node_trace, node_trace_highlight],
        layout=dict(
            plot_bgcolor='rgb(30, 30, 30)',
            paper_bgcolor='rgb(255, 255, 255)',
            height=900,
            showlegend=False
        )
    )
    
    # Afficher les informations sur le nœud cliqué
    node_info = f"Vous avez cliqué sur : {clicked_node}. Il est connecté à {len(neighbors)} autres mots."

    return updated_figure, node_info

# Lancer l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)