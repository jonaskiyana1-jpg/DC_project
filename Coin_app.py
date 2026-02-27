#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import os
import pandas as pd
#%pip install pandas openpyxl
from requests import get # récupérer le contenu html de la page
from bs4 import BeautifulSoup as bs
import seaborn as sns
import matplotlib.pyplot as plt



# In[ ]:


st.markdown("<h1 style='text-align: center; color: black;'>MY DATA APP</h1>", unsafe_allow_html=True)

st.markdown("""
This app allows you to download scraped data on shoes and clothes from coin Africa and to produce dashbords from cleaned data 
* **Python libraries:** base64,pandas, streamlit
* **Data source:** [coinAfr](https://sn.coinafrique.com).
""")


# In[ ]:


# définir quelques styles liés aux box
st.markdown('''<style> .stButton>button {
    font-size: 12px;
    height: 3em;
    width: 25em;
}</style>''', unsafe_allow_html=True)


# Stocker les données dans une database (base de données sql)

# In[ ]:





# In[2]:


# import sqlite3
import sqlite3
# Créer une connexion avec une base de données  (Immobilier.db)
conn = sqlite3.connect('COIN.db')
# créer un curseur (permettant d'intéragir avec la base données)
c = conn.cursor()
# créer une table


# In[ ]:


# Connexion SQL
conn = sqlite3.connect("COIN.db")

# Menu latéral
menu = st.sidebar.selectbox(
    "Choisir une option",
    ["Scraper des données", "Télécharger données brutes", "Voir Dashboard", "Formulaire d'évaluation"]
)

# Bloc 1 : Scraper des données
def collect_data(site, max_pages):
    
        data = []
        for i in range(1, max_pages+1):
            url = site['base_url'].format(page=i)
            res =get(url)
            if res.status_code != 200:
                continue
            soup = bs(res.content, 'html.parser')
            containers = soup.select(site['container'])

            for container in containers:
                try:
                    dic = {
                        'type': container.select_one(site['selectors']['type']).get_text(strip=True),
                        'price': container.select_one(site['selectors']['price']).get_text(strip=True),
                        'adresse': container.select_one(site['selectors']['adresse']).get_text(strip=True),
                        'url_image': container.select_one(site['selectors']['image'])['src']
                    }
                    data.append(dic)
                except Exception:
                    pass

       
        return pd.DataFrame(data)




# In[ ]:


# Navigation
if menu == "Scraper des données":

# Liste des noms personnalisés
    site_names = [
    "chaussures_hommes",
    "vêtements_hommes",
    "vêtements_enfants",
    "chaussures_enfants"
]


    st.subheader("Scraping des données")
    nb_pages = st.slider("Nombre de pages à scraper :", min_value=1, max_value=100, value=5, step=1)

    if st.button("Lancer le scraping"):
        sites = [{ 
        'base_url': 'https://sn.coinafrique.com/categorie/chaussures-homme?page={page}',
        'container': 'div.col.s6.m4.l3',
        'selectors': {
            'type': 'p.ad__card-description',
            'price': 'p.ad__card-price',
            'adresse': 'p.ad__card-location span',
            'image': 'img.ad__card-img'
            }
        },
        {
            'base_url': 'https://sn.coinafrique.com/categorie/vetements-homme?page={page}',
            'container': 'div.col.s6.m4.l3',
            'selectors': {
                'type': 'p.ad__card-description',
                'price': 'p.ad__card-price',
                'adresse': 'p.ad__card-location span',
                'image': 'img.ad__card-img'
            }
        },
        {
            'base_url': 'https://sn.coinafrique.com/categorie/vetements-enfants?page={page}',
            'container': 'div.col.s6.m4.l3',
            'selectors': {
                'type': 'p.ad__card-description',
                'price': 'p.ad__card-price',
                'adresse': 'p.ad__card-location span',
                'image': 'img.ad__card-img'
            }
        },
        {
            'base_url': 'https://sn.coinafrique.com/categorie/chaussures-enfants?page={page}',
            'container': 'div.col.s6.m4.l3',
            'selectors': {
                'type': 'p.ad__card-description',
                'price': 'p.ad__card-price',
                'adresse': 'p.ad__card-location span',
                'image': 'img.ad__card-img'
            }
        }


    ]
   # Création des onglets avec noms personnalisés
        tabs = st.tabs([name for name in site_names])

        for i, tab in enumerate(tabs):
            with tab:
                st.subheader(f"Résultats pour {site_names[i]}")
                df = collect_data(sites[i], max_pages=nb_pages)

                # Nom de table SQL basé sur le nom personnalisé
                table_name = site_names[i]
                df.to_sql(table_name, conn, if_exists="replace", index=False)

                st.success(f"Scraping terminé ({nb_pages} pages) pour {table_name}. Données enregistrées en SQL.")
                st.dataframe(df.head())

elif menu == "Télécharger données brutes":
    st.subheader("Télécharger données brutes")


    # Connexion SQL
    conn = sqlite3.connect("COIN.db")

        # Dossier contenant tes fichiers CSV
    folder ="coinafrica"

        # Parcourir tous les fichiers CSV du dossier
    for file in os.listdir(folder):
            if file.endswith(".csv"):
                file_path = os.path.join(folder, file)

                # Charger le fichier CSV
                df1 = pd.read_csv(file_path)

                # Nom de la table = nom du fichier sans extension
                table_name1 = os.path.splitext(file)[0]

                # Insérer dans SQL
                df1.to_sql(table_name1, conn, if_exists="replace", index=False)

                st.success(f"{file} inséré dans la table {table_name1}")

                # Ajouter un bouton de téléchargement pour chaque CSV
                st.download_button(
                    label=f"Télécharger {file}",
                    data=df1.to_csv(index=False).encode("utf-8"),
                    file_name=file,
                    mime="text/csv"
                )

    conn.close()

elif menu == "Voir Dashboard":
    st.subheader("Dashboard des données nettoyées")
        # Liste des 4 tables nettoyées
    tables_clean = [
    "Chaussures_homme_clean",
    "vetement_homme_clean",
    "vet_enfants_clean",
    "chaussures_enfants_clean"
]
    conn = sqlite3.connect("COIN.db")
        # Création des onglets
    tabs = st.tabs(tables_clean)

    # Parcourir chaque table et l'afficher dans son onglet
    for i, tab in enumerate(tabs):
        with tab:
            table_name = tables_clean[i]
            

            df_clean = pd.read_sql(f"SELECT * FROM {table_name}", conn)

            st.write(f"### Table : {table_name}")
            st.dataframe(df_clean.head())

            # Conversion prix en numérique
            df_clean["prix"] = pd.to_numeric(df_clean["prix"], errors="coerce")

            # Séparer les produits
            df_prix = df_clean[df_clean["prix"] > 0]
            df_sans_prix = df_clean[df_clean["prix"] == 0]

    
            # Déterminer la colonne de type
            if "type_chaussure" in df_clean.columns:
                col_type = "type_chaussure"
            elif "type_habit" in df_clean.columns:
                col_type = "type_habit"
            else:
                col_type = None

            # Sous-onglets
            tab1, tab2, tab3, tab4 = st.tabs([
                "Vue Générale", 
                "Analyse des Prix", 
                "Analyse par Catégorie", 
                "Produits sans prix"
            ])

            # --- Vue Générale ---
            with tab1:
                st.subheader("Vue Générale")
                df_prix = df_clean[df_clean["prix"] > 0]
                df_sans_prix = df_clean[df_clean["prix"] == 0]

                if "type_chaussure" in df_clean.columns:
                    col_type = "type_chaussure"
                elif "type_habit" in df_clean.columns:
                    col_type = "type_habit"
                else:
                    col_type = None

                st.metric("Prix moyen", f"{df_prix['prix'].mean():,.0f} FCFA")
                st.metric("Prix minimum", f"{df_prix['prix'].min():,.0f} FCFA")
                st.metric("Prix maximum", f"{df_prix['prix'].max():,.0f} FCFA")
                st.metric("Produits avec prix", len(df_prix))
                st.metric("Produits sans prix", len(df_sans_prix))
                if col_type:
                    st.metric("Nombre de catégories", df_prix[col_type].nunique())

            # --- Analyse des Prix ---
            with tab2:
                st.subheader("Analyse des Prix")
                bins = [0, 5000, 10000, 20000, 50000, 100000]
                df_prix["classe_prix"] = pd.cut(df_prix["prix"], bins=bins).astype(str)
                prix_counts = df_prix["classe_prix"].value_counts().sort_index()
                st.bar_chart(prix_counts)

                plt.figure(figsize=(8,5))
                sns.boxplot(x=df_prix["prix"])
                st.pyplot(plt)

                if col_type:
                    # Prix moyen par catégorie
                    st.markdown("### 💰 Prix moyen par catégorie")

                    st.write(df_prix.groupby(col_type)["prix"].mean().sort_values(ascending=False))
                    # Top 10 produits les plus chers
                    st.markdown("### 🔝 Top 10 produits les plus chers")

                    st.write(df_prix.nlargest(10, "prix")[[col_type, "prix"]] if col_type else df_prix.nlargest(10, "prix"))

            # --- Analyse par Catégorie ---
            with tab3:
                st.subheader("Analyse par Catégorie")
                if col_type:
                    st.bar_chart(df_prix[col_type].value_counts())
                    st.write(df_prix.groupby(col_type)["prix"].mean().sort_values(ascending=False))
                else:
                    st.warning("Pas de colonne type disponible pour cette table.")

            # --- Produits sans prix ---
            with tab4:
                st.subheader("Produits sans prix (à demander)")
                st.write(f"Nombre de produits sans prix : {len(df_sans_prix)}")

                # Vérifier colonnes image et adresse
                if "image_lien" in df_sans_prix.columns:
                    image_col = "image_lien"
                elif "url_image" in df_sans_prix.columns:
                    image_col = "url_image"
                else:
                    image_col = None

                if "adresse" in df_sans_prix.columns:
                    adresse_col = "adresse"
                elif "location" in df_sans_prix.columns:
                    adresse_col = "location"
                else:
                    adresse_col = None

                # Affichage des 10 premiers produits sans prix
                for _, row in df_sans_prix.head(10).iterrows():
                    caption = row.get(col_type, "Produit")
                    if adresse_col:
                        caption += f" - {row[adresse_col]}"
                    else:
                        caption += " - adresse non disponible"

                    if image_col:
                        st.image(row[image_col], caption=caption)
                    else:
                        st.write(caption)

                # Bouton d’export CSV
                st.download_button(
                    label="📥 Télécharger la liste complète des produits sans prix",
                    data=df_sans_prix.to_csv(index=False).encode("utf-8"),
                    file_name="produits_sans_prix.csv",
                    mime="text/csv",
                    key=f"download_{table_name}_sans_prix"  # clé unique
                )
    conn.close()
elif menu == "Formulaire d'évaluation":
    st.subheader("Formulaire d'évaluation")
    st.markdown("[📝 Remplir le formulaire](https://ee.kobotoolbox.org/x/2rrMWz1a)")


