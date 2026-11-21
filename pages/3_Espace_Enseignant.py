"""Espace enseignant EPS : préparation de séance sans données d'élèves."""
from __future__ import annotations

import csv
import io
from datetime import date

import streamlit as st

st.set_page_config(page_title="ACPA/MSMDA | Espace enseignant",page_icon="📋",layout="wide")
st.title("Espace enseignant — Planifier une séance EPS")
st.caption("Prototype opérationnel de planification ; recommandations organisationnelles explicites, non issues d'un modèle validé.")
st.info("Ne renseignez pas de noms d'élèves. Ce formulaire n'enregistre pas les données de manière durable.")
with st.form("session_plan"):
    a,b=st.columns(2)
    with a:
        aps=st.selectbox("Activité physique et sportive",["Endurance","Athlétisme","Gymnastique","Basketball","Football","Volleyball","Badminton","Autre"])
        niveau=st.selectbox("Niveau",["Primaire","Collège","Lycée","Supérieur"])
        effectif=st.number_input("Effectif",min_value=1,max_value=60,value=35)
        duree=st.number_input("Durée de séance (minutes)",min_value=20,max_value=180,value=55,step=5)
    with b:
        espace=st.selectbox("Espace disponible",["Terrain extérieur","Gymnase","Piste","Salle polyvalente","Autre"])
        materiel=st.text_input("Matériel disponible (sans informations personnelles)",value="Plots, chronomètre")
        connexion=st.selectbox("Connectivité",["Aucune","Instable","Stable"])
        appareils=st.selectbox("Appareils disponibles",["Aucun","Téléphone enseignant","Téléphones partagés","Téléphones individuels"])
    objectif=st.text_area("Objectif d'apprentissage",value="Améliorer la participation motrice et suivre les progrès.",max_chars=500)
    n_ateliers=st.slider("Nombre d'ateliers",min_value=1,max_value=8,value=4)
    submitted=st.form_submit_button("Construire la séance",type="primary")
if submitted:
    accueil=max(3,round(duree*.10))
    bilan=max(4,round(duree*.10))
    retour=max(3,round(duree*.10))
    pratique=duree-accueil-bilan-retour
    groupes=[effectif//n_ateliers+(1 if i<effectif%n_ateliers else 0) for i in range(n_ateliers)]
    temps_rotation=pratique/n_ateliers
    phases=[
        ("Accueil et consignes",accueil),
        ("Ateliers et rotations",pratique),
        ("Retour au calme",retour),
        ("Bilan et traces",bilan),
    ]
    st.session_state["eps_plan"]={"aps":aps,"niveau":niveau,"effectif":effectif,"duree":duree,"espace":espace,"materiel":materiel,"connexion":connexion,"appareils":appareils,"objectif":objectif,"ateliers":n_ateliers,"groupes":groupes,"rotation":temps_rotation,"phases":phases}
plan=st.session_state.get("eps_plan")
if plan:
    st.subheader("Plan proposé")
    st.write(f"**{plan['aps']}** · {plan['niveau']} · {plan['effectif']} élèves · {plan['duree']} min")
    st.write("**Objectif :** "+plan["objectif"])
    st.dataframe([{"Phase":name,"Durée (min)":minutes} for name,minutes in plan["phases"]],hide_index=True,use_container_width=True)
    st.write("**Répartition indicative des groupes :** "+", ".join(str(n) for n in plan["groupes"])+" élèves")
    st.write(f"**Temps brut par atelier :** {plan['rotation']:.1f} min, transitions comprises ; à ajuster selon le terrain.")
    if plan["connexion"]!="Stable":
        st.warning("Connexion limitée : privilégier chronomètres, supports téléchargés et saisie locale seulement si l'outil garantit réellement sa conservation.")
    if plan["appareils"]=="Aucun":
        st.info("Aucun smartphone nécessaire : privilégier des consignes imprimées, des ateliers autonomes et l'observation directe.")
    elif plan["aps"]=="Endurance":
        st.info("Technologies à examiner : chronomètre et suivi d'activité ; vérifier confidentialité, âge des élèves et accès réel aux appareils avant de choisir.")
    elif plan["aps"]=="Gymnastique":
        st.info("Technologies à examiner : analyse vidéo et parcours de ressources ; demander l'autorisation nécessaire avant tout enregistrement d'élèves.")
    else:
        st.info("Comparer les outils de mesure, d'observation et d'organisation avec le moteur ACPA/MSMDA ; aucun score réel n'est calculé ici.")
    output=io.StringIO()
    writer=csv.writer(output)
    writer.writerow(["APS","Niveau","Effectif","Durée","Objectif","Phase","Minutes"])
    for name,minutes in plan["phases"]:
        writer.writerow([plan["aps"],plan["niveau"],plan["effectif"],plan["duree"],plan["objectif"],name,minutes])
    st.download_button("Exporter le plan (CSV)",output.getvalue().encode("utf-8-sig"),file_name="acpa_plan_seance.csv",mime="text/csv")
    st.caption("Proposition calculée selon une répartition indicative du temps, à adapter par l'enseignant ; ne constitue pas une optimisation scientifiquement démontrée.")
