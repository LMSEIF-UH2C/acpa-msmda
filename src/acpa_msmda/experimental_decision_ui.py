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


def render_internal_review(path, lang, leads):
    """Separate restricted view; disabled in all existing deployments by default."""
    import os
    import streamlit as st
    from sqlite3 import Error as SQLiteError
    from .experimental_real_admission import load_operator_review_config, evaluate_operator_review
    if os.environ.get("ACPA_EXPERIMENTAL_INTERNAL_REVIEW")!="1":
        return
    def msg(fr,ar,en):
        return {"fr":fr,"ar":ar,"en":en}.get(lang,fr)
    def fn(code):
        return msg(*FUNCTION_LABELS[code])
    with st.expander(msg("Configuration réelle — revue interne","منظومة حقيقية — مراجعة داخلية","Real configuration — internal review")):
        st.warning(msg("Usage interne uniquement. Ne constitue pas une validation scientifique externe.",
                       "للاستخدام الداخلي فقط. لا يمثل مصادقة علمية خارجية.",
                       "Internal use only. Not external scientific validation."))
        try:
            config=load_operator_review_config()
        except (OSError,ValueError,TypeError,KeyError):
            st.warning(msg("Configuration interne absente ou non vérifiable.","التهيئة الداخلية غائبة أو غير قابلة للتحقق.","Internal configuration missing or unverifiable."))
            return
        if config is None:
            return
        scenario=config["scenario"]; context=config["context"]
        for k,title in (("id",msg("Scénario","السيناريو","Scenario")),("platform",msg("Plateforme","المنصة","Platform")),
                        ("setting",msg("Cadre","السياق","Setting")),("data_policy",msg("Politique de données","سياسة البيانات","Data policy"))):
            st.text(title+": "+scenario[k])
        st.text(msg("Besoins obligatoires","الحاجات الإلزامية","Required needs")+": "+", ".join(fn(x) for x in context["required"]))
        st.text(msg("Besoins facultatifs","الحاجات الاختيارية","Optional needs")+": "+(", ".join(fn(x) for x in context["optional"]) or "—"))
        st.text(msg("Budget (DH) / période","الميزانية (درهم) / الفترة","Budget (MAD) / period")+f": {context['budget_mad']} / {context['period']}")
        st.text(msg("Appareils simultanés","الأجهزة المتزامنة","Simultaneous devices")+f": {context['devices']}")
        st.text(msg("Hors ligne exigé","العمل دون إنترنت مطلوب","Offline required")+": "+(msg("Oui","نعم","Yes") if context["offline"] else msg("Non","لا","No")))
        if context["unsupported_requirements"]:
            st.text(msg("Exigences non modélisées","متطلبات غير ممثلة","Unmodelled requirements")+": "+", ".join(context["unsupported_requirements"]))
        confirmed=st.checkbox(msg("Ce contexte correspond à la situation examinée","هذا السياق يطابق الحالة المدروسة","This context matches the situation under review"),key="a5_internal_context")
        if not st.button(msg("Évaluer la configuration interne","تقييم المنظومة الداخلية","Evaluate internal configuration"),key="a5_internal_evaluate",disabled=not confirmed):
            return
        try:
            result=evaluate_operator_review(path,config)
        except (OSError,ValueError,RuntimeError,SQLiteError,KeyError,TypeError):
            st.warning(msg("Abstention : dossier interne non vérifiable.","امتناع: الملف الداخلي غير قابل للتحقق.","Abstention: internal dossier unverifiable."))
            return
        st.write(msg("Technologies admises en interne","تقنيات مقبولة داخليا","Internally admitted technologies")+f" : {result['admitted']}")
        selected=result["selected"]
        if result["status"]!="COMPLETE_INTERNAL_CONFIGURATION" or selected is None:
            st.warning(msg("Abstention : aucune configuration complète admise.","امتناع: لا توجد منظومة كاملة مقبولة.","Abstention: no complete admitted configuration."))
            labels={
                "NO_APPROVED_MANIFEST":msg("Dossier approuvé absent","الملف المعتمد غائب","No approved dossier"),
                "APPROVED_DIGEST_MISMATCH":msg("Empreinte du dossier incorrecte","بصمة الملف غير مطابقة","Dossier digest mismatch"),
                "NO_ADMISSIBLE_REAL_CANDIDATE":msg("Aucun candidat admissible","لا يوجد مرشح مقبول","No admissible candidate"),
                "NO_COMPLETE_SET":msg("Couverture obligatoire incomplète","التغطية الإلزامية غير مكتملة","Required coverage incomplete"),
                "UNSUPPORTED_REQUIREMENT":msg("Exigence non modélisée","متطلب غير ممثل","Unmodelled requirement"),
                "INCOMPLETE_SEARCH":msg("Recherche incomplète","بحث غير مكتمل","Incomplete search"),
            }
            st.caption(labels.get(result["status"],msg("Décision non concluante","قرار غير حاسم","Inconclusive decision")))
            return
        st.success(msg("Configuration admise pour ce contexte interne","منظومة مقبولة لهذا السياق الداخلي","Configuration admitted for this internal context"))
        names={r["id"]:r["name"] for r in leads}
        for key in selected["ids"]:
            st.text(names.get(key,key)+" ["+key+"] : "+", ".join(fn(x) for x in selected["roles"][key]))
        st.text(msg("Couverture obligatoire","التغطية الإلزامية","Required coverage")+f" : {len(selected['covered_required'])}/{len(context['required'])}")
        st.text(msg("Couverture facultative","التغطية الاختيارية","Optional coverage")+f" : {len(selected['covered_optional'])}/{len(context['optional'])}")
        st.text(msg("Coût total documenté (DH)","الكلفة الإجمالية الموثقة (درهم)","Documented total cost (MAD)")+f" : {selected['cost_mad']}")
        st.caption(msg("Validité limitée au dossier, aux variantes et au contexte approuvés. Aucun effet pédagogique démontré.",
                       "الصلاحية محصورة في الملف والنسخ والسياق المعتمد. لم تثبت فعالية تربوية.",
                       "Validity limited to the approved dossier, variants and context. No demonstrated pedagogical effect."))
