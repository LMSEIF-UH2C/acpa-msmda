"""Restitution des analyses du Laboratoire EPS en trois niveaux : comprendre, analyser, investiguer.

Module de présentation uniquement. Il lit les résultats déjà calculés par ``lab_statistics`` sans
les modifier ni recalculer les tests. Seules exceptions, explicites : les statistiques descriptives
des données affichées (moyenne, écart-type, médiane, extrêmes) et les droites d'un graphique de
régression ou d'interaction, obtenues à partir des coefficients calculés. Aucun intervalle de
confiance ni aucune taille d'effet n'est ajouté quand le moteur ne les fournit pas.

Règles d'interprétation (prudentes, jamais causales) :
- seuil de décision α = 0,05, présenté comme une convention, pas comme une preuve ;
- un résultat non significatif ne démontre pas l'absence d'effet ;
- ordres de grandeur conventionnels des tailles d'effet (Cohen, 1988) : d ou dz 0,2 / 0,5 / 0,8 ;
  r, rho, W de Kendall et corrélation bisériale de rangs 0,1 / 0,3 / 0,5 ; η² et η²p 0,01 / 0,06 / 0,14.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from statistics import mean, median, stdev
from typing import Any, Sequence

from .i18n import colon, current, is_rtl, t

ALPHA = 0.05
STUDY_METHODS = ("descriptive", "pearson", "spearman", "paired_t", "wilcoxon", "repeated_anova", "friedman",
                 "mixed_anova", "paired_posthoc", "welch", "mann_whitney", "one_way")
MULTIVARIABLE_METHODS = ("pearson", "spearman", "regression", "moderation")


# ---------------------------------------------------------------------------- mise en forme

def ltr(text: str) -> str:
    """En arabe, isole un nombre ou une expression mathématique (« < 0.001 », « [0.17, 1.33] »,
    « 16.51 (2, 46) ») pour qu'il garde l'ordre de gauche à droite dans une phrase de droite à gauche."""
    return f"\u2066{text}\u2069" if is_rtl() else text


def _plain(value: Any, digits: int = 2, sign: bool = False) -> str:
    text = f"{float(value):+.{digits}f}" if sign else f"{float(value):.{digits}f}"
    return text.replace(".", ",") if current() == "fr" else text


def num(value: Any, digits: int = 2, sign: bool = False) -> str:
    """Nombre lisible : virgule décimale en français, point en arabe et en anglais."""
    if value is None:
        return "–"
    return ltr(_plain(value, digits, sign))


def pval(p: Any) -> str:
    """p arrondie à 3 décimales ; « < 0,001 » en dessous."""
    if p is None:
        return "–"
    return ltr("< " + _plain(0.001, 3)) if p < 0.001 else num(p, 3)


def ci(interval: Any, digits: int = 2) -> str | None:
    if not interval or len(interval) != 2 or any(v is None for v in interval):
        return None
    sep = " ; " if current() == "fr" else ", "
    return ltr(f"[{_plain(interval[0], digits)}{sep}{_plain(interval[1], digits)}]")


def magnitude(value: float | None, small: float, medium: float, large: float) -> str | None:
    if value is None:
        return None
    v = abs(value)
    if v < small:
        return t("négligeable")
    if v < medium:
        return t("faible")
    if v < large:
        return t("moyen")
    return t("élevé")


def significant(p: Any) -> bool | None:
    return None if p is None else p < ALPHA


# ---------------------------------------------------------------------------- contenu

@dataclass
class Indicator:
    label: str
    value: str
    help: str | None = None


@dataclass
class Restitution:
    """Ce qui est affiché à chaque niveau."""
    indicators: list[Indicator] = field(default_factory=list)
    sample: list[Indicator] = field(default_factory=list)
    interpretation: list[str] = field(default_factory=list)
    tables: list[tuple[str, list[dict]]] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    limits: list[str] = field(default_factory=list)


CONDITIONS = {
    "descriptive": ["Statistiques descriptives des cas complets : aucune inférence au-delà de l'échantillon."],
    "pearson": ["Relation approximativement linéaire, sans valeur extrême isolée.",
                "Distribution conjointe proche de la normale pour l'intervalle de confiance.",
                "Participants indépendants (attention aux élèves d'une même classe)."],
    "spearman": ["Relation monotone (qui augmente ou diminue de façon régulière).",
                 "Participants indépendants ; nombreuses égalités de rangs à signaler."],
    "paired_t": ["Mêmes participants mesurés deux fois, dans des conditions comparables.",
                 "Différences approximativement normales, sans valeur extrême isolée."],
    "wilcoxon": ["Mêmes participants mesurés deux fois.",
                 "Distribution des différences à peu près symétrique."],
    "repeated_anova": ["Mêmes participants à chaque occasion, cas complets.",
                       "Sphéricité : la correction de Greenhouse-Geisser est fournie lorsqu'elle est calculée.",
                       "Résidus approximativement normaux."],
    "friedman": ["Mêmes participants à chaque occasion, cas complets.",
                 "Test sur les rangs : adapté aux données ordinales ou non normales."],
    "mixed_anova": ["Groupes indépendants, effectifs égaux, mêmes occasions pour tous.",
                    "Covariances comparables entre groupes ; sphéricité corrigée lorsqu'elle est calculée.",
                    "Résidus approximativement normaux."],
    "paired_posthoc": ["Comparaisons deux à deux par t apparié, correction de Holm sur l'ensemble des comparaisons.",
                       "À interpréter après un test global (ANOVA répétée ou Friedman)."],
    "welch": ["Deux groupes indépendants ; variances inégales acceptées.",
              "Distributions approximativement normales ou effectifs suffisants."],
    "mann_whitney": ["Deux groupes indépendants.",
                     "Test sur les rangs : compare les distributions, pas seulement les médianes."],
    "one_way": ["Groupes indépendants, variances comparables.",
                "Résidus approximativement normaux ; aucune comparaison deux à deux n'est fournie ici."],
    "regression": ["Relation linéaire, résidus indépendants, de variance constante et approximativement normaux.",
                   "Absence de colinéarité forte et de valeurs très influentes."],
    "moderation": ["Mêmes conditions que la régression ; X et M centrés avant le produit X × M.",
                   "L'interaction décrit une variation de la relation X–Y selon M, pas un mécanisme."],
}
LIMITS = {
    "default": ["Analyse exploratoire sur cas complets : les participants incomplets sont exclus, sans imputation.",
                "Une association ou une différence observée ne prouve pas une relation de cause à effet.",
                "Un résultat non significatif ne démontre pas l'absence d'effet, surtout avec un petit effectif."],
    "regression": ["Le R² décrit l'ajustement dans cet échantillon ; il surestime en général la performance sur d'autres élèves."],
    "moderation": ["Les droites simples sont tracées à M = moyenne − 1 ET, moyenne et moyenne + 1 ET de l'échantillon."],
    "paired_posthoc": ["La correction de Holm contrôle le risque d'erreur sur l'ensemble des comparaisons."],
}


def _sample(result: dict) -> list[Indicator]:
    """Participants analysés et données manquantes, d'après ce que le moteur a renvoyé."""
    out = []
    if "n_eligible" in result:
        analysed = result.get("n_complete", result.get("n"))
        out.append(Indicator(t("Participants analysés"), ltr(f"{analysed} / {result['n_eligible']}")))
        if result.get("n_excluded") is not None:
            out.append(Indicator(t("Exclus (données manquantes)"), str(result["n_excluded"])))
    elif "included" in result and "eligible" in result:
        labels = result.get("group_labels") or [str(i + 1) for i in range(len(result["included"]))]
        out.append(Indicator(t("Participants analysés"), " · ".join(
            ltr(f"{g} {i}/{e}") for g, i, e in zip(labels, result["included"], result["eligible"]))))
        missing = sum(e - i for i, e in zip(result["included"], result["eligible"]))
        out.append(Indicator(t("Exclus (données manquantes)"), str(missing)))
    elif "n" in result:
        out.append(Indicator(t("Participants analysés"), str(result["n"])))
    return out


def _decision(p: Any, what: str) -> str:
    """Phrase prudente selon le seuil de 5 %. ``what`` : « différence » ou « association »."""
    if p is None:
        return t("Probabilité non calculée : aucune conclusion de test.")
    expr = ltr("p < " + _plain(0.001, 3)) if p < 0.001 else ltr("p = " + _plain(p, 3))
    if p < ALPHA:
        return t("Une {what} statistiquement significative est observée au seuil de 5 % ({p}).",
                 what=t(what), p=expr)
    return t("Aucune {what} statistiquement significative n'est détectée au seuil de 5 % ({p}) ; "
             "cela ne prouve pas son absence.", what=t(what), p=expr)


def _effect_sentence(label: str, value: float | None, size: str | None) -> str | None:
    if value is None or size is None:
        return None
    return t("Taille d'effet {label} = {v} : effet {size} selon les repères usuels.",
             label=label, v=num(value), size=size)


def describe(columns: Sequence[str], values: Sequence[Sequence[float]]) -> list[dict]:
    """Statistiques descriptives par colonne (occasion ou groupe) des valeurs affichées."""
    rows = []
    for j, name in enumerate(columns):
        col = [float(r[j]) for r in values if r[j] is not None]
        if not col:
            continue
        rows.append({t("Occasion"): name, "n": len(col), t("Moyenne"): num(mean(col)),
                     t("Écart-type"): num(stdev(col)) if len(col) > 1 else "–",
                     t("Médiane"): num(median(col)), t("Minimum"): num(min(col)), t("Maximum"): num(max(col))})
    return rows


def build(method: str, result: dict, panel_values: Sequence[Sequence[float]] | None = None,
          columns: Sequence[str] | None = None) -> Restitution:
    """Contenu des trois niveaux pour une méthode et son résultat calculé."""
    r = Restitution(sample=_sample(result))
    add_effect = r.interpretation.append

    def effect(label, value, thresholds):
        sentence = _effect_sentence(label, value, magnitude(value, *thresholds) if value is not None else None)
        if sentence:
            add_effect(sentence)

    if method == "descriptive":
        if panel_values is not None and columns:
            r.tables.append((t("Statistiques descriptives"), describe(columns, panel_values)))
            means = [mean([row[j] for row in panel_values]) for j in range(len(columns))] if panel_values else []
            if len(means) >= 2:
                r.indicators.append(Indicator(t("Écart des moyennes (dernière − première)"),
                                              num(means[-1] - means[0], sign=True)))
        r.interpretation.append(t("Description de l'échantillon : ces chiffres ne se généralisent pas à d'autres élèves."))
    elif method in ("pearson", "spearman"):
        coef = result.get("r") if method == "pearson" else result.get("rho")
        name = "r" if method == "pearson" else "ρ"
        r.indicators.append(Indicator(name, num(coef)))
        r.indicators.append(Indicator("p", pval(result.get("p"))))
        if ci(result.get("ci95")):
            r.indicators.append(Indicator(t("IC 95 %"), ci(result["ci95"])))
        direction = t("positive") if coef and coef > 0 else t("négative")
        r.interpretation.append(t("Association {direction} : quand une mesure est plus élevée, l'autre tend à l'être {sens}.",
                                  direction=direction, sens=t("aussi") if coef and coef > 0 else t("moins")))
        r.interpretation.append(_decision(result.get("p"), "association"))
        effect(name, coef, (.1, .3, .5))
        row = {name: num(coef), "p": pval(result.get("p")), "n": result.get("n")}
        if ci(result.get("ci95")):
            row[t("IC 95 %")] = ci(result["ci95"])
        r.tables.append((t("Corrélation"), [row]))
    elif method in ("paired_t", "wilcoxon"):
        if method == "paired_t":
            r.indicators += [Indicator(t("Différence moyenne (après − avant)"), num(result.get("mean_difference"), sign=True)),
                             Indicator("p", pval(result.get("p"))), Indicator("dz", num(result.get("dz")))]
            if ci(result.get("ci95")):
                r.indicators.append(Indicator(t("IC 95 % de la différence"), ci(result["ci95"])))
            r.tables.append((t("Test t apparié"), [{"t": num(result.get("t")), "ddl": result.get("df"), "p": pval(result.get("p")),
                                                    t("Différence moyenne"): num(result.get("mean_difference"), sign=True),
                                                    t("IC 95 %"): ci(result.get("ci95")) or "–", "dz": num(result.get("dz")),
                                                    "n": result.get("n")}]))
            effect("dz", result.get("dz"), (.2, .5, .8))
        else:
            r.indicators += [Indicator("W", num(result.get("W"), 1)), Indicator("p", pval(result.get("p")))]
            r.tables.append((t("Test de Wilcoxon"), [{"W": num(result.get("W"), 1), "p": pval(result.get("p")), "n": result.get("n")}]))
            r.interpretation.append(t("Le moteur ne calcule pas de taille d'effet pour ce test : aucune n'est affichée."))
        r.interpretation.insert(0, _decision(result.get("p"), "différence"))
    elif method in ("repeated_anova", "friedman"):
        if method == "repeated_anova":
            p_main = result.get("p_gg") if result.get("p_gg") is not None else result.get("p")
            r.indicators += [Indicator("F", ltr(f"{_plain(result.get('F'))} ({result.get('df1')}, {result.get('df2')})")),
                             Indicator("p" + (" (GG)" if result.get("p_gg") is not None else ""), pval(p_main)),
                             Indicator("η²p", num(result.get("partial_eta2")))]
            r.tables.append((t("ANOVA à mesures répétées"), [{"F": num(result.get("F")), "ddl1": result.get("df1"),
                                                             "ddl2": result.get("df2"), "p": pval(result.get("p")),
                                                             "ε GG": num(result.get("gg_epsilon"), 3),
                                                             "p GG": pval(result.get("p_gg")), "η²p": num(result.get("partial_eta2")),
                                                             "n": result.get("n"), "k": result.get("k")}]))
            r.interpretation.append(_decision(p_main, "différence entre occasions"))
            effect("η²p", result.get("partial_eta2"), (.01, .06, .14))
        else:
            r.indicators += [Indicator("χ²", num(result.get("chi2"))), Indicator("p", pval(result.get("p"))),
                             Indicator("W", num(result.get("kendall_W")))]
            r.tables.append((t("Test de Friedman"), [{"χ²": num(result.get("chi2")), "p": pval(result.get("p")),
                                                      "W": num(result.get("kendall_W")), "n": result.get("n"), "k": result.get("k")}]))
            r.interpretation.append(_decision(result.get("p"), "différence entre occasions"))
            effect("W", result.get("kendall_W"), (.1, .3, .5))
        if panel_values is not None and columns:
            r.tables.append((t("Statistiques descriptives"), describe(columns, panel_values)))
    elif method == "mixed_anova":
        names = {"group": t("Groupe"), "time": t("Temps"), "group_time": t("Interaction groupe × temps")}
        rows = []
        for key in ("group", "time", "group_time"):
            e = result.get(key) or {}
            rows.append({t("Effet"): names[key], "F": num(e.get("F")), "ddl1": e.get("df1"), "ddl2": e.get("df2"),
                         "p": pval(e.get("p")), "p GG": pval(e.get("p_gg")) if key != "group" else "–",
                         "η²p": num(e.get("partial_eta2"))})
        r.tables.append((t("ANOVA mixte"), rows))
        inter = result.get("group_time") or {}
        p_inter = inter.get("p_gg", inter.get("p"))
        r.indicators += [Indicator(t("Interaction groupe × temps") + " · p", pval(p_inter)),
                         Indicator("η²p", num(inter.get("partial_eta2")))]
        r.interpretation.append(_decision(p_inter, "différence d'évolution entre groupes"))
        effect("η²p", inter.get("partial_eta2"), (.01, .06, .14))
    elif method == "paired_posthoc":
        labels = result.get("occasion_labels") or []
        rows = []
        for c in result.get("contrasts", []):
            a = labels[c["first"]] if c["first"] < len(labels) else c["first"]
            b = labels[c["second"]] if c["second"] < len(labels) else c["second"]
            rows.append({t("Comparaison"): f"{b} − {a}", t("Différence moyenne"): num(c.get("mean_difference"), sign=True),
                         t("IC 95 %"): ci(c.get("ci95")) or "–", "t": num(c.get("t")), "p": pval(c.get("p")),
                         "p Holm": pval(c.get("p_holm")), "dz": num(c.get("dz"))})
        r.tables.append((t("Comparaisons deux à deux (Holm)"), rows))
        n_sig = sum(1 for c in result.get("contrasts", []) if c.get("p_holm") is not None and c["p_holm"] < ALPHA)
        r.indicators.append(Indicator(t("Comparaisons significatives (Holm)"), ltr(f"{n_sig} / {len(rows)}")))
        r.interpretation.append(t("{n} comparaison(s) sur {total} reste(nt) significative(s) après correction de Holm.",
                                  n=n_sig, total=len(rows)))
    elif method in ("welch", "mann_whitney"):
        labels = result.get("group_labels") or ["1", "2"]
        if method == "welch":
            r.indicators += [Indicator(t("Différence moyenne ({a} − {b})", a=labels[0], b=labels[-1]),
                                       num(result.get("mean_difference"), sign=True)),
                             Indicator("p", pval(result.get("p")))]
            if ci(result.get("ci95")):
                r.indicators.append(Indicator(t("IC 95 % de la différence"), ci(result["ci95"])))
            r.tables.append((t("Test t de Welch"), [{"t": num(result.get("t")), "ddl": num(result.get("df"), 1), "p": pval(result.get("p")),
                                                     t("Différence moyenne"): num(result.get("mean_difference"), sign=True),
                                                     t("IC 95 %"): ci(result.get("ci95")) or "–",
                                                     "n1": result.get("n1"), "n2": result.get("n2")}]))
            r.interpretation.append(t("Le moteur ne calcule pas de taille d'effet pour ce test : aucune n'est affichée."))
        else:
            r.indicators += [Indicator("U", num(result.get("U"), 1)), Indicator("p", pval(result.get("p"))),
                             Indicator(t("Corrélation bisériale de rangs"), num(result.get("rank_biserial")))]
            r.tables.append((t("Test de Mann-Whitney"), [{"U": num(result.get("U"), 1), "p": pval(result.get("p")),
                                                          t("Corrélation bisériale de rangs"): num(result.get("rank_biserial")),
                                                          "n1": result.get("n1"), "n2": result.get("n2")}]))
            effect(t("bisériale de rangs"), result.get("rank_biserial"), (.1, .3, .5))
        r.interpretation.insert(0, _decision(result.get("p"), "différence entre groupes"))
    elif method == "one_way":
        r.indicators += [Indicator("F", ltr(f"{_plain(result.get('F'))} ({result.get('df1')}, {result.get('df2')})")),
                         Indicator("p", pval(result.get("p"))), Indicator("η²", num(result.get("eta2")))]
        r.tables.append((t("ANOVA à un facteur"), [{"F": num(result.get("F")), "ddl1": result.get("df1"), "ddl2": result.get("df2"),
                                                    "p": pval(result.get("p")), "η²": num(result.get("eta2")), "n": result.get("n")}]))
        r.interpretation.append(_decision(result.get("p"), "différence entre groupes"))
        effect("η²", result.get("eta2"), (.01, .06, .14))
        r.interpretation.append(t("Ce test global n'indique pas quels groupes diffèrent."))
    elif method in ("regression", "moderation"):
        r.indicators += [Indicator("R²", num(result.get("r2"))), Indicator(t("R² ajusté"), num(result.get("adjusted_r2"))),
                         Indicator(t("Modèle") + " · p", pval(result.get("model_p")))]
        r.tables.append((t("Ajustement du modèle"), [{"R²": num(result.get("r2"), 3), t("R² ajusté"): num(result.get("adjusted_r2"), 3),
                                                      "F": num(result.get("model_F")), "ddl1": result.get("model_df1"),
                                                      "ddl2": result.get("df"), "p": pval(result.get("model_p")),
                                                      t("ET résiduel"): num(result.get("residual_sd")), "n": result.get("n")}]))
        r.tables.append((t("Coefficients"), [{t("Terme"): t(c.get("term", "")) if c.get("term") == "Intercept" else c.get("term", ""),
                                              "b": num(c.get("b"), 3), t("Erreur type"): num(c.get("se"), 3), "t": num(c.get("t")),
                                              "p": pval(c.get("p")), t("IC 95 %"): ci(c.get("ci95"), 3) or "–"}
                                             for c in result.get("coefficients", [])]))
        r.tables.append((t("Diagnostics"), [{t("Résidu standardisé maximal (valeur absolue)"): num(result.get("max_abs_scaled_residual")),
                                             t("Nombre de conditionnement"): num(result.get("condition_number"), 1)}]))
        share = result.get("r2")
        if share is not None:
            r.interpretation.append(t("Le modèle décrit {pct} % de la variation de la variable étudiée dans cet échantillon.",
                                      pct=num(100 * share, 1)))
        r.interpretation.append(_decision(result.get("model_p"), "association globale"))
        if method == "moderation" and result.get("coefficients"):
            inter = result["coefficients"][-1]
            r.indicators.append(Indicator("X × M · p", pval(inter.get("p"))))
            r.interpretation.append(t("Interaction X × M : ") + _decision(inter.get("p"), "modération"))
        if (result.get("max_abs_scaled_residual") or 0) > 3:
            r.interpretation.append(t("Au moins un résidu dépasse 3 écarts-types : vérifiez les valeurs influentes."))
    r.conditions = [t(c) for c in CONDITIONS.get(method, [])]
    r.limits = [t(x) for x in LIMITS.get(method, []) + LIMITS["default"]]
    return r


def investigate_payload(result: dict) -> str:
    """JSON complet du résultat, tel que calculé (pour l'export de reproductibilité)."""
    return json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)


def metadata(result: dict, method: str) -> list[tuple[str, str]]:
    import platform

    rows = [(t("Méthode"), method), (t("Moteur statistique"), "SciPy " + str(result.get("scipy_version", "–"))),
            ("Python", platform.python_version())]
    for key, label in (("instrument", "Instrument"), ("protocol", "Protocole"), ("group", "Groupe")):
        if result.get(key) is not None:
            rows.append((t(label), str(result[key])))
    return rows


# ---------------------------------------------------------------------------- graphiques

def chart(method: str, result: dict, *, panel_values=None, columns=None, participants=None, samples=None,
          group_labels=None, group_panels=None, matrix=None, unit: str = "", max_subjects: int = 100):
    """Graphique adapté à la méthode, ou None. Construit uniquement à partir des données analysées
    et des résultats calculés. À appeler dans ``chart_guard`` : une erreur graphique n'atteint ni
    les résultats ni les exports."""
    import altair as alt
    import pandas as pd

    value_axis = alt.Y("value:Q", title=t(unit) if unit else t("Valeur"), scale=alt.Scale(zero=False))
    if method in ("descriptive", "paired_t", "wilcoxon", "repeated_anova", "friedman", "paired_posthoc") and panel_values:
        cols = list(columns or [])
        shown = list(zip(participants or range(len(panel_values)), panel_values))[:max_subjects]
        records = [{"participant": str(p), "occasion": o, "value": float(v)} for p, row in shown for o, v in zip(cols, row)]
        means = pd.DataFrame([{"occasion": o, "value": mean(float(r[j]) for r in panel_values)} for j, o in enumerate(cols)])
        x = alt.X("occasion:N", sort=cols, title=t("Occasion"))
        if method == "descriptive":
            box = alt.Chart(pd.DataFrame(records)).mark_boxplot(size=36).encode(x=x, y=value_axis)
            return box + alt.Chart(means).mark_point(shape="diamond", size=90, filled=True, color="#dc2626").encode(x=x, y="value:Q")
        lines = alt.Chart(pd.DataFrame(records)).mark_line(opacity=.25, strokeWidth=1).encode(
            x=x, y=value_axis, detail="participant:N")
        average = alt.Chart(means).mark_line(point=alt.OverlayMarkDef(size=70), strokeWidth=3, color="#1552F8").encode(
            x=x, y="value:Q", tooltip=[alt.Tooltip("value:Q", format=".2f", title=t("Moyenne"))])
        return lines + average
    if method == "mixed_anova" and group_panels:
        cols = list(columns or [])
        rows = [{"group": g, "occasion": o, "value": mean(float(r[j]) for r in vals)}
                for g, vals in zip(group_labels or [], group_panels) if vals for j, o in enumerate(cols)]
        return alt.Chart(pd.DataFrame(rows)).mark_line(point=True, strokeWidth=3).encode(
            x=alt.X("occasion:N", sort=cols, title=t("Occasion")), y=alt.Y("value:Q", title=t("Moyenne"), scale=alt.Scale(zero=False)),
            color=alt.Color("group:N", title=t("Groupe")), tooltip=["group", "occasion", alt.Tooltip("value:Q", format=".2f")])
    if method in ("welch", "mann_whitney", "one_way") and samples:
        rows = [{"group": g, "value": float(v)} for g, vals in zip(group_labels or [], samples) for v in vals]
        frame = pd.DataFrame(rows)
        order = list(group_labels or [])
        box = alt.Chart(frame).mark_boxplot(size=40).encode(x=alt.X("group:N", title=t("Groupe"), sort=order), y=value_axis)
        dots = alt.Chart(frame).mark_circle(opacity=.35, size=22).encode(x=alt.X("group:N", sort=order), y="value:Q")
        return box + dots
    if method in ("pearson", "spearman") and (matrix is not None or panel_values):
        pairs = matrix if matrix is not None else panel_values
        frame = pd.DataFrame([{"x": float(a[0]), "y": float(a[1])} for a in pairs])
        names = list(columns or ["X", "Y"])
        return alt.Chart(frame).mark_circle(size=55, opacity=.7).encode(
            x=alt.X("x:Q", title=names[0], scale=alt.Scale(zero=False)),
            y=alt.Y("y:Q", title=names[1] if len(names) > 1 else "Y", scale=alt.Scale(zero=False)))
    if method in ("regression", "moderation") and matrix is not None and result.get("coefficients"):
        import numpy as np

        m = np.asarray(matrix, dtype=float)
        y, xs = m[:, 0], m[:, 1:]
        b = [c["b"] for c in result["coefficients"]]
        names = list(columns or [])
        if method == "moderation":
            centers = result.get("predictor_centers") or xs.mean(axis=0).tolist()
            xc = xs[:, 0] - centers[0]
            sd_m = float(np.std(xs[:, 1] - centers[1], ddof=1))
            grid = np.linspace(xc.min(), xc.max(), 20)
            rows = []
            levels = ((t("M bas (−1 ET)"), -sd_m), (t("M moyen"), 0.0), (t("M haut (+1 ET)"), sd_m))
            for name, level in levels:
                for g in grid:
                    rows.append({"x": float(g + centers[0]), "y": b[0] + b[1] * g + b[2] * level + b[3] * g * level, "M": name})
            points = alt.Chart(pd.DataFrame({"x": xs[:, 0], "y": y})).mark_circle(opacity=.3, size=25).encode(
                x=alt.X("x:Q", title=names[1] if len(names) > 1 else "X", scale=alt.Scale(zero=False)),
                y=alt.Y("y:Q", title=names[0] if names else "Y", scale=alt.Scale(zero=False)))
            lines = alt.Chart(pd.DataFrame(rows)).mark_line(strokeWidth=3).encode(
                x="x:Q", y="y:Q", color=alt.Color("M:N", title="M", sort=[n for n, _ in levels],
                                                  scale=alt.Scale(domain=[n for n, _ in levels],
                                                                  range=["#93c5fd", "#2563eb", "#1e3a8a"])))
            return points + lines
        fitted = b[0] + xs @ np.asarray(b[1:])
        if xs.shape[1] == 1:
            frame = pd.DataFrame({"x": xs[:, 0], "y": y})
            order = np.argsort(xs[:, 0])
            line = pd.DataFrame({"x": xs[order, 0], "y": fitted[order]})
            return (alt.Chart(frame).mark_circle(size=50, opacity=.6).encode(
                x=alt.X("x:Q", title=names[1] if len(names) > 1 else "X", scale=alt.Scale(zero=False)),
                y=alt.Y("y:Q", title=names[0] if names else "Y", scale=alt.Scale(zero=False)))
                + alt.Chart(line).mark_line(strokeWidth=3, color="#1552F8").encode(x="x:Q", y="y:Q"))
        frame = pd.DataFrame({"fitted": fitted, "observed": y})
        return alt.Chart(frame).mark_circle(size=50, opacity=.6).encode(
            x=alt.X("fitted:Q", title=t("Valeurs ajustées par le modèle"), scale=alt.Scale(zero=False)),
            y=alt.Y("observed:Q", title=t("Valeurs observées"), scale=alt.Scale(zero=False)))
    return None


# ---------------------------------------------------------------------------- affichage

def render(st, method: str, method_label: str, result: dict, *, export_key: str, file_name: str,
           chart_args: dict | None = None, panel_values=None, columns=None) -> None:
    """Affiche les trois niveaux. Le JSON n'apparaît que dans « Investiguer »."""
    from .lab_display import chart_guard

    content = build(method, result, panel_values=panel_values, columns=columns)
    # Deux indicateurs par ligne, y compris sur téléphone (Streamlit empile les colonnes sous 640 px).
    st.markdown("<style>div[class*='_understand'] [data-testid=stHorizontalBlock]{flex-wrap:nowrap!important;gap:.75rem!important}"
                "div[class*='_understand'] [data-testid=stColumn]{min-width:0!important;flex:1 1 0!important;width:auto!important}"
                "div[class*='_understand'] [data-testid=stMetricValue]{font-size:1.45rem!important}"
                "div[class*='_understand'] [data-testid=stMetricLabel] p{white-space:normal!important}</style>",
                unsafe_allow_html=True)
    with st.container(border=True, key=f"{export_key}_understand"):
        st.markdown("**" + t("Comprendre") + "** · " + method_label)
        cards = content.sample + content.indicators
        for start in range(0, len(cards), 2):
            cols = st.columns(2)
            for col, card in zip(cols, cards[start:start + 2]):
                col.metric(card.label, card.value, help=card.help)
        with chart_guard(st, current()):
            figure = chart(method, result, **(chart_args or {}))
            if figure is not None:
                st.altair_chart(figure, use_container_width=True)
        for line in content.interpretation:
            st.write(line)
        st.caption(t("Lecture prudente : ces résultats décrivent des données observées, sans établir de cause."))
    with st.expander(t("Analyser : tableaux statistiques et conditions")):
        for title, rows in content.tables:
            st.markdown("**" + title + "**")
            st.dataframe(rows, hide_index=True, use_container_width=True)
        st.markdown("**" + t("Conditions d'application") + "**")
        for line in content.conditions:
            st.write("• " + line)
        st.markdown("**" + t("Limites d'interprétation") + "**")
        for line in content.limits:
            st.write("• " + line)
    with st.expander(t("Investiguer : données complètes et reproductibilité")):
        st.dataframe([{t("Élément"): k, t("Valeur"): v} for k, v in metadata(result, method)], hide_index=True,
                     use_container_width=True)
        payload = investigate_payload(result)
        st.download_button(t("Exporter le résultat (JSON)"), payload, file_name, "application/json",
                           key=export_key, on_click="ignore")
        st.json(result, expanded=False)


__all__ = ["ALPHA", "Indicator", "Restitution", "build", "chart", "describe", "investigate_payload", "metadata",
           "num", "pval", "render", "colon"]
