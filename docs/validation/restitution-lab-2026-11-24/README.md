# Restitution des analyses du Laboratoire EPS en trois niveaux : 24 novembre 2026

Correction ergonomique pré-livraison. Constat de la recette sur iPhone du porteur du projet : les analyses, les
graphiques et les exports fonctionnent, mais le résultat s'affichait en JSON brut, ce qui fait obstacle pour les
enseignants. Rôles : porteur du projet (constat, décision), assistant de développement (correction, tests, preuves).

## Ce qui change

Après le calcul, le résultat apparaît en trois niveaux :

1. **Comprendre** (affiché par défaut, dans un cadre) :
   - participants analysés et exclus (données manquantes) ;
   - indicateurs essentiels, deux par ligne y compris sur téléphone ;
   - graphique adapté à la méthode ;
   - interprétation prudente.
2. **Analyser** (volet replié) :
   - tableaux structurés : statistique, ddl, p, IC 95 % et taille d'effet quand le moteur les fournit ;
   - statistiques descriptives ;
   - conditions d'application propres à la méthode et limites d'interprétation.
3. **Investiguer** (volet replié) :
   - métadonnées (méthode, versions de SciPy et de Python, instrument, protocole, groupe) ;
   - export JSON, inchangé ;
   - JSON complet.

| Méthode | Graphique « Comprendre » | Indicateurs |
|---|---|---|
| Descriptif | Boîtes à moustaches par occasion, moyenne marquée | Écart des moyennes ; tableau descriptif |
| Pearson, Spearman | Nuage de points | r ou ρ, p, IC 95 % (Pearson seulement, car seul fourni) |
| t apparié, Wilcoxon | Trajectoires individuelles et moyenne avant-après | Différence moyenne, p, dz, IC 95 % (t) ; W, p (Wilcoxon, sans taille d'effet) |
| ANOVA répétée, Friedman | Évolution des moyennes et trajectoires | F (ddl), p corrigé GG si calculé, η²p ; χ², p, W de Kendall |
| ANOVA mixte | Évolution comparée des moyennes par groupe | Interaction groupe × temps : p, η²p ; tableau des trois effets |
| Post-hoc (Holm) | Évolution des moyennes ; tableau des comparaisons | Comparaisons significatives après Holm |
| Welch, Mann-Whitney, ANOVA à un facteur | Boîtes à moustaches par groupe et points | Différence moyenne, p, IC 95 % ; U, p, bisériale de rangs ; F, p, η² |
| Régression | Droite ajustée (1 prédicteur) ou observé / ajusté | R², R² ajusté, p du modèle ; coefficients, IC, diagnostics |
| Modération | Droites simples à M − 1 ET, moyenne, + 1 ET | R², p du modèle, p de l'interaction X × M |

Bland-Altman et ICC étaient déjà restitués sans JSON dans le bilan test-retest : non modifiés.

## Garanties

- **Calculs :** `lab_statistics.py`, `longitudinal.py` et `requirements.txt` ne sont pas modifiés. Le nouveau module `lab_results.py` lit les résultats sans les changer ; un test le vérifie pour 13 méthodes.
- **Ajouts calculés dans `lab_results.py` :** seulement les statistiques descriptives des données affichées et les droites tracées à partir des coefficients calculés. Aucun IC ni aucune taille d'effet n'est ajouté quand le moteur n'en fournit pas ; un test le vérifie pour Spearman, Wilcoxon, Mann-Whitney et Friedman.
- **Interprétation :**
  - seuil de 5 % présenté comme une convention ;
  - un résultat non significatif « ne prouve pas l'absence » d'effet ;
  - repères usuels pour la taille d'effet (Cohen) ;
  - formulation descriptive, jamais causale (test sur une liste de verbes causaux).
- **Échec graphique :** le graphique reste dans `chart_guard` (correctif REC-Y001, PR #64) ; les indicateurs, tableaux et l'export restent affichés, ce qu'un test vérifie.
- **Langues :**
  - FR, AR et EN ;
  - virgule décimale en français ;
  - en arabe, les nombres et expressions (« p < 0.001 », « [0.17, 1.33] », « 16.51 (2, 46) ») sont isolés pour garder leur ordre ;
  - 125 textes ajoutés à `data/translations.json`.
- **Exports :** clés et noms de fichiers inchangés (`lab_study_analysis_export`, `lab_mv_download`), avec `on_click="ignore"`.

## Tests et preuves

| # | Test | Résultat |
|---|---|---|
| L1 | `tests/test_lab_results.py` : 9 cas (contenu des trois niveaux, résultats non modifiés, absence d'IC ou de taille d'effet inventés, valeurs identiques au moteur, formulation prudente, conditions propres à chaque méthode, trois langues, graphique pour chaque méthode, page sans JSON par défaut, échec graphique isolé) | Réussi |
| L2 | Suite complète en Python 3.12 (versions exactes) et contrôle de mutation | 223 tests réussis (branche issue de `main` à f7044f4, sans la PR #65) |
| L3 | Banc visuel iPhone 13 simulé : 6 méthodes × 3 langues (`scripts/banc_restitution.py`) | 18/18 sans exception ni débordement horizontal (`captures/methodes_iphone.jpg`) |
| L4 | Page réelle sur iPhone simulé : import de 2 880 observations synthétiques, groupe TC1, T1-T2, t apparié | FR et AR : carte « Comprendre » affichée, JSON masqué par défaut, aucune exception (`captures/page_reelle_t_apparie_*.jpg`, `scripts/parcours_lab_reel.py`) |
| L5 | Intégration continue de la PR #66 : tests Python 3.12 et 3.14, démonstration publique, validation indépendante avec R | Tout réussi : https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45511840505 (tests) et https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/45511840464 (R) |

## Limites

- La restitution AppTest en arabe n'est pas automatisée (les libellés traduits des listes ne sont pas pris en charge par AppTest) : elle est couverte par les tests de contenu et le parcours réel L4.
- Les textes intégrés de Streamlit (zone de dépôt de fichier) restent en anglais.

## Corrections après audit indépendant (25 novembre 2026)

L'audit de la PR #66 a confirmé la conformité générale et la préservation du moteur. Il a demandé douze corrections ciblées avant la fusion. `lab_statistics.py`, `longitudinal.py` et `requirements.txt` restent inchangés.

| # | Demande | Correction | Test |
|---|---|---|---|
| 1 | Corrélation exactement nulle | Coefficient nul : phrase neutre (« aucune tendance commune »), jamais « négative » | `test_zero_correlation_is_not_negative` |
| 2 | Distributions descriptives | Boîtes calculées sur tous les cas complets (quartiles, minimum–maximum, moyenne) puis tracées ; plus de mélange entre 100 participants affichés et une moyenne sur l'ensemble ; légende explicite | `test_descriptive_boxes_use_all_complete_cases` |
| 3 | Arrondi de p autour de 0,05 | Décimales ajoutées tant que l'arrondi donnerait 0,050 pour p ≠ 0,05 (p = 0,04996 et non 0,050) ; même règle dans les phrases | `test_p_rounding_stays_on_the_right_side` |
| 4 | IC post-hoc | Colonne « IC 95 % non corrigé » ; limite : seules les p sont corrigées par Holm | `test_posthoc_and_friedman_notes` |
| 5 | t appariés après Friedman | Condition ajoutée : différences approximativement normales pour chaque paire, aucune alternative non paramétrique calculée | `test_posthoc_and_friedman_notes` |
| 6 | Protections de volume (PR #62) | Trajectoires par `trajectory_records` (100 participants, 5 000 lignes au plus) ; nuages limités à 5 000 points ; chaque limitation est signalée sous le graphique | `test_display_limits_are_reported` |
| 7 | Ordre d'affichage | Carte « Comprendre » d'abord ; tableau des participants ensuite, dans un volet replié après calcul | `test_no_raw_json_by_default` (ordre des volets) |
| 8 | Libellés explicites | « Force de la relation (r) », « Taille d'effet (dz) », « Proportion de variance expliquée (R²) », « Probabilité (p) », « Statistique F (ddl) », « Concordance de Kendall (W) »… | `test_values_match_engine_for_each_method` |
| 9 | Avertissements et rôles des variables | Avertissement avant calcul tiré des conditions de la méthode choisie ; sélecteurs « Première / Seconde variable » (corrélation), « Variable expliquée (Y) / Variables explicatives (X) » (régression), « Prédicteur X puis modérateur M » (modération) | `test_precheck_and_labels_follow_method` |
| 10 | Tests ciblés | 7 tests de cas limites et de correspondance des valeurs pour 10 méthodes | 16 cas dans `tests/test_lab_results.py` |
| 11 | Preuves et workflows | Captures mises à jour (`captures/corrections_audit_iphone.jpg`, `captures/page_reelle_t_apparie_*.jpg`) ; suite locale : 230 tests réussis (Python 3.12) ; workflows 3.12, 3.14 et R relancés sur la PR | voir ci-dessous |
| 12 | Description de la PR | Mention automatique retirée de la description | — |

Recette après correction :
- banc visuel iPhone : 8 méthodes × 3 langues, sans exception ni débordement horizontal ;
- page réelle (2 880 observations, t apparié) en FR et en AR : carte « Comprendre » affichée, JSON masqué, aucune exception.
