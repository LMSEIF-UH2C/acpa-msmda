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
    "natation": ("natation", "nage", "nager", "swim", "swimming", "swimmer", "pool", "piscine"),
    "football": ("football", "soccer", "futsal"),
    "basketball": ("basketball", "basket", "hoops"),
    "volleyball": ("volleyball", "volley"),
    "handball": ("handball",),
    "rugby": ("rugby",),
    "tennis": ("tennis", "padel"),
    "badminton": ("badminton",),
    "tennis de table": ("tennis de table", "table tennis", "ping pong", "pingpong"),
    "athletisme": ("athletisme", "athletics", "track and field", "javelin", "javelot", "shot put", "lancer de poids",
                   "hurdles", "haies", "relais", "relay"),
    "saut": ("saut", "sauter", "jump", "jumping", "vertical jump", "long jump", "high jump", "detente"),
    "corde a sauter": ("corde a sauter", "corde", "jump rope", "skipping rope", "skipping"),
    "gymnastique": ("gymnastique", "gym artistique", "gymnastics", "tumbling", "acrobatics", "acrobatie",
                    "acrosport", "trampoline"),
    "yoga": ("yoga",),
    "pilates": ("pilates",),
    "musculation": ("musculation", "strength", "weight training", "weightlifting", "dumbbell", "dumbbells",
                    "barbell", "bodybuilding", "kettlebell"),
    "renforcement": ("renforcement", "gainage", "bodyweight", "calisthenics", "core", "abs", "plank",
                     "push up", "push ups", "pushups", "squat", "squats"),
    "souplesse": ("souplesse", "etirement", "etirements", "stretch", "stretching", "flexibility", "mobility",
                  "splits"),
    "echauffement": ("echauffement", "warm up", "warmup", "warm-up"),
    "danse": ("danse", "dance", "dancing", "choreography", "choregraphie", "zumba"),
    "sports de combat": ("combat", "boxe", "boxing", "judo", "karate", "taekwondo", "martial arts",
                         "arts martiaux", "lutte", "wrestling"),
    "velo": ("velo", "cyclisme", "cycling", "bike", "bicycle", "vtt"),
    "orientation": ("orientation", "course d orientation", "orienteering", "boussole", "compass", "carte",
                    "map", "maps", "gps", "topographic", "topo"),
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
}

# Libellés affichés à l'enseignant pour chaque mot-clé canonique (traduits par i18n.t).
LABELS = {
    "chronometrage": "chronométrage", "frequence cardiaque": "fréquence cardiaque", "athletisme": "athlétisme",
    "corde a sauter": "corde à sauter", "echauffement": "échauffement", "velo": "vélo",
    "randonnee": "randonnée", "video": "vidéo", "equipes": "équipes", "evaluation": "évaluation",
    "entrainement": "entraînement",
}


def label(key: str) -> str:
    """Libellé du mot-clé dans la langue de l'interface."""
    from .i18n import t

    return t(LABELS.get(key, key))


# Formes arabes (et quelques formes courtes françaises) des mêmes mots-clés, pour les demandes saisies
# en arabe. Normalisées comme le reste : article, hamza et tâ marbûta ne gênent pas la comparaison.
_ARABIC_FORMS: dict[str, tuple[str, ...]] = {
    'course': ('جري', 'الجري', 'عدو', 'ركض'),
    'endurance': ('تحمل', 'التحمل', 'المداومة', 'مداومة', 'جري المداومة'),
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
VOCABULARY = {key: forms + _ARABIC_FORMS.get(key, ()) for key, forms in VOCABULARY.items()}

OFFLINE_FORMS = ("offline", "no internet", "without internet", "works without", "sans connexion",
                 "hors ligne", "hors connexion", "no connection", "no wifi", "بدون انترنت", "بدون اتصال",
                 "دون انترنت", "دون اتصال", "بلا انترنت", "لا يوجد انترنت", "غير متصل")

_FORMS = sorted(((normalize_text(form), key) for key, forms in VOCABULARY.items() for form in forms),
                key=lambda pair: -len(pair[0]))


def keywords_in(text: str) -> list[str]:
    """Mots-clés canoniques présents dans un texte (forme entière, pas un fragment de mot)."""
    padded = f" {normalize_text(text or '')} "
    return sorted({key for form, key in _FORMS if form and f" {form} " in padded})


def mentions_offline(text: str) -> bool:
    padded = f" {normalize_text(text or '')} "
    return any(f" {normalize_text(form)} " in padded for form in OFFLINE_FORMS)
