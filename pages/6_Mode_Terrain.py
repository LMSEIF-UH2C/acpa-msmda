"""Mode terrain : outils de séance, état temporaire."""
import sys
import time
from pathlib import Path
import streamlit as st
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.field_tools import Timer, change_count, rotation_assignments
from acpa_msmda.i18n import t
from acpa_msmda.ui import FIELD, configure_page, page_header, PRIVACY_NOTE

S = st.session_state
configure_page(FIELD)
page_header(FIELD, PRIVACY_NOTE)
st.caption(t("Ces outils nécessitent une connexion à l’application hébergée. Gardez un chronomètre autonome en secours."))
data = ctx.store(S)
mode = st.radio(t("Outil de terrain"), ["Chronomètre", "Compteurs", "Scores", "Rotations"], format_func=t, horizontal=True)
if mode == "Chronomètre":
    minutes = st.number_input(t("Durée (min)"), min_value=1, max_value=120, value=5)
    if "field_timer" not in data or st.button(t("Régler le chronomètre")):
        data["field_timer"] = Timer.new(int(minutes)*60)
    @st.fragment(run_every=1)
    def clock():
        timer = data["field_timer"]
        now = time.monotonic()
        left = timer.seconds_left(now)
        st.metric(t("Temps restant"), f"{left//60:02d}:{left%60:02d}")
        a,b,c = st.columns(3)
        if a.button(t("Démarrer"), disabled=timer.started is not None or left==0):
            data["field_timer"] = timer.start(time.monotonic())
            st.rerun(scope="fragment")
        if b.button(t("Pause"), disabled=timer.started is None):
            data["field_timer"] = timer.pause(time.monotonic())
            st.rerun(scope="fragment")
        if c.button(t("Réinitialiser")):
            data["field_timer"] = Timer.new(timer.duration)
            st.rerun(scope="fragment")
        if left == 0:
            st.success(t("Temps écoulé"))
    clock()
elif mode in ("Compteurs", "Scores"):
    labels = ("Tentatives", "Réussites") if mode == "Compteurs" else ("Équipe A", "Équipe B")
    prefix = "count" if mode == "Compteurs" else "score"
    for i,(col,label) in enumerate(zip(st.columns(2),labels)):
        key = f"field_{prefix}_{i}"
        with col:
            st.metric(t(label), data.get(key,0))
            a,b=st.columns(2)
            if a.button("+1",key=key+"plus"):
                data[key]=change_count(data.get(key,0),1)
                st.rerun()
            if b.button("−1",key=key+"minus"):
                data[key]=change_count(data.get(key,0),-1)
                st.rerun()
    if st.button(t("Réinitialiser")):
        for i in range(2):
            data[f"field_{prefix}_{i}"]=0
        st.rerun()
else:
    count=st.number_input(t("Nombre d'ateliers"),min_value=1,max_value=8,value=int(ctx.get(S,"workshops") or 4))
    if data.get("field_rotation_count") != count:
        data["field_rotation_count"]=count
        data["field_rotation_step"]=0
    step=data.get("field_rotation_step",0)
    st.write(t("Rotation {n}",n=step+1))
    for i,station in enumerate(rotation_assignments(int(count),step),1):
        st.write(t("Groupe {g} : atelier {a}",g=i,a=station))
    if st.button(t("Rotation suivante"),disabled=step>=count-1):
        data["field_rotation_step"]=step+1
        st.rerun()
    if st.button(t("Réinitialiser")):
        data["field_rotation_step"]=0
        st.rerun()
