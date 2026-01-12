import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Alchimiste - Convertisseur", layout="wide")

# --- LISTE OFFICIELLE DES SKUS (ORDRE FIXE) ---
SKU_MASTER_LIST = [
    "** 4 PACK ** BLONDE", "** 4 PACK ** ECOSSAISE", "** 4 PACK ** IPA", 
    "** 4 PACK ** ROUSSE", "** CAISSE DE 12 **IPA", "CS DE 12 ** QUATUOR",
    "**4 PACK** CALIFORNIA IPA", "**4 PACK** PROJET TROPICAL", 
    "**CAISSE DE 12 ** BOCK DE JOLI", "**CAISSE DE 12* TOKYO IPA", 
    "**CAISSE DE 12** ARIZONA MONUM", "**CAISSE DE 12** BLANCHE PILON", 
    "**CAISSE DE 12** BLONDE", "**CAISSE DE 12** CABANA", 
    "**CAISSE DE 12** CALIFORNIA ST", "**CAISSE DE 12** DRY STOUT", 
    "**CAISSE DE 12** ECOSSAISE", "**CAISSE DE 12** FLEUR", 
    "**CAISSE DE 12** FORÊT", "**CAISSE DE 12** IPA", 
    "**CAISSE DE 12** LA BITTER", "**CAISSE DE 12** LA BLANCHE CL", 
    "**CAISSE DE 12** LA GOSE", "**CAISSE DE 12** LA ROUSSE", 
    "**CAISSE DE 12** PALE ALE", "**CAISSE DE 12** PARASOL", 
    "**CAISSE DE 12** PLUME", "**CAISSE DE 12** PROJET TROPIC", 
    "**CAISSE DE 12** SANS ALCOOL B", "**CAISSE DE 12** SANS ALCOOL E", 
    "**CAISSE DE 12** SANS ALCOOL G", "**CAISSE DE 12** SANS ALCOOL I", 
    "**CAISSE DE 12** SANS ALCOOL S", "**CAISSE DE 12** YUKON", 
    "**CAISSES DE 12** BIG SURF", "**SANS GLUTEN & SANS ALCOOL ****", 
    "**SANS GLUTEN ** 4 PACK ** BLA", "**SANS GLUTEN ** 4 PACK ** BLO", 
    "**SANS GLUTEN ** 4 PACK ** IPA", "**SANS GLUTEN ** 4 PACK ** ROU", 
    "**SANS GLUTEN ** CS DE 12 ** ULTRA"
]

st.title("🍺 Alchimiste : Traitement de Ventes")
uploaded_file = st.file_uploader("Glissez le fichier CSV ici", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Nettoyage
    df['LineQty'] = pd.to_numeric(df['LineQty'], errors='coerce').fillna(0)
    df['LineTotal'] = pd.to_numeric(df['LineTotal'], errors='coerce').fillna(0)
    df['Rabais'] = pd.to_numeric(df['Rabais'], errors='coerce').fillna(0)

    # Fonction pour forcer l'ordre et inclure les zéros
    def force_sku_order(data_df, value_cols):
        # Créer un DataFrame vide avec tous les SKUs
        base = pd.DataFrame({'ItemName': SKU_MASTER_LIST})
        # Fusionner avec les données réelles
        merged = pd.merge(base, data_df, on='ItemName', how='left').fillna(0)
        return merged

    # 1. Ventes par SKU (Caisses)
    res_sku = df.groupby('ItemName')['LineQty'].sum().reset_index()
    res_sku = force_sku_order(res_sku, 'LineQty')

    # 2. Ventes par SKU par Jour
    res_jour = df.pivot_table(index='ItemName', columns='DocDate', values='LineQty', aggfunc='sum', fill_value=0).reset_index()
    res_jour = force_sku_order(res_jour, []) # Les colonnes de dates seront ajoutées par le merge

    # 6. Ventes SKU Financier
    res_fin = df.groupby('ItemName').agg({'LineTotal': 'sum', 'Rabais': 'sum'}).reset_index()
    res_fin = force_sku_order(res_fin, ['LineTotal', 'Rabais'])

    # Autres (Bannière, Région, Rep) - Pas d'ordre fixe demandé ici
    res_banniere = df.groupby('GroupName')['LineQty'].sum().reset_index()
    res_region = df.groupby('CityS')['LineQty'].sum().reset_index()
    res_rep = df.groupby('RefPartenaire')['LineQty'].sum().reset_index()

    # Création du fichier Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        res_sku.to_excel(writer, sheet_name='Ventes_SKU_Caisses', index=False)
        res_jour.to_excel(writer, sheet_name='Ventes_SKU_Par_Jour', index=False)
        res_banniere.to_excel(writer, sheet_name='Ventes_Banniere', index=False)
        res_region.to_excel(writer, sheet_name='Ventes_Region', index=False)
        res_rep.to_excel(writer, sheet_name='Ventes_Representant', index=False)
        res_fin.to_excel(writer, sheet_name='Ventes_Financier', index=False)
    
    st.success("✅ Fichier prêt !")
    st.download_button("📥 Télécharger Excel", output.getvalue(), "Ventes_Alchimiste.xlsx")
