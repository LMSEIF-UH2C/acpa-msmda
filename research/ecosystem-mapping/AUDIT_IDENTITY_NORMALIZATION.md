# Audit du pilote de normalisation V0.1 — 28 novembre 2026
[Exécution 46133860479](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46133860479), job 140944723789 : succès, 8/8 tests unitaires. 4 archives existantes traitées sans requête aux boutiques; 9 237 identifiants de source (Apple 3 709, F-Droid 5 057, GitHub 471 dépôts), 12 524 observations/entrées de sources hétérogènes (1 563 + 5 424 + 5 057 + 480), non assimilables à des produits uniques.
669 paires candidates: 656 intrasources, 13 intersources. 192 signal nom, 483 signal URL de dépôt, dont 6 avec les deux; aucun signal de chaîne d'identifiant technique commune dans ce pilote. 230 IDs Apple et 684 IDs F-Droid avec plusieurs noms observés; cela peut refléter des variantes linguistiques, des changements d'appellation ou des métadonnées divergentes. Un groupe de 63 identifiants sur URL de dépôt a été différé (seuil exploratoire >30); 1953 paires possibles dans ce groupe, pas 1953 liens réels ni paires nécessairement absentes de tous les autres signaux. Ne pas fusionner ce groupe. 0 rapprochement automatique de produits, nombre de produits confirmés non déterminé.
| Paire source | Signal | Paires |
|---|---|---:|
| Apple–F-Droid | nom | 3 |
| Apple–GitHub | nom | 2 |
| F-Droid–GitHub | nom | 5 |
| F-Droid–GitHub | nom + dépôt | 2 |
| F-Droid–GitHub | dépôt | 1 |
| Apple–Apple | nom | 15 |
| F-Droid–F-Droid | nom | 67 |
| F-Droid–F-Droid | nom + dépôt | 4 |
| F-Droid–F-Droid | dépôt | 476 |
| GitHub–GitHub | nom | 94 |

Artefact 15258718327 ([téléchargement GitHub](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46133860479/artifacts/15258718327)), 3 fichiers, 3991 octets, SHA256 c500826a46398420400aa32066ee0ffdefde3c073ab5b15f8dbf36b9382000b0 recalculé dans le runtime, CRC ZIP valides. Deux CSV strictement identiques, 57 review_id uniques et décisions vierges; les 13 paires intersources ont toutes été tirées, plus 44 intrasources (max10 par strate). Ce contrôle du fichier d'échantillonnage ne constitue pas un audit indépendant de chaque paire. Absence de jugements humains; pas de précision, rappel ni kappa calculables. Le flag fork est faux/non observé pour les dépôts du pilote selon rapport; ne pas conclure à l'absence de forks fonctionnels.
Faiblesses : génération de candidats limitée au nom normalisé, identifiant technique exact, URL GitHub exacte; traduction/renommage, homonymie, suites, liens non indexés peuvent être manqués. Le partage d'un dépôt n'est pas une preuve d'identité. Les noms courts et groupes larges différés requièrent contrôle spécifique. Les 13 paires intersources ne mesurent pas la couverture réelle des variantes multiplateformes. Aucun rapprochement aux archives brutes historiques de 45 676.
Suite : [codebook de relations](IDENTITY_REVIEW_CODEBOOK.md), deux évaluateurs distincts et jeu de contrôle hors candidats; récupérer les historiques et qualifier les paramètres 10D/97P en parallèle. Le catalogue publié reste intact.
