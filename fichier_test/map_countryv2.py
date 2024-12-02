import json
import re
import unicodedata
import pycountry
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Chargement des données
with open("fr.sputniknews.africa--20220630--20230630.json", "r") as f:
    data = json.load(f)

# Extraction de la liste de localisation
data_2023 = data.get('metadata', {}).get('month', {}).get('2023', {})
data_2022 = data.get('metadata', {}).get('month', {}).get('2022', {})

print("data extracted")
#on trie par mois afin que ce soit dans le bon ordre des moisq
data_2022=dict(sorted(data_2022.items(), key=lambda item: int(item[0])))
data_2023=dict(sorted(data_2023.items(), key=lambda item: int(item[0])))


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
    
print("data combined")

# Normaliser les noms des pays
normalized_data_month = {}
for month, data_mensuelle in data_month.items():
    normalized_data_month_en_cours = {}

    for pays, values in data_mensuelle.items():
        pays_normalize = normalize_country_name(pays)
        if pays_normalize != None:
            normalized_data_month_en_cours[pays_normalize] = normalized_data_month_en_cours.get(pays_normalize, 0) + values

    normalized_data_month[month] = normalized_data_month_en_cours
    
print("data normalized") 

# Créer les frames pour l'animation
frames = []
for month, values in normalized_data_month.items():
    frame_data = [{'Country': pays, 'Frequency': freq, 'Month': f'{month}'} for pays, freq in values.items()]
    frames.append(pd.DataFrame(frame_data))


# Créer la figure avec le graphique géographique
fig = go.Figure()

scale_factor = 5#facteur pour diminuer la taille des ronds

# Ajouter le premier mois comme trace de base
first_month = next(iter(data_month))
frame = frames[0]  # Le premier mois dans les frames
fig.add_trace(go.Scattergeo(
    locations=frame['Country'],
    locationmode="country names",
    text=frame['Frequency'],
    marker=dict(
        size=frame['Frequency']/scale_factor,
        color=frame['Frequency'],
        showscale=True,
        sizemode='diameter',
        colorbar=dict(title="Frequency")
    ),
))

#differentes frames a afficher
fig.frames = [
    go.Frame(
        data=[go.Scattergeo(
            locations=frame['Country'],
            locationmode="country names",
            text=frame['Frequency'],
            marker=dict(
                size=frame['Frequency']/scale_factor,
                color=frame['Frequency'],
                showscale=True,
                sizemode='diameter',
                colorbar=dict(title="Frequency")
            ),
        )],
        name=f"Month: {month} " + ("- 2022" if int(month) > 7 else "- 2023")  # Ajouter l'année selon le mois
    )
    for month, frame in zip(data_month.keys(), frames)
]

#updtae du slider et des frames
fig.update_layout(
    title="Fréquence des mentions par pays(2022-2023)",  # Titre du graphique
    title_x=0.5,  # Centrer le titre
    sliders=[{
        "currentvalue": {"prefix": "Month: ", "visible": True, "xanchor": "center"},
        "steps": [
            {
                "args": [
                    [f"Month: {month} " + ("- 2022" if int(month) > 7 else "- 2023")],
                    {"frame": {"duration": 0, "redraw": True}, "mode": "immediate", "transition": {"duration": 0}},
                ],
                "label": f"{month} " + ("- 2022" if int(month) > 7 else "- 2023"),
                "method": "animate",
            }
            for month in data_month.keys()
        ],
    }]
)


# Afficher le graphique
fig.write_html("map.html")
print("data mapped")
