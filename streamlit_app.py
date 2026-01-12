import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Alchimiste - Convertisseur", layout="wide")

# --- MAPPING OFFICIEL : ITEMCODE -> NOM DE SKU (ORDRE FIXE) ---
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
    "MASABLO12": "**CAISSE DE 12** SANS ALCOOL B",
    "MASABLA12": "**CAISSE DE 12** SANS ALCOOL B ",
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

st.title("🍺 Alchimiste : Traitement Pro")

uploaded_file = st.file_uploader("Glissez le fichier CSV ici", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, encoding='latin1')
        
        # Nettoyage numérique
        for col in ['LineQty', 'LineTotal', 'Rabais']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)

        # Mapping des noms propres
        df['Nom_Propre'] = df['ItemCode'].map(SKU_MAPPING).fillna(df['ItemName'])

        def force_order(data_df):
            base = pd.DataFrame({'Nom_Propre': SKU_ORDER})
            merged = pd.merge(base, data_df, on='Nom_Propre', how='left').fillna(0)
            return merged.rename(columns={'Nom_Propre': 'ItemName'})

        # Préparation des DataFrames
        data_sheets = {
            'SKU_Caisses': force_order(df.groupby('Nom_Propre')['LineQty'].sum().reset_index()),
            'SKU_Par_Jour': force_order(df.pivot_table(index='Nom_Propre', columns='DocDate', values='LineQty', aggfunc='sum', fill_value=0).reset_index()),
            'Banniere_Caisses': df.groupby('GroupName')['LineQty'].sum().sort_values(ascending=False).reset_index(),
            'Region_Caisses': df.groupby('CityS')['LineQty'].sum().sort_values(ascending=False).reset_index(),
            'Rep_Caisses': df.groupby('RefPartenaire')['LineQty'].sum().sort_values(ascending=False).reset_index(),
            'SKU_Financier': force_order(df.groupby('Nom_Propre').agg({'LineTotal': 'sum', 'Rabais': 'sum'}).reset_index())
        }

        # Export avec mise en page
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            for sheet_name, data in data_sheets.items():
                data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Accès à l'objet xlsxwriter pour le formatage
                worksheet = writer.sheets[sheet_name]
                workbook = writer.book
                header_format = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
                
                # Ajustement automatique de la largeur des colonnes
                for i, col in enumerate(data.columns):
                    column_len = max(data[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(i, i, column_len)
                    worksheet.write(0, i, col, header_format)

        st.success("✅ Fichier prêt avec mise en page !")
        st.download_button("📥 Télécharger Excel Formaté", output.getvalue(), "Ventes_Alchimiste_Pro.xlsx")

    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
