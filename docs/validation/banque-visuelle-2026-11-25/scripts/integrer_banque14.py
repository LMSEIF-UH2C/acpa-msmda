"""Intègre la remise des 14 illustrations dans le manifeste de la banque visuelle et les traductions.

Usage : python -I integrer_banque14.py <manifeste_de_remise.json> <sha256_archive> <racine_du_depot>
Le manifeste de remise est lu comme donnée JSON uniquement.
"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

delivery_path, archive_sha, repo = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
delivery = {e["id"]: e for e in json.loads(delivery_path.read_text(encoding="utf-8"))}

ALT = {
    "leger20": (
        "Groupe d'élèves en course entre deux lignes balisées par des plots, dans une cour d'établissement ; "
        "l'enseignant tient un porte-bloc près d'une enceinte qui diffuse le signal sonore. "
        "Matériel représenté : plots, lignes au sol, enceinte, porte-bloc.",
        "مجموعة من التلاميذ يجرون بين خطين محددين بأقماع في ساحة مؤسسة تعليمية؛ يقف الأستاذ حاملًا لوح كتابة "
        "قرب مكبر صوت يبث الإشارة الصوتية. العتاد الظاهر في الرسم: أقماع، خطوط على الأرض، مكبر صوت، لوح كتابة.",
        "Group of students running between two lines marked with cones in a school yard; the teacher holds a "
        "clipboard next to a speaker playing the audio signal. Equipment shown: cones, floor lines, speaker, clipboard.",
    ),
    "sprint30": (
        "Départ individuel d'un sprint dans un couloir balisé, pendant que les autres élèves attendent leur tour ; "
        "l'enseignant tient un chronomètre, sur le côté. Matériel représenté : plots, lignes au sol, chronomètre.",
        "انطلاق فردي في عدو داخل رواق محدد، بينما ينتظر باقي التلاميذ دورهم؛ يقف الأستاذ جانبًا حاملًا ميقاتية. "
        "العتاد الظاهر في الرسم: أقماع، خطوط على الأرض، ميقاتية.",
        "Individual sprint start in a marked lane while the other students wait their turn; the teacher holds a "
        "stopwatch at the side. Equipment shown: cones, floor lines, stopwatch.",
    ),
    "saut_horizontal": (
        "Saut pieds joints sans élan, en trois phases : flexion bras en arrière derrière la ligne, envol, réception. "
        "Un ruban de mesure part de la ligne de départ. Matériel représenté : ligne de départ, ruban de mesure.",
        "قفز بالقدمين معًا من الثبات في ثلاث مراحل: ثني الركبتين والذراعان إلى الخلف وراء الخط، ثم الطيران، ثم الهبوط. "
        "يمتد شريط قياس من خط الانطلاق. العتاد الظاهر في الرسم: خط الانطلاق، شريط قياس.",
        "Two-footed jump without run-up, in three phases: crouch with arms back behind the line, flight, landing. "
        "A tape measure runs from the take-off line. Equipment shown: take-off line, tape measure.",
    ),
    "sargent": (
        "Le long d'une toise murale : marque bras tendu en position debout, puis marque au sommet du saut ; "
        "la flèche indique l'écart entre les deux marques. La flexion préparatoire, à droite, ne fixe pas l'ordre "
        "des étapes. Matériel représenté : toise murale graduée.",
        "على طول مسطرة حائطية مدرجة: علامة الذراع الممدودة في وضع الوقوف، ثم علامة أعلى نقطة في القفزة؛ يشير السهم "
        "إلى الفرق بين العلامتين. ثني الركبتين التحضيري الظاهر على اليمين لا يحدد ترتيب المراحل. "
        "العتاد الظاهر في الرسم: مسطرة حائطية مدرجة.",
        "Along a wall-mounted scale: mark with the arm extended while standing, then mark at the peak of the jump; "
        "the arrow shows the gap between the two marks. The preparatory crouch, on the right, does not set the order "
        "of the steps. Equipment shown: graduated wall scale.",
    ),
    "medecine_ball": (
        "Lancer en trois phases, assis dos au mur, jambes tendues : ballon contre la poitrine, poussée des deux bras, "
        "ballon en vol. Un ruban de mesure part du pied du mur. Matériel représenté : médecine-ball, mur, ruban de mesure.",
        "رمي في ثلاث مراحل من الجلوس، والظهر مستند إلى الحائط والرجلان ممدودتان: الكرة على الصدر، ثم الدفع بالذراعين، "
        "ثم الكرة في الهواء. يمتد شريط قياس من أسفل الحائط. العتاد الظاهر في الرسم: كرة طبية، حائط، شريط قياس.",
        "Throw in three phases, seated with the back against the wall and legs extended: ball against the chest, "
        "two-arm push, ball in flight. A tape measure runs from the foot of the wall. "
        "Equipment shown: medicine ball, wall, tape measure.",
    ),
    "souplesse_assise": (
        "Élève assis et chaussé, jambes tendues, pieds contre une boîte graduée ; il pousse le curseur du bout "
        "des doigts. Matériel représenté : boîte de souplesse graduée avec curseur.",
        "تلميذ جالس بحذائه، والرجلان ممدودتان والقدمان مستندتان إلى صندوق مدرج؛ يدفع المؤشر بأطراف أصابعه. "
        "العتاد الظاهر في الرسم: صندوق مرونة مدرج بمؤشر منزلق.",
        "Student seated with shoes on and legs extended, feet against a graduated box, pushing the slider with the "
        "fingertips. Equipment shown: graduated sit-and-reach box with slider.",
    ),
    "souplesse_debout": (
        "Élève debout pieds nus sur un support stable, jambes tendues, qui descend les mains le long d'une règle "
        "graduée verticale ; l'enseignant note le résultat. Matériel représenté : support stable, règle graduée.",
        "تلميذ واقف حافي القدمين على قاعدة ثابتة، والرجلان ممدودتان، ينزل بيديه على طول مسطرة مدرجة عمودية؛ "
        "يسجل الأستاذ النتيجة. العتاد الظاهر في الرسم: قاعدة ثابتة، مسطرة مدرجة.",
        "Student standing barefoot on a stable support, legs straight, lowering the hands along a vertical graduated "
        "ruler; the teacher records the result. Equipment shown: stable support, graduated ruler.",
    ),
    "flamingo": (
        "Une élève en équilibre sur un pied sur une poutre basse, tenant l'autre pied derrière elle, un bras tendu ; "
        "l'enseignant tient un chronomètre. Matériel représenté : poutre basse et étroite, chronomètre.",
        "تلميذة في وضع توازن على قدم واحدة فوق عارضة منخفضة، تمسك القدم الأخرى خلفها وذراعها ممدودة؛ "
        "يمسك الأستاذ ميقاتية. العتاد الظاهر في الرسم: عارضة منخفضة وضيقة، ميقاتية.",
        "A student balancing on one foot on a low beam, holding the other foot behind her, one arm extended; the "
        "teacher holds a stopwatch. Equipment shown: low, narrow beam, stopwatch.",
    ),
    "taille": (
        "Élève debout pieds nus, dos contre une toise ; l'enseignant descend le curseur jusqu'au sommet de la tête. "
        "Matériel représenté : toise.",
        "تلميذ واقف حافي القدمين وظهره إلى مقياس القامة؛ ينزل الأستاذ المؤشر حتى قمة الرأس. "
        "العتاد الظاهر في الرسم: مقياس القامة.",
        "Student standing barefoot with the back against a stadiometer; the teacher lowers the headpiece onto the top "
        "of the head. Equipment shown: stadiometer.",
    ),
    "poids": (
        "Élève debout pieds nus sur une balance ; l'enseignant note la mesure. Matériel représenté : balance.",
        "تلميذ واقف حافي القدمين على ميزان؛ يسجل الأستاذ القياس. العتاد الظاهر في الرسم: ميزان.",
        "Student standing barefoot on a scale; the teacher records the measurement. Equipment shown: scale.",
    ),
    "fc_repos": (
        "Élève assis au repos, avant-bras posé sur une table ; l'enseignant prend le pouls au poignet, chronomètre "
        "en main. Matériel représenté : chaise, table, chronomètre.",
        "تلميذ جالس في راحة وساعده على طاولة؛ يقيس الأستاذ النبض عند المعصم والميقاتية في يده. "
        "العتاد الظاهر في الرسم: كرسي، طاولة، ميقاتية.",
        "Student seated at rest, forearm on a table; the teacher takes the pulse at the wrist, stopwatch in hand. "
        "Equipment shown: chair, table, stopwatch.",
    ),
    "ruffier": (
        "Séquence en cinq vignettes : P1, fréquence cardiaque au repos ; 30 flexions en 45 s ; P2, fréquence "
        "cardiaque immédiate ; récupération, 1 min ; P3, fréquence cardiaque après récupération. Les prises de pouls "
        "sont représentées en position assise, au poignet, chronométrées par l'enseignant. "
        "Matériel représenté : chaise, chronomètre.",
        "تسلسل في خمس صور: P1، نبض القلب في الراحة؛ 30 ثنية للركبتين في 45 ثانية؛ P2، نبض القلب مباشرة بعد الجهد؛ "
        "الاسترجاع، دقيقة واحدة؛ P3، نبض القلب بعد الاسترجاع. تظهر قياسات النبض في وضع الجلوس، عند المعصم، "
        "بتوقيت من الأستاذ. العتاد الظاهر في الرسم: كرسي، ميقاتية.",
        "Five-panel sequence: P1, resting heart rate; 30 squats in 45 s; P2, immediate heart rate; recovery, 1 min; "
        "P3, heart rate after recovery. Pulse checks are shown seated, at the wrist, timed by the teacher. "
        "Equipment shown: chair, stopwatch.",
    ),
    "killy": (
        "Élève dos au mur, cuisses à l'horizontale et bras croisés, en maintien ; l'enseignante tient le chronomètre. "
        "Matériel représenté : mur, chronomètre.",
        "تلميذ ظهره مستند إلى الحائط، والفخذان في وضع أفقي والذراعان متقاطعتان، في وضع ثبات؛ تمسك الأستاذة الميقاتية. "
        "العتاد الظاهر في الرسم: حائط، ميقاتية.",
        "Student with the back against the wall, thighs horizontal and arms crossed, holding the position; the teacher "
        "holds the stopwatch. Equipment shown: wall, stopwatch.",
    ),
    "front_plank": (
        "Gainage sur les avant-bras et la pointe des pieds, corps aligné, sur un tapis ; un chronomètre est posé au sol. "
        "Matériel représenté : tapis, chronomètre.",
        "ثبات على الساعدين وأطراف القدمين، والجسم مستقيم، فوق بساط؛ ميقاتية موضوعة على الأرض. "
        "العتاد الظاهر في الرسم: بساط، ميقاتية.",
        "Plank on the forearms and toes, body aligned, on a mat; a stopwatch lies on the floor. "
        "Equipment shown: mat, stopwatch.",
    ),
}

manifest_path = repo / "assets" / "visual-bank" / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
assert set(ALT) == set(delivery) == {e["id"] for e in manifest["lab_specific"]}, "inventaire divergent"

manifest["purpose"] = "Banque de ressources facultatives ; repères affichés à la demande dans le Laboratoire"
updated = []
for entry in manifest["lab_specific"]:
    d = delivery[entry["id"]]
    path = repo / d["path"]
    data = path.read_bytes()
    with Image.open(path) as image:
        size = image.size
    assert hashlib.sha256(data).hexdigest() == d["sha256"] and len(data) == d["bytes"], entry["id"]
    assert size == (d["width"], d["height"]), entry["id"]
    updated.append({
        "id": entry["id"],
        "path": d["path"],
        "status": "accepted_by_user_imported",
        "origin": entry["origin"],
        "scientific_status": d["scientific_status"],
        "width": d["width"],
        "height": d["height"],
        "bytes": d["bytes"],
        "sha256": d["sha256"],
        "retouch": "aucune",
        "delivery_note": d["note"],
        "alt": ALT[entry["id"]][0],
    })
manifest["lab_specific"] = updated
manifest["lab_delivery"] = {
    "archive": "ACPA_MSMDA_banque_visuelle_14.zip",
    "sha256": archive_sha,
    "received": "2026-11-25",
    "files": len(updated),
    "retouch": "aucune : fichiers importés tels que remis, empreintes vérifiées",
    "evidence": "docs/validation/banque-visuelle-2026-11-25/remise/",
}
order = ["version", "date", "purpose", "lab_delivery", "lab_specific", "lab_generic", "icons", "references"]
manifest = {k: manifest[k] for k in order + [k for k in manifest if k not in order]}
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

tr_path = repo / "data" / "translations.json"
translations = json.loads(tr_path.read_text(encoding="utf-8"))
for fr, ar, en in ALT.values():
    for text in (fr, ar, en):
        assert "—" not in text, text
    translations[fr] = {"ar": ar, "en": en}
tr_path.write_text(json.dumps(translations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("manifeste et traductions mis à jour :", len(updated), "illustrations")
