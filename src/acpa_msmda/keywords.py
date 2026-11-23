"""Vocabulaire EPS commun aux fiches du catalogue et aux demandes des enseignants.

Chaque mot-clé canonique (en français) regroupe les formes rencontrées dans les descriptions des
magasins d'applications (souvent en anglais) et dans les demandes des enseignants (en français).
Les formes sont comparées après normalisation (minuscules, sans accents ni ponctuation).
"""
from __future__ import annotations

from .context_engine import normalize_text

VOCABULARY: dict[str, tuple[str, ...]] = {
    "course": ("course", "courir", "run", "running", "runner", "jogging", "jog", "marathon", "5k", "10k"),
    "endurance": ("endurance", "cardio", "aerobic", "aerobie", "vo2", "vo2max", "cooper", "beep test",
                  "bleep test", "shuttle run", "navette", "leger"),
    "vitesse": ("vitesse", "sprint", "sprints", "speed", "acceleration"),
    "chronometrage": ("chronometrage", "chronometre", "chrono", "stopwatch", "timer", "lap timer", "laps",
                      "countdown", "minuteur", "temps de passage"),
    "intervalles": ("intervalle", "intervalles", "interval", "intervals", "hiit", "tabata", "emom", "circuit"),
    "marche": ("marche", "walk", "walking", "pedometer", "podometre", "step counter", "steps"),
    "frequence cardiaque": ("frequence cardiaque", "heart rate", "pulse", "bpm", "cardiofrequencemetre"),
    "natation": ("natation", "nage", "nager", "swim", "swimming", "swimmer", "piscine", "swim workout"),
    "football": ("football", "soccer", "futsal"),
    "basketball": ("basketball", "basket", "hoops"),
    "volleyball": ("volleyball", "volley"),
    "handball": ("handball",),
    "rugby": ("rugby",),
    "tennis": ("tennis", "padel"),
    "beach": ("beach volley", "beach soccer", "beach handball", "sandball"),
    "badminton": ("badminton",),
    "tennis de table": ("tennis de table", "table tennis", "ping pong", "pingpong"),
    "athletisme": ("athletisme", "athletics", "track and field", "javelin", "javelot", "shot put", "lancer de poids",
                   "hurdles", "haies", "relais", "relay"),
    "saut": ("saut", "sauter", "jump", "jumping", "vertical jump", "long jump", "high jump", "detente"),
    "corde a sauter": ("corde a sauter", "corde", "jump rope", "skipping rope", "skipping"),
    "gymnastique": ("gymnastique", "gym artistique", "gymnastique rythmique", "gymnastics", "rhythmic gymnastics",
                    "tumbling", "acrobatics", "acrobatie", "acrosport", "trampoline"),
    "yoga": ("yoga",),
    "pilates": ("pilates",),
    "musculation": ("musculation", "strength", "weight training", "dumbbell", "dumbbells",
                    "barbell", "bodybuilding", "kettlebell"),
    "renforcement": ("renforcement", "gainage", "bodyweight", "calisthenics", "core", "abs", "plank",
                     "push up", "push ups", "pushups", "squat", "squats"),
    "souplesse": ("souplesse", "etirement", "etirements", "stretch", "stretching", "flexibility", "mobility",
                  "splits"),
    "echauffement": ("echauffement", "warm up", "warmup", "warm-up"),
    "danse": ("danse", "dance", "dancing", "choreography", "choregraphie", "zumba"),
    "sports de combat": ("combat", "boxe", "boxing", "kickboxing", "wushu", "kung fu", "judo", "karate", "taekwondo", "martial arts",
                         "arts martiaux", "lutte", "wrestling"),
    "velo": ("velo", "cyclisme", "cycling", "bike", "bicycle", "vtt"),
    "orientation": ("orientation", "course d orientation", "course orientation", "orienteering", "boussole",
                    "compass", "carte", "map", "maps", "topographic", "topo"),
    "randonnee": ("randonnee", "hiking", "hike", "trail", "trek", "trekking"),
    "escalade": ("escalade", "climbing", "bouldering"),
    "video": ("video", "videos", "ralenti", "slow motion", "slow mo", "replay", "frame by frame"),
    "analyse": ("analyse", "analyser", "analysis", "analytics", "statistiques", "statistics", "stats"),
    "tactique": ("tactique", "tactic", "tactics", "playbook", "tactical board", "strategy board", "whiteboard"),
    "score": ("score", "scores", "scoreboard", "scorekeeper", "score keeper", "keep score", "marque",
              "tableau de marque", "compter les points", "marquer les points"),
    "tournoi": ("tournoi", "tournament", "bracket", "league", "championnat", "fixtures"),
    "equipes": ("equipes", "equipe", "groupes", "groupe", "team generator", "team picker", "random teams",
                "team maker", "split teams", "make teams", "teams", "groups"),
    "ateliers": ("ateliers", "atelier", "rotations", "circuit training"),
    "evaluation": ("evaluation", "evaluer", "notation", "gradebook", "grading", "grade book",
                   "assessment", "rubric", "bareme", "quiz"),
    "planification": ("planification", "planifier", "planning", "planner", "lesson plan", "schedule",
                      "session plan"),
    "entrainement": ("entrainement", "training", "workout", "workouts", "exercise", "exercises", "drills",
                     "coach", "coaching"),
    "mesure": ("mesure", "mesurer", "measure", "measurement", "tracker", "tracking", "suivi",
               "performance", "performances", "progression", "progress"),
    "respiration": ("respiration", "breathing", "relaxation", "retour au calme", "cool down"),
    "inclusion": ("inclusion", "inclusive", "adapte", "adaptive", "handicap", "disability", "accessibilite"),
    "cross": ("cross", "cross country", "cross-country", "crosscountry"),
    "course sur route": ("course sur route", "road race", "road running"),
    "golf": ("golf",),
    "echecs": ("echecs", "chess"),
    "tir a l arc": ("tir a l arc", "archery", "arc", "bow"),
    "petanque": ("petanque", "boules", "bocce"),
    "hockey": ("hockey",),
    "ski": ("ski", "skiing", "snowboard"),
    "surf": ("surf", "surfing", "bodyboard"),
    "voile": ("voile", "sailing", "sailboat", "windsurf", "kitesurf"),
    "roller": ("roller", "skate", "skateboard", "skating", "inline skating"),
    "flechettes": ("flechettes", "darts"),
    "halterophilie": ("halterophilie", "weightlifting", "olympic lifting", "clean and jerk", "snatch"),
    "jeux traditionnels": ("jeux traditionnels", "jeux traditionnels marocains", "traditional games", "jeux anciens"),
}

# Libellés affichés à l'enseignant pour chaque mot-clé canonique (traduits par i18n.t).
LABELS = {
    "chronometrage": "chronométrage", "frequence cardiaque": "fréquence cardiaque", "athletisme": "athlétisme",
    "corde a sauter": "corde à sauter", "echauffement": "échauffement", "velo": "vélo",
    "randonnee": "randonnée", "video": "vidéo", "equipes": "équipes", "evaluation": "évaluation",
    "entrainement": "entraînement", "orientation": "course d'orientation", "echecs": "échecs", "tir a l arc": "tir à l'arc", "petanque": "pétanque",
    "flechettes": "fléchettes", "halterophilie": "haltérophilie", "beach": "sports de plage",
}


def label(key: str) -> str:
    """Libellé du mot-clé dans la langue de l'interface."""
    from .i18n import t

    return t(LABELS.get(key, key))


# Formes arabes (et quelques formes courtes françaises) des mêmes mots-clés, pour les demandes saisies
# en arabe. Normalisées comme le reste : article, hamza et tâ marbûta ne gênent pas la comparaison.
_ARABIC_FORMS: dict[str, tuple[str, ...]] = {
    'course': ('جري', 'الجري', 'عدو', 'ركض'),
    'endurance': ('تحمل', 'التحمل', 'المداومة', 'مداومة'),
    'vitesse': ('سرعة', 'السرعة', 'عدو سريع'),
    'chronometrage': ('ميقاتية', 'توقيت', 'التوقيت', 'كرونومتر', 'مؤقت'),
    'intervalles': ('الجري المتقطع', 'تمارين متقطعة', 'فترات'),
    'marche': ('مشي', 'المشي', 'عداد الخطوات'),
    'frequence cardiaque': ('نبض القلب', 'معدل ضربات القلب', 'النبض', 'pulsations', 'fc'),
    'natation': ('سباحة', 'السباحة', 'مسبح'),
    'football': ('كرة القدم', 'foot'),
    'basketball': ('كرة السلة',),
    'volleyball': ('الكرة الطائرة', 'كرة الطائرة'),
    'handball': ('كرة اليد',),
    'rugby': ('الرغبي', 'رغبي'),
    'tennis': ('التنس', 'كرة المضرب'),
    'badminton': ('الريشة الطائرة',),
    'tennis de table': ('كرة الطاولة', 'تنس الطاولة'),
    'athletisme': ('العاب القوى', 'ألعاب القوى', 'رمي الجلة', 'رمي الرمح', 'الحواجز', 'التتابع'),
    'saut': ('قفز', 'القفز', 'الوثب', 'وثب', 'القفز الطويل', 'القفز العالي'),
    'corde a sauter': ('حبل القفز', 'نط الحبل'),
    'gymnastique': ('جمباز', 'الجمباز', 'الجمباز الأرضي', 'الأكروسبور'),
    'yoga': ('يوغا', 'اليوغا'),
    'musculation': ('تقوية العضلات', 'رفع الأثقال', 'كمال الأجسام'),
    'renforcement': ('التقوية العضلية', 'تقوية عضلية', 'تمارين التقوية'),
    'souplesse': ('مرونة', 'المرونة', 'تمدد', 'الإطالة'),
    'echauffement': ('إحماء', 'الإحماء', 'تسخين', 'التسخين'),
    'danse': ('رقص', 'الرقص', 'التعبير الجسدي'),
    'sports de combat': ('رياضات النزال', 'الملاكمة', 'الجيدو', 'الكراطي', 'المصارعة', 'التايكواندو'),
    'velo': ('دراجة', 'الدراجة', 'ركوب الدراجات'),
    'orientation': ('السباق التوجيهي', 'التوجيه', 'بوصلة', 'خريطة'),
    'randonnee': ('المشي الجبلي', 'التنزه', 'مشي في الطبيعة'),
    'escalade': ('تسلق', 'التسلق'),
    'video': ('فيديو', 'الفيديو', 'تصوير', 'العرض البطيء'),
    'analyse': ('تحليل', 'التحليل', 'إحصائيات'),
    'tactique': ('تكتيك', 'التكتيك', 'خطة اللعب', 'سبورة تكتيكية'),
    'score': ('النتيجة', 'تسجيل النقاط', 'لوحة النتائج'),
    'tournoi': ('دوري', 'الدوري', 'بطولة', 'البطولة'),
    'equipes': ('فرق', 'الفرق', 'تكوين الفرق', 'مجموعات', 'أفواج'),
    'ateliers': ('ورشات', 'الورشات', 'ورشة'),
    'evaluation': ('تقويم', 'التقويم', 'تقييم', 'التقييم', 'تنقيط', 'اختبار'),
    'planification': ('تخطيط', 'التخطيط', 'جذاذة', 'تحضير الحصة'),
    'entrainement': ('تدريب', 'التدريب', 'تمارين'),
    'mesure': ('قياس', 'القياس', 'تتبع', 'التتبع', 'التقدم'),
    'respiration': ('تنفس', 'التنفس', 'استرخاء', 'الرجوع إلى الهدوء'),
    'inclusion': ('إدماج', 'الإدماج', 'إعاقة', 'ذوي الاحتياجات الخاصة', 'التربية الدامجة'),
}

_ARABIC_FORMS_EXTRA: dict[str, tuple[str, ...]] = {
    "cross": ("العدو الريفي", "عدو ريفي", "الكروس"),
    "course sur route": ("السباق على الطريق",),
    "golf": ("الغولف", "الجولف"),
    "echecs": ("الشطرنج",),
    "tir a l arc": ("الرماية بالنبال", "الرماية بالقوس"),
    "petanque": ("الكرة الحديدية",),
    "hockey": ("الهوكي",),
    "ski": ("التزلج",),
    "surf": ("ركوب الموج", "السورف"),
    "voile": ("الشراع", "الإبحار الشراعي"),
    "roller": ("السكايت", "الرولر", "التزحلق"),
    "flechettes": ("الدارتس", "رمي السهام"),
    "halterophilie": ("رفع الأثقال",),
    "jeux traditionnels": ("الألعاب التقليدية", "الألعاب التقليدية والعتيقة", "ألعاب تقليدية"),
    "beach": ("الكرة الطائرة الشاطئية", "كرة القدم الشاطئية", "كرة اليد الشاطئية"),
    "orientation": ("سباق التوجيه", "السباق التوجيهي"),
    "gymnastique": ("الجمباز الإيقاعي", "الجمنازياد"),
    "sports de combat": ("الكيك بوكسينغ", "الووشو", "التايكواندو"),
}
for _key, _forms in _ARABIC_FORMS_EXTRA.items():
    _ARABIC_FORMS[_key] = _ARABIC_FORMS.get(_key, ()) + _forms
VOCABULARY = {key: forms + _ARABIC_FORMS.get(key, ()) for key, forms in VOCABULARY.items()}

# Activités physiques et sportives : un besoin de ce type pèse plus que le besoin d'une fonction
# (chronomètre, score...) et une demande qui en nomme une écarte les outils généralistes.
ACTIVITIES = frozenset({
    "course", "endurance", "vitesse", "intervalles", "marche", "natation", "football", "basketball",
    "volleyball", "handball", "rugby", "tennis", "badminton", "tennis de table", "athletisme", "saut",
    "corde a sauter", "gymnastique", "yoga", "pilates", "musculation", "renforcement", "souplesse", "danse",
    "sports de combat", "velo", "orientation", "randonnee", "escalade", "cross", "course sur route", "golf",
    "echecs", "tir a l arc", "petanque", "hockey", "ski", "surf", "voile", "roller", "flechettes",
    "halterophilie", "jeux traditionnels", "beach",
})

# Formes trop ambiguës dans les descriptions anglaises des magasins (« of course », « golf course »,
# « screen orientation », « core features »...) : elles servent pour les demandes des enseignants,
# pas pour indexer les fiches.
QUERY_ONLY = frozenset({"course", "courir", "orientation", "carte", "map", "maps", "marque", "core", "abs",
                        "steps", "circuit", "trail", "combat", "corde", "groupe", "groupes", "equipe",
                        "league", "schedule", "coach", "coaching", "performance", "performances",
                        "progress", "tracking", "tracker", "arc", "bow", "cross", "voile", "ski",
                        "suivi", "mesure", "analyse", "score", "scores", "skate", "roller", "teams", "groups",
                        "adaptive", "adapte", "inclusive"})


OFFLINE_FORMS = ("offline", "no internet", "without internet", "works without", "sans connexion",
                 "hors ligne", "hors connexion", "no connection", "no wifi", "بدون انترنت", "بدون اتصال",
                 "دون انترنت", "دون اتصال", "بلا انترنت", "لا يوجد انترنت", "غير متصل")

_FORMS = sorted(((normalize_text(form).strip(), key, form in QUERY_ONLY)
                 for key, forms in VOCABULARY.items() for form in forms), key=lambda item: -len(item[0]))


def keywords_in(text: str, catalog: bool = False) -> list[str]:
    """Mots-clés canoniques présents dans un texte (forme entière, pas un fragment de mot).

    Les formes longues passent d'abord et « consomment » leurs mots : « course d'orientation » donne
    orientation, pas course. Avec ``catalog=True`` (description d'une fiche), les formes ambiguës
    de QUERY_ONLY sont ignorées."""
    padded = " " + " ".join(normalize_text(text or "").split()) + " "
    found = set()
    for form, key, query_only in _FORMS:
        if not form or (catalog and query_only):
            continue
        needle = f" {form} "
        if needle in padded:
            found.add(key)
            padded = padded.replace(needle, " | ")
    return sorted(found)


def mentions_offline(text: str) -> bool:
    padded = f" {normalize_text(text or '')} "
    return any(f" {normalize_text(form)} " in padded for form in OFFLINE_FORMS)
