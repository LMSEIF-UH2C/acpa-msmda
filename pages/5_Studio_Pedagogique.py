"""Studio pédagogique : scénario de séance, supports et export."""
from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from acpa_msmda.scenario_engine import PHASES,recommend_phase_tools,validate_scenario,export_scenario_csv

st.set_page_config(page_title="ACPA/MSMDA | Studio pédagogique",page_icon="📚",layout="wide")
st.title("Studio pédagogique")
st.caption("Concevez vos séances et choisissez les supports adaptés à chaque phase.")
st.warning("Ne renseignez aucune donnée personnelle d'élève.")
a,b,c=st.columns(3)
with a:
    activity=st.text_input("Activité physique ou sportive",value="Endurance",max_chars=100)
    level=st.selectbox("Niveau",["Primaire","Collège","Lycée","Supérieur","Formation d'enseignants"])
with b:
    modality=st.selectbox("Modalité",["Présentiel","Hybride","À distance","Classe inversée","Autonomie accompagnée"])
    duration=int(st.number_input("Durée totale (minutes)",min_value=15,max_value=240,value=60,step=5))
with c:
    class_size=int(st.number_input("Effectif",min_value=1,max_value=150,value=30))
    connectivity=st.selectbox("Connectivité",["Aucune","Limitée","Disponible"])
objectives=st.text_area("Compétences et objectifs",value="Gérer son allure et analyser sa performance.",max_chars=800)
prerequisites=st.text_input("Prérequis",value="Connaître les consignes de sécurité",max_chars=300)
constraints=st.text_input("Matériel et contraintes",value="Terrain, chronomètre, un smartphone enseignant",max_chars=400)
st.subheader("Scénario de séance")
st.caption("Adaptez les activités, supports, critères de réussite et durées.")
phase_names=["Diagnostic","Mise en activité","Apprentissage","Régulation","Évaluation"]
defaults=[5,10,30,10,5]
rows=[]
for i,(phase,default) in enumerate(zip(phase_names,defaults)):
    with st.expander(f"{i+1}. {phase}",expanded=i==2):
        col1,col2=st.columns([3,1])
        with col1:
            action=st.text_area("Activité, consignes et rôle des élèves",key=f"action_{i}",max_chars=600)
            supports=st.multiselect("Supports multimédias",["Vidéo","Audio","Quiz","QR code","Fiche numérique","Démonstration","Capteurs","Analyse vidéo"],key=f"supports_{i}")
            evaluation=st.text_input("Critères de réussite et feedback",key=f"evaluation_{i}",max_chars=300)
        with col2:
            minutes=int(st.number_input("Durée (min)",min_value=0,max_value=240,value=default,key=f"minutes_{i}"))
        rows.append({"Phase":phase,"Durée (min)":minutes,"Activité / consignes":action,"Supports":", ".join(supports),"Évaluation / feedback":evaluation})
        st.markdown("**Technologies à explorer pour cette phase**")
        suggestions=recommend_phase_tools(phase,connectivity=connectivity,limit=5)
        if suggestions:
            for tool in suggestions:
                label=tool["name"]+" · "+tool["category"]
                if not tool["documented"]:label+=" · à confirmer"
                st.markdown(f"- [{label}]({tool['source_url']})")
                if tool["notes"]:st.caption(" ; ".join(tool["notes"]))
        else:
            st.caption("Aucune proposition avec les informations disponibles. Un support non numérique peut convenir.")
validation=validate_scenario(rows,duration)
if validation["balanced"]:
    st.success(f"Durée totale respectée : {duration} min.")
else:
    st.warning(f"Durée des phases : {validation['used_minutes']} min sur {duration} min. Écart : {validation['difference_minutes']:+d} min.")
metadata={"APS":activity,"Niveau":level,"Modalité":modality,"Effectif":class_size,"Connectivité":connectivity,"Objectifs":objectives,"Prérequis":prerequisites,"Contraintes":constraints}
st.download_button("Exporter mon scénario (CSV)",export_scenario_csv(metadata,rows),"scenario_pedagogique_eps.csv","text/csv")
