import streamlit as st
import pandas as pd
import plotly.express as px

# Autentification
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🔐 Accès à l'application")

    nom = st.text_input("Nom")
    prenom = st.text_input("Prénom")
    mot_de_passe = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if not nom.strip() or not prenom.strip() or not mot_de_passe.strip():
            st.error("Veuillez remplir Nom, Prénom et Mot de passe.")
        else:
            st.session_state["logged_in"] = True
            st.session_state["nom"] = nom.strip()
            st.session_state["prenom"] = prenom.strip()

    st.stop() #bloque tout lorsque cest pas connecté
st.set_page_config(layout="wide")
st.title("Tableau de bord - Commerce extérieur")

#chargement des données
df = pd.read_excel("WITS_FUSION_FINAL.xlsx")
df.columns = df.columns.str.strip()

df = df.rename(columns={
    "Year": "Année",
    "Export (US$ Thousand)": "Export",
    "Import (US$ Thousand)": "Import",
    "Product Group": "Produit"
})

col_year = "Année"
col_import = "Import"
col_export = "Export"
col_product = "Produit"

# Filtres
annee = st.sidebar.selectbox("Année", sorted(df[col_year].unique()))
produit = st.sidebar.selectbox(
    "Produit",
    ["Tous"] + sorted(df[col_product].unique())
)

df_f = df[df[col_year] == annee]

if produit != "Tous":
    df_f = df_f[df_f[col_product] == produit]

# KPI
import_total = df_f[col_import].sum()
export_total = df_f[col_export].sum()
balance = export_total - import_total

col1, col2, col3 = st.columns(3)

col1.metric(" Import", f"{import_total:,.0f}")
col2.metric(" Export", f"{export_total:,.0f}")
col3.metric(" Balance", f"{balance:,.0f}")

# Graph évolution
df_group = df.groupby(col_year)[[col_import, col_export]].sum().reset_index()
fig1 = px.line(
    df_group,
    x=col_year,
    y=[col_import, col_export],
    markers=True,
    title="Évolution Import / Export"
)
fig1.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
fig1.update_traces(
    selector=dict(name="Import"),
    line=dict(color="#f35912", width=3)
)
fig1.add_vline(x=annee, line_dash="dash", line_color="red")


# GRAPH 2 : BALANCE
df_group["Balance"] = df_group[col_export] - df_group[col_import]
fig2 = px.line(
    df_group,
    x=col_year,
    y="Balance",
    markers=True,
    title=" Balance commerciale"
)
fig2.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
fig2.update_traces(line=dict(color="#12f382"))


# GRAPH 3 : TOP IMPORT 
top_import = df_f.groupby(col_product)[col_import].sum().nlargest(10).reset_index()
fig3 = px.bar(
    top_import,
    x=col_import,
    y=col_product,
    orientation="h",
    title=f"Top Importations - {annee}"
)
fig3.update_layout(height=400, margin=dict(l=15, r=15, t=30, b=15))
fig3.update_traces(marker_color="#7C2F62")


#GRAPH 4 : TOP EXPORT 
top_export = df_f.groupby(col_product)[col_export].sum().nlargest(10).reset_index()
fig4 = px.bar(
    top_export,
    x=col_export,
    y=col_product,
    orientation="h",
    title=f"Top Exportations - {annee}"
)
fig4.update_layout(height=400, margin=dict(l=10, r=10, t=30, b=10))
fig4.update_traces(marker_color="#286117")


col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1, use_container_width=True, key="graph1")
with col2:
    st.plotly_chart(fig2, use_container_width=True, key="graph2")

#Interpretation automatique de la balance commerciale
if balance > 0:
        st.success(f"En {annee}, la balnce commerciale est excedentaire.")
elif balance < 0:
    st.error(f"En {annee}, la balance commerciale est déficitaire.")
else:
    st.info("la balance commerciale est équilibrée")


col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig3, use_container_width=True, key="graph3")
with col4:
    st.plotly_chart(fig4, use_container_width=True, key="graph4")
    
    # Bse de donnée
st.subheader("Données")
st.dataframe(df_f)



