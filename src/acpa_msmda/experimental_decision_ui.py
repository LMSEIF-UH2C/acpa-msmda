"""A5 experimental decision UI, separate real diagnostics and fictional simulation."""
from .experimental_ecosystem import GATES, inspect_documentary_register, solve_fixture

FUNCTION_LABELS = {
 "F01":("Planifier","التخطيط","Plan"),
 "F02":("Organiser","التنظيم","Organize"),
 "F03":("Diagnostiquer","التشخيص","Diagnose"),
 "F04":("Expliquer et démontrer","الشرح والعرض","Explain and demonstrate"),
 "F05":("Favoriser la pratique","تعزيز الممارسة","Support practice"),
 "F06":("Observer et mesurer","الملاحظة والقياس","Observe and measure"),
 "F07":("Réguler et donner du feedback","التقويم والتغذية الراجعة","Regulate and give feedback"),
 "F08":("Arbitrer et coopérer","التحكيم والتعاون","Officiate and cooperate"),
 "F09":("Différencier et inclure","التمايز والإدماج","Differentiate and include"),
 "F10":("Évaluer et suivre","التقييم والتتبع","Assess and track"),
 "F11":("Communiquer et assurer la continuité","التواصل والاستمرارية","Communicate and maintain continuity"),
 "F12":("Développer les connaissances","تنمية المعارف","Develop knowledge"),
 "F13":("Sécurité et confidentialité","السلامة والخصوصية","Safety and privacy"),
 "F14":("Analyser la pratique enseignante","تحليل الممارسة التدريسية","Analyze teaching practice"),
 "F15":("Organiser le sport scolaire","تنظيم الرياضة المدرسية","Organize school sport"),
}

def decision_context(required, optional, budget, devices, offline, unsupported):
    """Explicit session context; no inference from activity name."""
    return {"required":list(required),"optional":list(optional),"budget_mad":budget,
            "period":"session","devices":devices,"offline":offline,
            "unsupported_requirements":["UNMODELLED"] if unsupported else []}

def demonstration_context():
    return decision_context(["F04","F06","F07"],["F05"],0,1,True,False)

def demonstration_pool():
    def fixture(i, functions, phase):
        return {"id":i,"product":i,"mode":"TEST_FIXTURE","review":"FIXTURE_APPROVED",
                "gates":dict.fromkeys(GATES,"COMPATIBLE"),"offline":True,"cost":0,
                "period":"session","currency":"MAD","load":1,"device_slots":{phase:1},
                "functions":functions,"requires":[],"incompatible":[]}
    return [fixture("A",["F04"],"before"),fixture("B",["F06"],"during"),
            fixture("C",["F07"],"after")]

def render_decision(path, lang):
    import streamlit as st
    from sqlite3 import Error as SQLiteError
    def msg(fr, ar, en):
        return {"fr":fr,"ar":ar,"en":en}.get(lang,fr)
    def fn(code):
        return msg(*FUNCTION_LABELS[code])
    st.subheader(msg("Composer un écosystème pédagogique","تركيب منظومة تربوية","Build a pedagogical ecosystem"))
    with st.expander(msg("Diagnostic documentaire réel","التشخيص الوثائقي الحقيقي","Real documentary diagnosis")):
        st.caption(msg("Besoins et contraintes de la séance. Les fonctions proposées ne sont pas encore validées pour chaque technologie.",
                       "حاجات وقيود الحصة. لم يتم التحقق بعد من الوظائف المقترحة لكل تقنية.",
                       "Session needs and constraints. Proposed functions are not yet validated for each technology."))
        with st.form("a5_real_context"):
            required=st.multiselect(msg("Besoins obligatoires","الحاجات الإلزامية","Required needs"),list(FUNCTION_LABELS),default=["F04","F06"],format_func=fn)
            optional=st.multiselect(msg("Besoins facultatifs","الحاجات الاختيارية","Optional needs"),list(FUNCTION_LABELS),default=[],format_func=fn)
            budget=st.number_input(msg("Budget par séance (DH)","ميزانية الحصة (درهم)","Budget per session (MAD)"),min_value=0,max_value=100000,value=0,step=1)
            devices=st.number_input(msg("Appareils disponibles simultanément","الأجهزة المتاحة في الوقت نفسه","Simultaneously available devices"),min_value=0,max_value=100,value=1,step=1)
            offline=st.checkbox(msg("Sans Internet","دون إنترنت","No Internet"),value=True)
            unsupported=st.checkbox(msg("Autre contrainte non modélisée","قيد آخر غير ممثل","Other unmodelled constraint"))
            submitted=st.form_submit_button(msg("Analyser les preuves","تحليل الأدلة","Analyze evidence"))
        if submitted:
            if not required or set(required)&set(optional):
                st.error(msg("Choisissez au moins un besoin obligatoire, sans doublon facultatif.",
                             "اختر حاجة إلزامية واحدة على الأقل دون تكرار اختياري.",
                             "Choose at least one required need without optional overlap."))
            else:
                try:
                    result=inspect_documentary_register(path,decision_context(required,optional,int(budget),int(devices),offline,unsupported))
                except (OSError,ValueError,RuntimeError,SQLiteError,KeyError,TypeError):
                    st.error(msg("Analyse indisponible : preuves non vérifiables.","التحليل غير متاح: الأدلة غير قابلة للتحقق.","Analysis unavailable: evidence cannot be verified."))
                else:
                    st.warning(msg("Aucune recommandation opérationnelle","لا توجد توصية تشغيلية","No operational recommendation"))
                    st.write(msg("Propositions reliées aux observations","الاقتراحات المرتبطة بالملاحظات","Proposals linked to observations")+f" : {result['linked_proposals']}/{result['records']}")
                    st.write(msg("Technologies admissibles","التقنيات المقبولة","Admissible technologies")+f" : {result['admitted']}")
                    st.caption(msg("Couverture non évaluée : preuves contextuelles, identité et correspondances fonctionnelles à établir.",
                                   "لم يتم تقييم التغطية: يجب إثبات الأدلة السياقية والهوية وتطابق الوظائف.",
                                   "Coverage not assessed: contextual evidence, identity and function mapping remain to be established."))
                    st.write(msg("Besoins restant à documenter","الحاجات التي تتطلب توثيقا","Needs still to document")+": "+", ".join(fn(x) for x in result["required"]))
                    if unsupported:
                        st.info(msg("Contrainte non modélisée : aucune sélection possible.","قيد غير ممثل: لا يمكن الاختيار.","Unmodelled constraint: no selection possible."))
    with st.expander(msg("Simulation fictive — relais","محاكاة افتراضية — التتابع","Fictional simulation — relay")):
        st.warning(msg("Exemple fictif uniquement, aucun outil réel ni conseil d'achat.",
                       "مثال افتراضي فقط، لا أدوات حقيقية أو نصائح شراء.",
                       "Fictional example only, no real tools or purchase advice."))
        st.caption(msg("Trois besoins obligatoires, un appareil, sans Internet, budget fictif 0 DH.",
                       "ثلاث حاجات إلزامية، جهاز واحد، دون إنترنت، ميزانية افتراضية صفر درهم.",
                       "Three required needs, one device, no Internet, fictional budget MAD 0."))
        if st.button(msg("Lancer la simulation","تشغيل المحاكاة","Run simulation"),key="a5_demo"):
            context=demonstration_context()
            result=solve_fixture(context,demonstration_pool())
            if result["status"]!="COMPLETE_FIXTURE_SET":
                st.error(msg("Simulation sans solution complète.","المحاكاة دون حل كامل.","Simulation has no complete solution."))
                return
            st.success(msg("Configuration fictive complète","منظومة افتراضية كاملة","Complete fictional configuration"))
            for key,title in (("best_individual",msg("Outil unique","أداة واحدة","Single tool")),
                              ("simple_pair",msg("Deux outils maximum","أداتان على الأكثر","Up to two tools")),
                              ("selected",msg("Écosystème fictif","منظومة افتراضية","Fictional ecosystem"))):
                value=result[key]
                st.write(f"{title} : {len(value['covered_required'])}/{len(context['required'])}")
            for tool, roles in result["selected"]["roles"].items():
                st.write(msg("Outil fictif","أداة افتراضية","Fictional tool")+" "+tool+" : "+", ".join(fn(x) for x in roles))
            st.caption(msg("Résultat algorithmique, pas une preuve d'efficacité pédagogique.",
                           "نتيجة خوارزمية وليست دليلا على الفعالية التربوية.",
                           "Algorithmic result, not evidence of pedagogical effectiveness."))
