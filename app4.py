import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tableau de bord - Commerce extérieur", layout="wide")

# Authentification
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

    st.stop()  # bloque tout lorsque c'est pas connecté

if st.sidebar.button("Se déconnecter"):
    st.session_state["logged_in"] = False
    st.experimental_rerun()

st.title("Tableau de bord - Commerce extérieur")

# Chargement des données
DATA_FILE = "WITS_FUSION_FINAL.xlsx"

try:
    df = pd.read_excel(DATA_FILE)
except FileNotFoundError:
    st.error(f"Fichier de données introuvable : {DATA_FILE}")
    st.stop()

if df.empty:
    st.error("Le fichier de données est vide.")
    st.stop()

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

# TAUX DE CROISSANCE
annees_dispo = sorted(df[col_year].unique())

if len(annees_dispo) >= 2 and annee != annees_dispo[0]:
    annee_prec = annees_dispo[annees_dispo.index(annee) - 1]
    df_prec = df[df[col_year] == annee_prec]
    import_prec = df_prec[col_import].sum()
    export_prec = df_prec[col_export].sum()
    taux_import = ((import_total - import_prec) / import_prec) * 100 if import_prec > 0 else 0
    taux_export = ((export_total - export_prec) / export_prec) * 100 if export_prec > 0 else 0
else:
    taux_import = None
    taux_export = None

st.header(f"Synthèse - {annee}")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Import", f"{import_total:,.0f}")
with col2:
    st.metric("Export", f"{export_total:,.0f}")
with col3:
    st.metric("Balance", f"{balance:,.0f}")
with col4:
    st.metric("Taux de Croissance Import",
              f"{taux_import:+.2f} %" if taux_import is not None else "N/A")
with col5:
    st.metric("Taux de Croissance Export",
              f"{taux_export:+.2f} %" if taux_export is not None else "N/A")


# INTERPRETATION TAUX DE CROISSANCE
if taux_import is not None and taux_export is not None:
    if taux_export > 0 and taux_import > 0:
        if taux_export > taux_import:
            st.success(
                f"✅ En {annee}, les exportations ont enregistré une hausse de {taux_export:+.2f}% "
                f"contre {taux_import:+.2f}% pour les importations. "
                f"Cette progression des exportations supérieure aux importations traduit une amélioration "
                f"de la compétitivité commerciale du pays et contribue positivement à la balance commerciale."
            )
        elif taux_import > taux_export:
            st.warning(
                f"⚠️ En {annee}, les importations ont progressé de {taux_import:+.2f}% "
                f"contre {taux_export:+.2f}% pour les exportations. "
                f"Cette hausse plus rapide des importations exerce une pression sur la balance commerciale "
                f"et peut indiquer une dépendance accrue vis-à-vis des produits étrangers."
            )
        else:
            st.info(
                f"ℹ️ En {annee}, les exportations et les importations ont progressé au même rythme "
                f"({taux_export:+.2f}%). Les échanges commerciaux sont équilibrés sans tendance marquée."
            )
    elif taux_export < 0 and taux_import < 0:
        st.error(
            f"🔴 En {annee}, les échanges commerciaux sont en recul. "
            f"Les exportations ont diminué de {taux_export:+.2f}% et les importations de {taux_import:+.2f}%. "
            f"Ce recul général peut refléter un ralentissement de l'activité économique ou une baisse de la demande."
        )
    elif taux_export < 0 and taux_import > 0:
        st.error(
            f"🔴 En {annee}, les exportations ont reculé de {taux_export:+.2f}% "
            f"tandis que les importations ont progressé de {taux_import:+.2f}%. "
            f"Cette combinaison défavorable détériore la balance commerciale "
            f"et traduit une perte de compétitivité sur les marchés extérieurs."
        )
    elif taux_export > 0 and taux_import < 0:
        st.success(
            f"✅ En {annee}, les exportations ont progressé de {taux_export:+.2f}% "
            f"tandis que les importations ont reculé de {taux_import:+.2f}%. "
            f"Cette situation favorable améliore significativement la balance commerciale "
            f"et témoigne d'une bonne performance du pays sur les marchés internationaux."
        )
else:
    st.info(
        f"ℹ️ Sélectionnez une année autre que la première disponible "
        f"pour analyser l'évolution des échanges commerciaux par rapport à l'année précédente."
    )



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

# Interprétation automatique de la balance commerciale
if balance > 0:
    st.success(f"En {annee}, la balance commerciale est excédentaire.")
elif balance < 0:
    st.error(f"En {annee}, la balance commerciale est déficitaire.")
else:
    st.info("La balance commerciale est équilibrée.")

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig3, use_container_width=True, key="graph3")
with col4:
    st.plotly_chart(fig4, use_container_width=True, key="graph4")

# Base de données
st.subheader("Données")
st.dataframe(df_f.reset_index(drop=True))



