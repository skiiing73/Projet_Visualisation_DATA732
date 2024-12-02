import json
import re
import unicodedata
import pycountry
import pandas as pd
import plotly.express as px

# Chargement des données
with open("fr.sputniknews.africa--20220630--20230630.json", "r") as f:
    data = json.load(f)

# Extraction de la liste de localisation
data_loc = data.get('metadata', {}).get('all', {}).get('loc', {})

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
    "Congo": "Congo",
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
    "Uruguay": "Uruguay",
    "Vanuatu": "Vanuatu",
    "Vatican": "Vatican City",
    "Venezuela": "Venezuela",
    "Viêt Nam": "Vietnam",
    "Yémen": "Yemen",
    "Zambie": "Zambia",
    "Zimbabwe": "Zimbabwe"
}


# Fonction pour normaliser les noms des pays en supprimant les articles définis et en utilisant les codes ISO
def normalize_country_name(name):
    # Supprimer les articles définis
    name = re.sub(r"^(l’|la |le |les )", "", name, flags=re.IGNORECASE)
    
    # Supprimer les accents
    name = ''.join(
        c for c in unicodedata.normalize('NFD', name)
        if unicodedata.category(c) != 'Mn'
    )
    
    if name in pays_traduction.keys():
        return pays_traduction[name]

    return name


# Appliquer la normalisation aux noms de pays
normalized_data_loc = {}
for pays, values in data_loc.items():
    pays_normalize = normalize_country_name(pays)
    
    if pays_normalize in normalized_data_loc:
        normalized_data_loc[pays_normalize] += values
    else:
        normalized_data_loc[pays_normalize] = values

# Vérification des pays normalisés
print(normalized_data_loc)
print("\n\n\n\n")

# Conversion en DataFrame
df = pd.DataFrame(list(normalized_data_loc.items()), columns=['Country', 'Frequency'])

# Créer la carte
fig = px.scatter_geo(df, locations="Country", locationmode="country names",
                     color="Frequency", size="Frequency",
                     size_max=50,  # Augmenter cette valeur pour des bulles plus grandes
                     projection="natural earth",
                     title="Distribution des pays")
fig.show()