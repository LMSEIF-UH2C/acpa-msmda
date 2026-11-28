"""Optional, isolated experimental entry. No change to stable recommendation."""
import os

def enabled():
    return os.environ.get("ACPA_EXPERIMENTAL_ECOSYSTEM") == "1"

def label(lang):
    return {"fr":"Technothèque expérimentale","ar":"المكتبة التقنية التجريبية","en":"Experimental technology library"}.get(lang,"Technothèque expérimentale")

def render():
    import streamlit as st
    from . import i18n
    from .ui import HOME, configure_page
    from .experimental_registry import read_preview
    configure_page(HOME)
    lang=i18n.current()
    def msg(fr,ar,en):
        return {"fr":fr,"ar":ar,"en":en}.get(lang,fr)
    st.title(label(lang))
    st.warning(msg("Parcours expérimental : pistes non qualifiées, aucune nouvelle recommandation validée.",
                   "مسار تجريبي: موارد غير مقيمة، لا توصيات جديدة معتمدة.",
                   "Experimental path: unassessed leads, no new validated recommendations."))
    if not enabled():
        st.stop()
    path=os.environ.get("ACPA_EXPERIMENTAL_DB")
    if not path:
        st.info(msg("Registre expérimental non configuré.","السجل التجريبي غير مهيأ.","Experimental register not configured."))
        return
    try:
        result=read_preview(path)
    except (OSError,ValueError,RuntimeError, __import__("sqlite3").Error):
        st.info(msg("Registre expérimental indisponible. Le parcours stable reste accessible.",
                    "السجل التجريبي غير متاح. المسار المستقر متاح.",
                    "Experimental register unavailable. The stable path remains accessible."))
        return
    st.caption(msg("Enregistrements de source, pas de produits uniques.","سجلات المصادر وليست منتجات فريدة.","Source records, not unique products."))
    st.metric(msg("Pistes documentaires","موارد موثقة أولياً","Documentary leads"),result["documentary_leads"])
    st.metric(msg("Observations","الملاحظات","Observations"),result["observations"])
    for row in result["leads"]:
        with st.expander(row["name"]):
            st.text(row["kind"]+" · "+row["category"]+" · "+row["date"])
            st.link_button(msg("Source","المصدر","Source"),row["url"])
            st.caption(msg("Pertinence, contraintes et identité à vérifier.","الملاءمة والقيود والهوية تحتاج إلى تحقق.","Relevance, constraints and identity require review."))
            proposal=row.get("qualification_proposal")
            if proposal:
                st.caption(msg("Proposition documentaire — non évaluée indépendamment",
                               "اقتراح وثائقي — غير مقيم بشكل مستقل",
                               "Documentary proposal — not independently assessed"))
                role_labels={
                    "DIRECT":msg("Usage direct envisagé","استخدام مباشر مقترح","Proposed direct use"),
                    "COMPLEMENTAIRE":msg("Usage complémentaire envisagé","استخدام تكميلي مقترح","Proposed complementary use"),
                    "NON_PERTINENT":msg("Non pertinent proposé","عدم ملاءمة مقترح","Proposed not relevant"),
                    "INCERTAIN":msg("Usage incertain","استخدام غير مؤكد","Uncertain use")}
                st.text(role_labels[proposal["proposed_role"]])
                st.caption(msg("Documentation originale en français","التوثيق الأصلي بالفرنسية","Original documentation in French"))
                st.text(proposal["documented_function"])
                st.text(proposal["variant"])
                st.caption(msg("Preuve documentaire : déclaration éditeur rapportée, scénario non testé.",
                               "دليل وثائقي: تصريح الناشر المنقول، سيناريو غير مختبر.",
                               "Documentary evidence: reported publisher declaration, untested scenario."))
                st.text(proposal["scenario"])
                st.text(proposal["documented_limits"])
                st.caption(msg("Toutes les contraintes contextuelles restent à vérifier. Aucun score attribué.",
                               "جميع القيود السياقية تحتاج إلى تحقق. لم يتم إسناد أي درجة.",
                               "All contextual constraints require verification. No score assigned."))
