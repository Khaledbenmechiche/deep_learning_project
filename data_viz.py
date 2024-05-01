import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Chargement du fichier de données traitées
df_viz = pd.read_csv("data/donnees_traitees.csv")

# Titre de l'application
st.title("Analyse des points de charge pour véhicules électriques")

# Sous-titre et lien vers la documentation
st.markdown("### **Données utilisées**")
st.subheader("Fichier consolidé des Bornes de Recharge pour Véhicules Électriques")
st.write("[Documentation api 1](https://www.data.gouv.fr/fr/datasets/fichier-consolide-des-bornes-de-recharge-pour-vehicules-electriques/#/resources)")
st.subheader("Voitures particulières immatriculées par commune et par type de recharge")
st.write("[Documentation api 2](https://www.data.gouv.fr/fr/datasets/voitures-particulieres-immatriculees-par-commune-et-par-type-de-recharge-jeu-de-donnees-aaadata/#/community-reuses)")

# Convertir la colonne 'date_mise_en_service' en datetime
df_viz['date_mise_en_service'] = pd.to_datetime(df_viz['date_mise_en_service'])

# Agréger les données par mois et extraire l'année pour l'affichage
df_viz['year_month'] = df_viz['date_mise_en_service'].dt.to_period('M').apply(lambda x: x.start_time)

# Grouper les données par année et compter le nombre de points de charge et de stations uniques
df_count_by_year = df_viz.groupby(df_viz['year_month']).agg({
    'id_pdc_itinerance': 'count',
    'id_station_itinerance': 'nunique'  # Nombre de stations uniques
}).reset_index()

# Affichage interactif avec st.line_chart() en spécifiant l'axe des x comme 'year_month'
chart = st.line_chart(df_count_by_year.set_index('year_month'))

# Supprimer la colonne temporaire 'year_month' après utilisation
df_viz.drop('year_month', axis=1, inplace=True)


# Liste des colonnes à analyser
columns_to_analyze = [
    'implantation_station',
    'date_mise_en_service',
    'consolidated_is_lon_lat_correct',
    'consolidated_is_code_insee_verified',
    'nom_departement'
]

# Sélection de la colonne à analyser à l'aide d'un widget de sélection (filtre)
selected_column = st.selectbox("Sélectionner une colonne à analyser:", options=columns_to_analyze)

# Vérification que la colonne sélectionnée est valide
if selected_column:
    # Calcul du nombre de chaque valeur unique dans la colonne sélectionnée
    value_counts = df_viz[selected_column].value_counts()

    # Affichage des résultats sous forme de titre
    st.header(f"Analyse de la colonne '{selected_column}'")

    # Affichage de l'histogramme pour la colonne sélectionnée
    st.bar_chart(value_counts)





# Filtrer les données pour les colonnes pertinentes
df_filtered = df_viz[['id_pdc_itinerance', 'consolidated_longitude', 'consolidated_latitude', 'nom_departement', 'nb_vp_rechargeables_el', 'nom_region']]

# Titre de l'application
st.title("Répartition des points de charge et des véhicules électriques sur la carte")

# Créer une carte centrée sur la France
m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

# Créer un cluster de marqueurs pour regrouper les points de charge
marker_cluster_pdc = MarkerCluster().add_to(m)

# Créer un dictionnaire pour stocker les clusters de véhicules par région
region_clusters = {}

# Parcourir chaque ligne du DataFrame filtré
for index, row in df_filtered.iterrows():
    id_pdc = row['id_pdc_itinerance']
    latitude = row['consolidated_latitude']
    longitude = row['consolidated_longitude']
    departement = row['nom_departement']
    nb_vp = row['nb_vp_rechargeables_el']
    region = row['nom_region']
    
    # Créer un popup pour le point de charge
    popup_text_pdc = f"ID: {id_pdc}<br>Latitude: {latitude}<br>Longitude: {longitude}<br>Département: {departement}"
    
    # Ajouter un marqueur pour chaque point de charge au cluster
    folium.Marker([latitude, longitude], popup=popup_text_pdc).add_to(marker_cluster_pdc)
    
    # Créer un cluster de marqueurs pour les véhicules par région si la région n'existe pas encore
    if region not in region_clusters:
        region_clusters[region] = MarkerCluster().add_to(m)
    
    # Créer un popup pour le nombre de véhicules électriques par région
    popup_text_vp = f"Région: {region}<br>Nombre de véhicules électriques: {nb_vp}"
    
    # Ajouter un marqueur pour le nombre de véhicules électriques à son cluster de région correspondant
    folium.Marker([latitude, longitude], popup=popup_text_vp).add_to(region_clusters[region])

# Afficher la carte Folium dans Streamlit
folium_static(m)