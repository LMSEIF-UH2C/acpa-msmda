"""Studio pédagogique : conception de scénarios EPS et ressources multimédias."""
from __future__ import annotations
import csv
import io
import sys
from pathlib import Path
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.real_catalog import load_real_tools

st.set_page_config(page_title="ACPA/MSMDA | Studio pédagogique",page_icon="📚",layout="wide")
st.title("Studio pédagogique")
st.caption("Construisez votre scénario de séance et repérez les ressources adaptées à chaque phase.")
st.info("Modèle de travail modifiable par l'enseignant : les propositions ne remplacent pas les choix pédagogiques.")
st.warning("N'indiquez pas de noms ni d'informations personnelles d'élèves.")

c1,c2,c3=st.columns(3)
with c1:
    activity=st.text_input("Activité physique ou sportive",value="Endurance",max_chars=100)
    level=st.selectbox("Niveau",["Primaire","Collège","Lycée","Supérieur","Formation d'enseignants"])
with c2:
    modality=st.selectbox("Modalité",["Présentiel","Hybride","À distance","Classe inversée","Autonomie accompagnée"])
    duration=st.number_input("Durée totale (minutes)",min_value=15,max_value=240,value=60,step=5)
with c3:
    class_size=st.number_input("Effectif",min_value=1,max_value=150,value=30)
    connectivity=st.selectbox("Connectivité",["Aucune","Limitée","Disponible"])
objectives=st.text_area("Compétences et objectifs visés",value="Gérer son allure et interpréter les informations de sa performance.",max_chars=800)
prerequisites=st.text_input("Prérequis",value="Connaître les consignes de sécurité",max_chars=300)
constraints=st.text_input("Matériel et contraintes",value="Terrain, chronomètre, un smartphone enseignant",max_chars=400)
st.subheader("Déroulement du scénario")
st.caption("Modifiez les phases, leurs durées et les modalités de travail. La durée totale est contrôlée.")
phases=["Accueil et diagnostic","Mise en activité","Situation d'apprentissage","Feedback et régulation","Bilan et évaluation"]
defaults=[5,10,30,10,5]
rows=[]
for i,(phase,default) in enumerate(zip(phases,defaults)):
    with st.expander(f"{i+1}. {phase}",expanded=i==2):
        a,b=st.columns([3,1])
        with a:
            action=st.text_input("Activité et consignes",value="",key=f"act_{i}",max_chars=600,placeholder="Décrire ce que font l'enseignant et les élèves")
            media=st.multiselect("Supports possibles",["Aucun","Vidéo","Fiche numérique","Quiz","QR code","Audio","Démonstration","Capteurs","Analyse vidéo"],default=["Aucun"],key=f"media_{i}")
            assessment=st.text_input("Critères de réussite / feedback",value="",key=f"assess_{i}",max_chars=300)
        with b:
            minutes=st.number_input("Minutes",min_value=0,max_value=240,value=default,key=f"mins_{i}")
        rows.append({"Phase":phase,"Durée (min)":minutes,"Activité / consignes":action,"Supports":", ".join(media),"Évaluation / feedback":assessment})
used=sum(r["Durée (min)"] for r in rows)
if used!=duration:
    st.warning(f"Durée prévue : {used} min pour {duration} min disponibles. Ajustez les phases ({used-duration:+d} min).")
else:
    st.success(f"Scénario équilibré sur {duration} minutes.")
st.subheader("Ressources technologiques à explorer")
catalogue=load_real_tools()
categories=sorted({t["category"] for t in catalogue})
chosen=st.multiselect("Familles d'outils",categories,default=[c for c in categories if c in ("Ressources et apprentissage","Analyse vidéo et mouvement")])
suggestions=[t for t in catalogue if t["category"] in chosen]
st.dataframe([{"Outil":t["name"],"Catégorie":t["category"],"Site éditeur":t.get("source_url") or "À compléter"} for t in suggestions],hide_index=True,use_container_width=True)
st.caption("Ces outils sont proposés par famille d'usage, sans présumer de leur adéquation, de leur prix ou de leur conformité.")
output=io.StringIO()
writer=csv.writer(output)
writer.writerow(["APS",activity,"Niveau",level,"Modalité",modality,"Effectif",class_size])
writer.writerow(["Objectifs",objectives])
writer.writerow(["Prérequis",prerequisites])
writer.writerow(["Contraintes",constraints,"Connectivité",connectivity])
writer.writerow(list(rows[0].keys()))
for row in rows:writer.writerow(list(row.values()))
st.download_button("Exporter le scénario (CSV)",data=output.getvalue().encode("utf-8-sig"),file_name="scenario_pedagogique_eps.csv",mime="text/csv")
