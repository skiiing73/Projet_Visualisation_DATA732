
import json
from collections import Counter
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import *
from tqdm import tqdm
import networkx as nx

# Chargement des données JSON
with open("fr.sputniknews.africa--20220630--20230630.json", "r") as f:
    data = json.load(f)

with open("co_occurrence_loc_matrix.json", "r") as f:
    data_network = json.load(f)

# Extraction et transformation des données
############################################################
####               Graphe Network                       ####
############################################################
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

# Extraction et transformation des données
############################################################
##################Graphe map################################
############################################################

# Extraction de la liste de localisation
data_2023 = data.get('metadata', {}).get('month', {}).get('2023', {})
data_2022 = data.get('metadata', {}).get('month', {}).get('2022', {})

#on trie par mois afin que ce soit dans le bon ordre des moisq
data_2022=dict(sorted(data_2022.items(), key=lambda item: int(item[0])))
data_2023=dict(sorted(data_2023.items(), key=lambda item: int(item[0])))
def get_frequence_for_country(month):
    #dictionnaire de traduction du pays
    pays_traduction = {
        "Afghanistan": "Afghanistan",
        "Afrique du Sud": "South Africa",
        "Albanie": "Albania",
        "Algérie": "Algeria",
        "Allemagne": "Germany",
        "Andorre": "Andorra",
        "Angola": "Angola",
        "Antigua-et-Barbuda": "Antigua and Barbuda",
        "Arabie Saoudite": "Saudi Arabia",
        "Argentine": "Argentina",
        "Arménie": "Armenia",
        "Australie": "Australia",
        "Autriche": "Austria",
        "Azerbaïdjan": "Azerbaijan",
        "Bahamas": "Bahamas",
        "Bahreïn": "Bahrain",
        "Bangladesh": "Bangladesh",
        "Barbade": "Barbados",
        "Belgique": "Belgium",
        "Belize": "Belize",
        "Bénin": "Benin",
        "Bhoutan": "Bhutan",
        "Bolivie": "Bolivia",
        "Bosnie-Herzégovine": "Bosnia and Herzegovina",
        "Botswana": "Botswana",
        "Brésil": "Brazil",
        "Brunei": "Brunei",
        "Bulgarie": "Bulgaria",
        "Burkina Faso": "Burkina Faso",
        "Burundi": "Burundi",
        "Bélarus": "Belarus",
        "Bénin": "Benin",
        "Bhoutan": "Bhutan",
        "Bolivie": "Bolivia",
        "Bosnie-Herzégovine": "Bosnia and Herzegovina",
        "Botswana": "Botswana",
        "Brésil": "Brazil",
        "Brunei": "Brunei",
        "Bulgarie": "Bulgaria",
        "Burkina Faso": "Burkina Faso",
        "Burundi": "Burundi",
        "Cambodge": "Cambodia",
        "Cameroun": "Cameroon",
        "Canada": "Canada",
        "Cap-Vert": "Cape Verde",
        "Chili": "Chile",
        "Chine": "China",
        "Chypre": "Cyprus",
        "Colombie": "Colombia",
        "Comores": "Comoros",
        "Congo": "Democratic Republic of the Congo",
        "Corée du Nord": "North Korea",
        "Corée du Sud": "South Korea",
        "Costa Rica": "Costa Rica",
        "Côte d'Ivoire": "Ivory Coast",
        "Croatie": "Croatia",
        "Cuba": "Cuba",
        "Danemark": "Denmark",
        "Djibouti": "Djibouti",
        "Dominique": "Dominica",
        "Égypte": "Egypt",
        "Émirats arabes unis": "United Arab Emirates",
        "Equateur": "Ecuador",
        "Érythrée": "Eritrea",
        "Espagne": "Spain",
        "Estonie": "Estonia",
        "Eswatini": "Eswatini",
        "États-Unis": "United States",
        "Éthiopie": "Ethiopia",
        "Fidji": "Fiji",
        "Finlande": "Finland",
        "France": "France",
        "Gabon": "Gabon",
        "Gambie": "Gambia",
        "Géorgie": "Georgia",
        "Ghana": "Ghana",
        "Grèce": "Greece",
        "Grenade": "Grenada",
        "Guatemala": "Guatemala",
        "Guinée": "Guinea",
        "Guinée-Bissau": "Guinea-Bissau",
        "Guyana": "Guyana",
        "Haïti": "Haiti",
        "Honduras": "Honduras",
        "Hongrie": "Hungary",
        "Iles Marshall": "Marshall Islands",
        "Inde": "India",
        "Indonésie": "Indonesia",
        "Irak": "Iraq",
        "Iran": "Iran",
        "Irlande": "Ireland",
        "Islande": "Iceland",
        "Israël": "Israel",
        "Italie": "Italy",
        "Jamaïque": "Jamaica",
        "Japon": "Japan",
        "Jordanie": "Jordan",
        "Kazakhstan": "Kazakhstan",
        "Kenya": "Kenya",
        "Kiribati": "Kiribati",
        "Koweït": "Kuwait",
        "Laos": "Laos",
        "Lesotho": "Lesotho",
        "Lettonie": "Latvia",
        "Liban": "Lebanon",
        "Liberia": "Liberia",
        "Libye": "Libya",
        "Liechtenstein": "Liechtenstein",
        "Lituanie": "Lithuania",
        "Luxembourg": "Luxembourg",
        "Macédoine du Nord": "North Macedonia",
        "Madagascar": "Madagascar",
        "Malaisie": "Malaysia",
        "Malawi": "Malawi",
        "Maldives": "Maldives",
        "Mali": "Mali",
        "Malte": "Malta",
        "Mariannes du Nord": "Northern Mariana Islands",
        "Maroc": "Morocco",
        "Maurice": "Mauritius",
        "Mauritanie": "Mauritania",
        "Mexique": "Mexico",
        "Micronésie": "Micronesia",
        "Moldavie": "Moldova",
        "Monaco": "Monaco",
        "Mongolie": "Mongolia",
        "Monténégro": "Montenegro",
        "Mozambique": "Mozambique",
        "Namibie": "Namibia",
        "Nauru": "Nauru",
        "Népal": "Nepal",
        "Nicaragua": "Nicaragua",
        "Niger": "Niger",
        "Nigeria": "Nigeria",
        "Niue": "Niue",
        "Norvège": "Norway",
        "Nouvelle-Zélande": "New Zealand",
        "Oman": "Oman",
        "Ouganda": "Uganda",
        "Panama": "Panama",
        "Papouasie-Nouvelle-Guinée": "Papua New Guinea",
        "Paraguay": "Paraguay",
        "Pays-Bas": "Netherlands",
        "Pérou": "Peru",
        "Philippines": "Philippines",
        "Pologne": "Poland",
        "Portugal": "Portugal",
        "Qatar": "Qatar",
        "République tchèque": "Czech Republic",
        "République dominicaine": "Dominican Republic",
        "Roumanie": "Romania",
        "Royaume-Uni": "United Kingdom",
        "Russie": "Russia",
        "Rwanda": "Rwanda",
        "Sahara Occidental": "Western Sahara",
        "Saint-Christophe-et-Niévès": "Saint Kitts and Nevis",
        "Saint-Marin": "San Marino",
        "Saint-Vincent-et-les-Grenadines": "Saint Vincent and the Grenadines",
        "Sainte-Lucie": "Saint Lucia",
        "Salvador": "El Salvador",
        "Samoa": "Samoa",
        "Sao Tomé-et-Principe": "São Tomé and Príncipe",
        "Sénégal": "Senegal",
        "Serbie": "Serbia",
        "Seychelles": "Seychelles",
        "Sierra Leone": "Sierra Leone",
        "Singapour": "Singapore",
        "Slovaquie": "Slovakia",
        "Slovénie": "Slovenia",
        "Somalie": "Somalia",
        "Soudan": "Sudan",
        "Sri Lanka": "Sri Lanka",
        "Suède": "Sweden",
        "Suisse": "Switzerland",
        "Syrie": "Syria",
        "Sainte-Hélène": "Saint Helena",
        "Tadjikistan": "Tajikistan",
        "Tanzanie": "Tanzania",
        "Tchad": "Chad",
        "Thaïlande": "Thailand",
        "Timor oriental": "East Timor",
        "Togo": "Togo",
        "Trinité-et-Tobago": "Trinidad and Tobago",
        "Tunisie": "Tunisia",
        "Turkménistan": "Turkmenistan",
        "Turquie": "Turkey",
        "Tuvalu": "Tuvalu",
        "Ukraine": "Ukraine",
        "Uruguay": "Uruguay",
        "Vanuatu": "Vanuatu",
        "Vatican": "Vatican City",
        "Venezuela": "Venezuela",
        "Viêt Nam": "Vietnam",
        "Yémen": "Yemen",
        "Zambie": "Zambia",
        "Zimbabwe": "Zimbabwe"
    }

    # Fonction pour normaliser les noms des pays
    def normalize_country_name(name):
        name = re.sub(r"^(l’|la |le |les )", "", name, flags=re.IGNORECASE)
        
        if name in pays_traduction.keys():

            return pays_traduction.get(name)

    # Combine both years of data
    data_month = {}
    for months, data in data_2022.items():
        data_month[months] = data.get('loc', {})
    for months, data in data_2023.items():
        data_month[months] = data.get('loc', {})
        
    

    # Normaliser les noms des pays
    normalized_data_month = {}
    for month, data_mensuelle in data_month.items():
        normalized_data_month_en_cours = {}

        for pays, values in data_mensuelle.items():
            pays_normalize = normalize_country_name(pays)
            if pays_normalize != None:
                normalized_data_month_en_cours[pays_normalize] = normalized_data_month_en_cours.get(pays_normalize, 0) + values

        normalized_data_month[month] = normalized_data_month_en_cours 

    # Créer les frames pour l'animation
    frames = []
    for month, values in normalized_data_month.items():
        frame_data = [{'Country': pays, 'Frequency': freq, 'Month': f'{month}'} for pays, freq in values.items()]
        frames.append(pd.DataFrame(frame_data))
    return frames


############################################################
##################Graphe barchart###########################
############################################################
# Fonction pour extraire les mots-clés en fonction du pays
def get_keywords_for_country(pays):
    keywords = {}
    ban_words=["pays",'russie','russe',"ans"]
    # Extraction de la liste des keywords par articles
    for year, data_year in data.get('data', {}).items():  # Parcours des années
        for month, data_month in data_year.items():  # Parcours des mois
            for day, data_day in data_month.items():  # Parcours des jours
                for data_article in data_month[day]:  # Parcours des articles
                    if pays in data_article.get('loc', {}):  # Vérification du pays
                        for kws, values in data_article.get('kws', {}).items():  # Parcours des mots-clés et leurs valeurs
                            if kws not in ban_words:  # Supprimer le mot "pays" non pertinent
                                keywords[kws] = keywords.get(kws, 0) + values  # Mise à jour du dictionnaire

    # Supprimer le pays des mots-clés s'il est présent
    if pays.lower() in keywords:
        del keywords[pays.lower()]

    # Trier et garder les 15 mots les plus fréquents
    top_words = dict(Counter(keywords).most_common(15))
    return top_words


############################################################
##################Graphe blinehcart thomas##################
############################################################
# Normalisation et filtrage des mots-clés
def normalize_and_filter_keywords(keywords):
    keyword_map = {'russe': 'russie', 'russes': 'russie'}
    ban_words = ['pays', 'président', 'mars', 'septembre', 'juin', 'nord', 
                 'juillet', 'octobre', 'août', 'novembre', 'ministre', 'région','gaz','centrale']
    normalized_keywords = []
    for keyword, count in keywords.items():
        normalized_keyword = keyword_map.get(keyword.lower(), keyword.lower())
        if normalized_keyword not in ban_words:
            normalized_keywords.append((normalized_keyword, count))
    return normalized_keywords

# Obtenir les mots-clés principaux par mois
def get_top_keywords_by_month(data, year, month, n_keywords=3):
    articles = data.get('data', {}).get(str(year), {}).get(str(month), {}).values()
    all_keywords = Counter()
    for day_articles in articles:
        for article in day_articles:
            keywords = article.get("kws", {})
            normalized_keywords = normalize_and_filter_keywords(keywords)
            top_keywords = [kw[0] for kw in sorted(normalized_keywords, key=lambda x: x[1], reverse=True)[:3]]
            all_keywords.update(top_keywords)
    return all_keywords.most_common(n_keywords)

# Fonction pour obtenir les mots-clés mensuels normalisés
def get_monthly_top_keywords_with_counts_normalized(data, start_year, start_month, end_year, end_month, n_keywords=3):
    monthly_keywords = []
    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            if year == start_year and month < start_month:
                continue
            if year == end_year and month > end_month:
                break
            top_keywords = get_top_keywords_by_month(data, year, month, n_keywords)
            for keyword, count in top_keywords:
                monthly_keywords.append({
                    'Month': f'{year}-{month:02d}',
                    'Keyword': keyword,
                    'Count': count
                })
    return pd.DataFrame(monthly_keywords)

# Données pour le graphique
df_keywords_counts_normalized = get_monthly_top_keywords_with_counts_normalized(data, 2022, 7, 2023, 6, 3)

############################################################
################# Application dash #########################
############################################################

# Initialiser l'application Dash
app = dash.Dash(__name__)
months_name = ["07/22", "08/22", "09/22", "10/22", "11/22", "12/22", "01/23", "02/23", "03/23", "04/23", "05/23", "06/23"]

# Layout de l'application
# Layout de l'application
app.layout = html.Div([
    # Main section with charts
    html.Div([
        
        # Geographic chart with a month slider
        html.Div([
            html.H1("Analyse de la Fréquence des Noms de Pays"),
            dcc.Graph(id="map-chart"),  # Hidden by default
            dcc.Slider(
                id='month-slider',
                min=1, max=12,
                marks={i: months_name[i - 1] for i in range(1, 13)},
                value=1,
                step=1
            )
        ], id="graph1-container"),

        # Dropdown and bar chart for keywords
        html.Div([
            html.H1("Analyse des mots les plus utilisés pour un pays"),
            dcc.Dropdown(
                id="pays-dropdown",
                options=[
                    {'label': 'France', 'value': 'France'},
                    {'label': 'Ukraine', 'value': 'Ukraine'},
                    {'label': 'Russie', 'value': 'Russie'},
                    {'label': 'Chine', 'value': 'Chine'},
                    {'label': 'Algérie', 'value': 'Algérie'},
                    {'label': 'États-Unis', 'value': 'États-Unis'},
                    {'label': 'Afrique', 'value': 'Afrique'}
                ],
                value='France',
                clearable=False,
                className='dash-dropdown'
            ),
            dcc.Graph(id="keyword-bar-chart", className='dash-graph')  # Hidden by default
        ], id="graph2-container"),

        # Network graph container
        html.Div([
            html.H1("Réseau de co-occurrences des localisations au sein des articles"),
            dcc.Graph(
                id='network-graph',
                figure=go.Figure(
                    data=[edge_trace, node_trace],
                    layout=dict(
                        plot_bgcolor='rgb(30, 30, 30)',  # Dark background
                        paper_bgcolor='rgb(240, 240, 240)',  # Light page background
                        showlegend=False  # Disable legend
                    )
                ),
                className='dash-graph',
                config={'scrollZoom': True}
            ),
        ], id="graph3-container"),
        
        #Line chart graph
        html.Div([
            
            html.H1("Analyse des mots clés dans le temps"),
            dcc.Graph(
                id='trend-line-chart',
                figure=px.line(df_keywords_counts_normalized, x='Month', y='Count', color='Keyword',
                            title="Trend des mots les plus utilisés par mois (July 2022 - June 2023)",
                            markers=True)
            )

        ], id="graph4-container"),
            
        html.Div(id='node-info')
    ], style={'margin-left': '270px','height':'100vh'}),
    

    # Sidebar on the right with a menu to choose charts
    html.Div([

        html.Div([
            html.H1("DATA732       Analyse de Données"),
        ], className="title_div"),

        html.Div([
            html.H2("Sélection des Graphiques"),
            dcc.Dropdown(
                id="graph-dropdown",
                options=[
                    {'label': 'Graphique 1', 'value': 'graph1'},
                    {'label': 'Graphique 2', 'value': 'graph2'},
                    {'label': 'Graphique 3', 'value': 'graph3'},
                    {'label': 'Graphique 4', 'value': 'graph4'}
                ],
                value='graph1',
                clearable=False,
                className='dash-dropdown'
            ),
        ], className="selection_div"),

        html.Div([
            html.H2("Télécharger notre fichier source"),
            
            # Button to download a file
            html.Button("Télécharger", id="download-button", n_clicks=0),

            # Dash component to manage file download
            dcc.Download(id="download"),

        ], className="download_div"),

    ], className="sidebar")

])


############################################################
######        Appelle des fonctions callback       #########
############################################################

# Fonction pour obtenir les données géographiques en fonction du mois
@app.callback(
    Output("map-chart", "figure"),
    [Input("month-slider", "value")]
)
def update_map_chart(month):
    # Filtrer et transformer les données pour le mois sélectionné
    frame = get_frequence_for_country(month)[month-1]  # Indexation pour le mois

    # Créer le graphique choropleth avec une échelle de couleur adaptée
    fig = go.Figure(go.Choropleth(
        locations=frame['Country'],  # Noms des pays
        locationmode="country names",  # Correspondance par noms des pays
        z=frame['Frequency'],  # Valeurs pour le coloriage
        colorscale=[
            [0.0, "white"],       # Blanc pour 0
            [0.5, "blue"],         # Couleurs intermédiaires
            [1.0, "darkblue"]      # Couleurs élevées
        ],
        zmin=0,  # Minimum explicitement défini
        zmax=max(frame['Frequency']),  # Maximum basé sur les données
        colorbar=dict(title="Frequency"),  # Légende de l'échelle
        showscale=True
    ))

    # Mise en page du graphique
    fig.update_layout(
        title="Nombre de fois où un pays a été mentionné par Sputnik sur un mois (2022-2023)",
        title_x=0.5,
        geo=dict(
            showframe=False,  # Masquer les bordures de la carte
            showcoastlines=True,  # Montrer les lignes de côte
            projection_type='natural earth'  # Projection pour la carte
        )
    )

    return fig


# Callback pour mettre à jour le graphique en fonction du pays choisi
@app.callback(
    Output("keyword-bar-chart", "figure"),
    [Input("pays-dropdown", "value")]
)
def update_graph(pays):
    # Obtenir les mots-clés pour le pays choisi
    top_words = get_keywords_for_country(pays)
    words = list(top_words.keys())
    occurrences = list(top_words.values())
    # Créer le graphique
    fig = px.bar(
        x=words,  # Liste des mots
        y=occurrences,  # Liste des occurrences
        labels={'x': 'Mots', 'y': 'Occurrences'},
        title=f"Top 15 des mots les plus utilisés lorsque {pays} est cité dans un article par Sputnik (2022-2023)."
        
    )
    fig.update_layout(title_x=0.5)
    return fig

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
                showlegend=False,  # Désactive la légende
                height=600
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
            showlegend=False
        )
    )
    
    # Afficher les informations sur le nœud cliqué
    node_info = f"Vous avez cliqué sur : {clicked_node}. Il est connecté à {len(neighbors)} autres mots."

    return updated_figure, node_info


#callbackpour afficher le bon graph
@app.callback(
    [Output("graph1-container", "style"),
     Output("graph2-container", "style"),
     Output("graph3-container", "style"),
     Output("graph4-container", "style"),
     Output("node-info", "style")],
    [Input("graph-dropdown", "value")]
)
def display_selected_graph(graph_name):
    # Cacher tous les graphiques par défaut
    styles = {'display': 'none'}
    
    # Afficher seulement le graphique sélectionné
    if graph_name == 'graph1':
        return {'display': 'block', 'height': '90vh'}, {'display': 'none'},{'display': 'none'},{'display': 'none'},{'display': 'none'}
    elif graph_name == 'graph2':
        return {'display': 'none'}, {'display': 'block', 'height': '90vh'},{'display': 'none'},{'display': 'none'},{'display': 'none'}
    elif graph_name == 'graph3':
        return {'display': 'none'}, {'display': 'none'},{'display': 'block', 'height': '90vh'},{'display': 'none'},{'display': 'block'},
    elif graph_name == 'graph4':
        return {'display': 'none'}, {'display': 'none'},{'display': 'none'},{'display': 'block', 'height': '90vh'},{'display': 'none'}
    
    return styles, styles,styles,styles

#callback pour le bouton télécharger le fichier source
@app.callback(
    Output("download", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def download_file(n_clicks):
    datadownload = data
    if n_clicks > 0:
        json_data = json.dumps(datadownload, indent=4)
        return dcc.send_string(json_data, "data.json")

# Exécuter l'application
if __name__ == "__main__":
    app.run_server(debug=True)
