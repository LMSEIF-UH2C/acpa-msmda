# Laboratoire EPS — périmètre pré-soutenance

## Périmètre
32 instruments de saisie et 83 pistes documentaires complémentaires. La bibliothèque ne constitue pas une liste de 115 tests indépendants et validés. Aucun ajout de variantes rares avant la soutenance. Les méthodes statistiques usuelles, y compris expérimentales, restent au périmètre.

## Données
CSV UTF-8 ou XLSX à une seule feuille, colonnes participant;group;instrument;unit;occasion;date;protocol;value. Dates ISO en texte, sans formules. Codes non nominatifs, correspondance conservée hors application. Une valeur vide reste manquante. Les données sont conservées en session, export nécessaire avant fermeture. Les codes doivent être uniques à travers les groupes d'une étude.

## Analyses
Cas complets, appariement explicite par participant. Le dénominateur éligible est l'union des observations des variables/occasions sélectionnées, pas un registre de recrutement. Les groupes ne sont pas des unités de randomisation automatiquement modélisées. Les tests supposent l'indépendance des participants; les classes ou établissements peuvent induire une dépendance. Ne pas utiliser les p-values naïves pour un essai randomisé en grappes sans méthode adaptée.

- Descriptives, ICC/SEM/MDC, Bland-Altman : parcours pédagogique existant.
- Pearson/Spearman, t apparié, Wilcoxon : deux occasions ou deux variables sélectionnées selon méthode.
- Welch/Mann-Whitney : deux groupes, une occasion. ANOVA classique : plusieurs groupes, une occasion.
- ANOVA répétée et Friedman : au moins trois occasions; correction Greenhouse-Geisser disponible pour ANOVA.
- ANOVA mixte : groupes de même effectif complet, au moins trois participants par groupe, au moins deux occasions, covariance commune supposée. Effets groupe, temps, interaction; pas de modèle mixte à effets aléatoires.
- Post-hoc : t appariés, Holm sur la famille des contrastes sélectionnés; IC individuels non simultanés.
- OLS : une variable dépendante, prédicteurs quantitatifs, erreurs classiques; modération : deux prédicteurs centrés et interaction. Pas de causalité déduite.
- Les conditions d'application déclarées par l'utilisateur ne constituent pas un diagnostic statistique automatique.

## Contrôles et limites
La révision 0ae44bc0 a réussi les deux workflows et 205 tests unitaires selon le journal 45451392880. Les révisions suivantes nécessitent leurs propres validations. Le succès CI ne constitue ni validation empirique des instruments, ni validation indépendante complète des méthodes. Les références génériques sont des pistes à vérifier. L'annexe institutionnelle originale, la recette mobile réelle, les illustrations et la comparaison indépendante R/jamovi restent à documenter avant gel définitif.

## Références méthodologiques
- https://docs.scipy.org/doc/scipy/reference/stats.html
- https://stat.ethz.ch/R-manual/R-devel/library/stats/html/00Index.html
- https://docs.jamovi.org/
- https://doi.org/10.3389/fpsyg.2013.00863

## Recette avant publication
- [ ] Vérifier chaque protocole prioritaire contre la source originale.
- [ ] Vérifier les illustrations et unités, sans inférer une norme.
- [ ] Exécuter les parcours import, appariement, groupes, régression et export sur données synthétiques.
- [ ] Comparer F, p, coefficients, IC et corrections à une implémentation indépendante.
- [ ] Vérifier les trois langues et les écrans mobiles réels.
- [ ] Vérifier CI sur le commit final et après fusion.
- [ ] Publier uniquement la version réellement validée; distinguer code, implémentation et résultats empiriques.
