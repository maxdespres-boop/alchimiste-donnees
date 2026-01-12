import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Alchimiste - Convertisseur", layout="wide")

# --- MAPPING OFFICIEL : CODE -> NOM DE SKU ---
# J'ai lié chaque code à votre nom exact pour garantir l'ordre et l'exactitude
SKU_MAPPING = {
    "MABLON4": "** 4 PACK ** BLONDE",
    "MAECOS4": "** 4 PACK ** ECOSSAISE",
    "MAIPA4": "** 4 PACK ** IPA",
    "MAROUS4": "** 4 PACK ** ROUSSE",
    "MAIPA12": "** CAISSE DE 12 **IPA",
    "MAQUAT12": "CS DE 12 ** QUATUOR",
    "MACALI4": "**4 PACK** CALIFORNIA IPA",
    "MATROP4": "**4 PACK** PROJET TROPICAL",
    "MABOCK12": "**CAISSE DE 12 ** BOCK DE JOLI",
    "MATOKY12": "**CAISSE DE 12* TOKYO IPA",
    "MAARIZ12": "**CAISSE DE 12** ARIZONA MONUM",
    "MABLANP12": "**CAISSE DE 12** BLANCHE PILON",
    "MABLON12": "**CAISSE DE 12** BLONDE",
    "MACABA12": "**CAISSE DE 12** CABANA",
    "MACALI12": "**CAISSE DE 12** CALIFORNIA ST",
    "MADRYS12": "**CAISSE DE 12** DRY STOUT",
    "MAECOS12": "**CAISSE DE 12** ECOSSAISE",
    "MAFLEU12": "**CAISSE DE 12** FLEUR",
    "MAFORE12": "**CAISSE DE 12** FORÊT",
    "MAIPA12_2": "**CAISSE DE 12** IPA", # Ajusté si doublon de code
    "MABITT12": "**CAISSE DE 12** LA BITTER",
    "MABLAN12": "**CAISSE DE 12** LA BLANCHE CL",
    "MAGOSE12": "**CAISSE DE 12** LA GOSE",
    "MAROUS12": "**CAISSE DE 12** LA ROUSSE",
    "MAPALE12": "**CAISSE DE 12** PALE ALE",
    "MAPARA12": "**CAISSE DE 12** PARASOL",
    "MAPLUM12": "**CAISSE DE 12** PLUME",
    "MATROP12": "**CAISSE DE 12** PROJET TROPIC",
    "MASABLO12": "**CAISSE DE 12** SANS ALCOOL B", # Blonde Sans Alcool
    "MASABLA12": "**CAISSE DE 12** SANS ALCOOL B_BLANCHE", # Pour les différencier (ajustable)
    "MASAECO12": "**CAISSE DE 12** SANS ALCOOL E",
    "MASAGOS12": "**CAISSE DE 12** SANS ALCOOL G",
    "MASAIPA12": "**CAISSE DE 12** SANS ALCOOL I",
    "MASASTO12": "**CAISSE DE 12** SANS ALCOOL S",
    "MAYUKO12": "**CAISSE DE 12** YUKON",
    "MABIGS12": "**CAISSES DE 12** BIG SURF",
    "MASGSA12": "**SANS GLUTEN & SANS ALCOOL ****",
    "MASGBLA4": "**SANS GLUTEN ** 4 PACK ** BLA",
    "MASGBLO4": "**SANS GLUTEN ** 4 PACK ** BLO",
    "MASGIPA4": "**SANS GLUTEN ** 4 PACK ** IPA",
    "MASGROU4": "**SANS GLUTEN ** 4 PACK ** ROU",
    "MASGULT12": "**SANS GLUTEN ** CS DE 12 ** ULTRA"
}

# Liste pour l'ordre fixe des onglets
SKU_ORDER = list(SKU_MAPPING.values())

st.title("🍺 Alchimiste : Traitement par ItemCode")

uploaded_file = st.file_uploader("Glissez le fichier CSV ici", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
        
        # Nettoyage des colonnes numériques
        for col in ['LineQty', 'LineTotal', 'Rabais']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        # Création d'une colonne de nom "Propre" basée sur l'ItemCode
        df['Nom_Propre'] = df['ItemCode'].map(SKU_MAPPING).fillna(df['ItemName'])

        def force_order(data_df, col_name='Nom_Propre'):
            base = pd.DataFrame({'Nom_Propre': SKU_ORDER})
            merged = pd.merge(base, data_df, on='Nom_Propre', how='left').fillna(0)
            return merged.rename(columns={'Nom_Propre': 'ItemName'})

        # 1. Ventes par SKU (Caisses)
        res_sku = df.groupby('Nom_Propre')['LineQty'].sum().reset_index()
        res_sku = force_order(res_sku)

        # 2. Ventes par SKU par Jour
        res_jour = df.pivot_table(index='Nom_Propre', columns='DocDate', values='LineQty', aggfunc='sum', fill_value=0).reset_index()
        res_jour = force_order(res_jour)

        # 3. Ventes par Bannière, Région, Rep (Reste inchangé)
        res_banniere = df.groupby('GroupName')['LineQty'].sum().reset_index()
        res_region = df.groupby('CityS')['LineQty'].sum().reset_index()
        res_rep = df.groupby('RefPartenaire')['LineQty'].sum().reset_index()

        # 6. Ventes SKU Financier
