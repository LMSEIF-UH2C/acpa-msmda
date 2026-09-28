import streamlit as st

from engine import recommend


st.set_page_config(
    page_title="ACPA/MSMDA PoC",
    page_icon="🏃",
    layout="centered",
)

st.title("ACPA/MSMDA")
st.caption(
    "Proof of Concept — Adapted Physical Education Recommendation System"
)

st.info(
    "Research prototype. The current rules and exercise catalogue are "
    "demonstration data and do not yet represent the complete patented "
    "ACPA/MSMDA knowledge base."
)

st.subheader("Profil pédagogique")

mobility = st.selectbox("Mobilité", ["standard", "reduced"])
balance_support = st.selectbox(
    "Besoin de soutien de l'équilibre",
    ["none", "moderate", "high"],
)
cardio_tolerance = st.selectbox(
    "Tolérance cardio",
    ["low", "moderate", "high"],
)
equipment = st.selectbox(
    "Matériel disponible",
    ["none", "ball", "band", "mixed"],
)
environment = st.selectbox(
    "Environnement",
    ["indoor", "outdoor"],
)
objective = st.selectbox(
    "Objectif pédagogique",
    ["general", "coordination", "endurance", "upper_body", "balance"],
)

profile = {
    "mobility": mobility,
    "balance_support": balance_support,
    "cardio_tolerance": cardio_tolerance,
    "equipment": equipment,
    "environment": environment,
    "objective": objective,
}

if st.button("Générer les recommandations", type="primary"):
    result = recommend(profile)

    st.divider()
    st.subheader("Règles activées")

    matched_rules = result["matched_rules"]

    if matched_rules:
        for rule in matched_rules:
            st.write(f"**{rule['id']} — {rule['label']}**")
            st.caption(rule["explanation"])
    else:
        st.write("Aucune règle d'adaptation spécifique activée.")

    st.divider()
    st.subheader("Recommandations")

    recommendations = result["recommendations"]

    if not recommendations:
        st.warning(
            "Aucune activité du catalogue de démonstration ne satisfait "
            "toutes les contraintes."
        )

    for index, activity in enumerate(recommendations, start=1):
        with st.container(border=True):
            st.markdown(f"### {index}. {activity['name']}")
            st.write(activity["description"])

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Score", activity["score"])

            with col2:
                st.metric("Intensité", activity["intensity"])

            st.write("**Pourquoi cette recommandation ?**")

            for reason in activity["reasons"]:
                st.write(f"- {reason}")

    with st.expander("Voir la politique d'adaptation calculée"):
        st.json(result["policy"])

st.divider()
st.caption(
    "ACPA/MSMDA research PoC — not a medical device and not intended "
    "for diagnosis or medical treatment."
)
