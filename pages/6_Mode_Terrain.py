"""Mode terrain : outils de séance, état temporaire."""
import sys
import time
from pathlib import Path
import streamlit as st
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from acpa_msmda import session_context as ctx
from acpa_msmda.field_tools import Timer, change_count, rotation_assignments, observation_change, next_rotation
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
    configure_timer = st.button(t("Régler le chronomètre"))
    if "field_timer" not in data or configure_timer:
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
            st.rerun()
        if b.button(t("Pause"), disabled=timer.started is None):
            data["field_timer"] = timer.pause(time.monotonic())
            st.rerun()
        if c.button(t("Réinitialiser")):
            data["field_timer"] = Timer.new(timer.duration)
            st.rerun()
        if left == 0:
            st.success(t("Temps écoulé"))
    clock()
elif mode in ("Compteurs", "Scores"):
    labels = ("Tentatives", "Réussites") if mode == "Compteurs" else ("Équipe A", "Équipe B")
    prefix = "count" if mode == "Compteurs" else "score"
    def adjust(i, delta):
        if mode == "Compteurs":
            a, b = observation_change(data.get("field_count_0", 0), data.get("field_count_1", 0), i, delta)
            data["field_count_0"], data["field_count_1"] = a, b
        else:
            key = f"field_score_{i}"
            data[key] = change_count(data.get(key, 0), delta)
    for i,(col,label) in enumerate(zip(st.columns(2),labels)):
        key = f"field_{prefix}_{i}"
        with col:
            st.metric(t(label), data.get(key,0))
            a,b=st.columns(2)
            if a.button("+1",key=key+"plus"):
                adjust(i, 1)
                st.rerun()
            if b.button("−1",key=key+"minus"):
                adjust(i, -1)
                st.rerun()
    if mode == "Compteurs":
        attempts, successes = data.get("field_count_0",0), data.get("field_count_1",0)
        if attempts:
            st.metric(t("Taux de réussite"), f"{100*successes/attempts:.1f} %")
            st.caption(f"{successes} / {attempts}")
        else:
            st.caption(t("Aucune tentative enregistrée."))
    if st.button(t("Réinitialiser")):
        for i in range(2):
            data[f"field_{prefix}_{i}"]=0
        st.rerun()
else:
    count=st.number_input(t("Nombre d'ateliers"),min_value=1,max_value=8,value=int(ctx.get(S,"workshops") or 4))
    interval = st.number_input(t("Durée par atelier (min)"), min_value=1,max_value=120,value=5)
    settings = (int(count), int(interval))
    reset = st.button(t("Régler les rotations"))
    if data.get("field_rotation_settings") != settings or reset:
        data["field_rotation_settings"] = settings
        data["field_rotation_step"] = 0
        data["field_rotation_timer"] = Timer.new(int(interval)*60)
    @st.fragment(run_every=1)
    def rotation_clock():
        step = data["field_rotation_step"]
        timer = data["field_rotation_timer"]
        now = time.monotonic()
        left = timer.seconds_left(now)
        st.write(t("Rotation {n}",n=step+1))
        for i,station in enumerate(rotation_assignments(int(count),step),1):
            st.write(t("Groupe {g} : atelier {a}",g=i,a=station))
        st.metric(t("Temps restant"), f"{left//60:02d}:{left%60:02d}")
        a,b = st.columns(2)
        if a.button(t("Démarrer"),key="rotation_start",disabled=timer.started is not None or left==0):
            data["field_rotation_timer"] = timer.start(time.monotonic())
            st.rerun()
        if b.button(t("Pause"),key="rotation_pause",disabled=timer.started is None or left==0):
            data["field_rotation_timer"] = timer.pause(time.monotonic())
            st.rerun()
        if left == 0:
            st.success(t("Temps écoulé"))
        if st.button(t("Rotation suivante"),disabled=step>=count-1 or left>0):
            data["field_rotation_step"], data["field_rotation_timer"] = next_rotation(step,int(count),timer,time.monotonic())
            st.rerun()
    rotation_clock()
