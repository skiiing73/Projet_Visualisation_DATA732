import json
from collections import Counter
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Chargement des données
with open("fr.sputniknews.africa--20220630--20230630.json", "r") as f:
    data = json.load(f)

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Layout de l'application
app.layout = html.Div([
    html.H1("Analyse des mots-clés par pays"),
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
        clearable=False
    ),
    dcc.Graph(id="keyword-bar-chart")
])

# Fonction pour extraire les mots-clés en fonction du pays
def get_keywords_for_country(pays):
    keywords = {}

    # Extraction de la liste des keywords par articles
    for year, data_year in data.get('data', {}).items():  # Parcours des années
        for month, data_month in data_year.items():  # Parcours des mois
            for day, data_day in data_month.items():  # Parcours des jours
                for data_article in data_month[day]:  # Parcours des articles
                    if pays in data_article.get('loc', {}):  # Vérification du pays
                        for kws, values in data_article.get('kws', {}).items():  # Parcours des mots-clés et leurs valeurs
                            if kws != "pays":  # Supprimer le mot "pays" non pertinent
                                # Enlever le pluriel pour les mots finissant en "s" (hors "paris")
                                if kws.endswith('s') and len(kws) > 1 and kws != "paris":
                                    kws = kws[:-1]
                                keywords[kws] = keywords.get(kws, 0) + values  # Mise à jour du dictionnaire

    # Supprimer le pays des mots-clés s'il est présent
    if pays.lower() in keywords:
        del keywords[pays.lower()]

    # Trier et garder les 15 mots les plus fréquents
    top_words = dict(Counter(keywords).most_common(15))
    return top_words


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
    fig = px.bar(x=words, y=occurrences, labels={'x': 'Mots', 'y': 'Occurrences'},
                 title=f"Top 15 des mots les plus utilisés lorsque {pays} est cité.")
    return fig

# Exécuter l'application
if __name__ == "__main__":
    app.run_server(debug=True)
 