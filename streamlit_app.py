import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Alchimiste - Convertisseur", layout="wide")

# --- MAPPING OFFICIEL : ITEMCODE -> NOM DE SKU (ORDRE FIXE) ---
# Ce dictionnaire assure que même avec des noms identiques, le Code fait foi.
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
    "MAIPA12": "**CAISSE DE 12** IPA",
    "MABITT12": "**CAISSE DE 12** LA BITTER",
    "MABLAN12": "**CAISSE DE 12** LA BLANCHE CL",
    "MAGOSE12": "**CAISSE DE 12** LA GOSE",
    "MAROUS12": "**CAISSE DE 12** LA ROUSSE",
    "MAPALE12": "**CAISSE DE 12** PALE ALE",
    "MAPARA12": "**CAISSE DE 12** PARASOL",
    "MAPLUM12": "**CAISSE DE 12** PLUME",
    "MATROP12": "**CAISSE DE 12** PROJET TROPIC",
    "MASABLO12": "**CAISSE DE 12** SANS ALCOOL B",  # BLONDE
    "MASABLA12": "**CAISSE DE 12** SANS ALCOOL B ", # BLANCHE (Espace ajouté pour différencier au besoin)
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

SKU_ORDER = list(SKU_MAPPING.values())

st.title("🍺 Alchimiste : Traitement des Ventes")
uploaded_file = st.file_uploader("Glissez le fichier CSV ici", type="csv")

if uploaded_file:
    try:
        # Lecture avec encodage pour les accents
        df = pd.read_csv(uploaded_file, encoding='latin1')
        
        # Nettoyage numérique
        for col in ['LineQty', 'LineTotal', 'Rabais']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        # Mapping des noms propres via ItemCode
        df['Nom_Propre'] = df['ItemCode'].map(SKU_MAPPING).fillna(df['ItemName'])

        def force_order(data_df):
            base = pd.DataFrame({'Nom_Propre': SKU_ORDER})
            merged = pd.merge(base, data_df, on='Nom_Propre', how='left').fillna(0)
            return merged.rename(columns={'Nom_Propre': 'ItemName'})

        # --- CALCULS DES ONGLETS ---
        res_sku = df.groupby('Nom_Propre')['LineQty'].sum().reset_index()
        res_sku = force_order(res_sku)

        res_jour = df.pivot_table(index='Nom_Propre', columns='DocDate', values='LineQty', aggfunc='sum', fill_value=0).reset_index()
        res_jour = force_order(res_jour)

        res_banniere = df.groupby('GroupName')['LineQty'].sum().sort_values(ascending=False).reset_index()
        res_region = df.groupby('CityS')['LineQty'].sum().sort_values(ascending=False).reset_index()
        res_rep = df.groupby('RefPartenaire')['LineQty'].sum().sort_values(ascending=False).reset_index()

        res_fin = df.groupby('Nom_Propre').agg({'LineTotal': 'sum', 'Rabais': 'sum'}).reset_index()
        res_fin = force_order(res_fin)

        # Création du fichier Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            res_sku.to_excel(writer, sheet_name='SKU_Caisses', index=False)
            res_jour.to_excel(writer, sheet_name='SKU_Par_Jour', index=False)
            res_banniere.to_excel(writer, sheet_name='Banniere_Caisses', index=False)
            res_region.to_excel(writer, sheet_name='Region_Caisses', index=False)
            res_rep.to_excel(writer, sheet_name='Rep_Caisses', index=False)
            res_fin.to_excel(writer, sheet_name='SKU_Financier', index=False)

        st.success("✅ Fichier prêt !")
        st.download_button("📥 Télécharger Excel", output.getvalue(), "Ventes_Hebdo_Alchimiste.xlsx")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
