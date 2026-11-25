# ACPA/MSMDA v0.2.0 : notes de version

Statut au 25 novembre 2026 : code consolidé et vérifié, en attente de la recette physique iPhone et de l'accord final du porteur du projet. Aucun tag stable ni DOI n'est attribué à ce stade. Le DOI de v0.1.1 (`10.5281/zenodo.23244629`) ne doit pas être réutilisé.

## Révision de référence

Révision consolidée : `96ad264` (PR #68 réconciliée avec `main` après les PR #70 à #74). Le tag sera posé sur le commit de `main` résultant de la fusion finale, après vérification que la CI y est verte.

| Contrôle | Résultat sur 96ad264 |
|---|---|
| Tests automatisés, Python 3.12 et 3.14 | 262 tests, OK |
| Démonstration web publique | 262 tests, OK |
| Comparaison indépendante avec R 4.5.2 | 29/29 métriques |
| Navigation mobile et dictée simulée | succès |
| Balayage 10 pages × FR/AR/EN × ordinateur/iPhone (Chromium) | 60/60 |

Détail : [recette de clôture](validation/recette-cloture-v0.2.0-2026-11-25/README.md). Les jalons antérieurs (188, 205, 211 tests) sont des états successifs de la suite : ils ne s'additionnent pas. Historique : [registre des validations](validation/README.md).

## Périmètre

- Évaluer, Explorer, Scénario : technothèque réelle (entrées documentées et non vérifiées), recherche contextualisée, évaluation sur 18 critères, Studio pédagogique.
- Espace EPS : ateliers, outils de terrain, évaluation formative, cahier journalier annuel avec projets de classe, planification des cycles adaptée à l'emploi du temps marocain.
- Laboratoire : 32 instruments de saisie, 83 pistes documentaires (pas toutes des tests distincts ni validés), suivi longitudinal, statistiques usuelles et mesures répétées, méthodes de fiabilité, restitution en trois niveaux (Comprendre, Analyser, Investiguer), repères visuels facultatifs.
- Sauvegardes enseignant en classeurs Excel restaurables ; JSON réservé au niveau Investiguer et aux usages techniques.
- Interface FR/AR/EN avec RTL, dictée vocale (Safari compris), exports PDF avec police arabe locale.

## Apports depuis v0.2.0-rc.1

Le tag `v0.2.0-rc.1` pointe sur `2da291a` (24 novembre 2026). Les PR fusionnées depuis (#50 à #58, #60 à #66, #70 à #74) et la PR #68 sont résumées dans le [CHANGELOG](../CHANGELOG.md).

## Statut scientifique

L'application publique v0.2.0 est distincte du prototype doctoral évalué ; les résultats empiriques de ce prototype ne lui sont pas transposables. La formule de score a été adaptée aux critères non renseignés, sans modification du moteur pendant la clôture. Le répertoire de 2 466 applications provient d'une cartographie de 45 676 enregistrements identifiés (40 759 après dédoublonnage). Détail, tableau des composantes et formulations à employer : [statut scientifique de v0.2.0](statut-scientifique-v0.2.0.md).

## Limites connues, non bloquantes

- Notes du répertoire : 2 354 fiches sur 2 466 sont notées par estimation à partir de la description de l'éditeur ; l'indice affiché est heuristique.

- Stabilité logicielle n'est pas validation empirique : ni efficacité pédagogique, ni validation scientifique des instruments, ni conformité réglementaire, ni aptitude à une production institutionnelle.
- Données temporaires côté serveur ; sauvegarder en Excel avant de fermer. Utiliser des données fictives sur le service public.
- Dictée vocale : la CI simule le micro ; seul l'essai physique iPhone confirme le comportement réel.
- Illustrations : générées par IA (outil non précisé dans la remise), non normatives ; souplesse assise avec élève chaussé ; sprint 30 m avec nuance de chronométrage en légende ; ressources Wikimedia non intégrées.
- Certains libellés internes de Streamlit restent en anglais (N2) ; le badge Streamlit Community Cloud peut recouvrir la barre d'onglets sur iPhone (N5, hors code de l'application).
- Paramètre `use_container_width` encore utilisé dans du code antérieur : sans effet sous Streamlit 1.52.0 épinglé, à remplacer avant toute montée de version.
- La circulaire 2358/25 est repérée dans la documentation de travail ([audit des références](LAB_REFERENCE_AUDIT.md)) mais son contenu n'a pas été inspecté ; le rattachement des onze instruments institutionnels reste provisoire. Elle n'est pas citée dans l'application.
- Compagnons hors ligne et vidéo : expérimentaux, non intégrés au service hébergé.

## Propriété industrielle

Demande de brevet OMPIC n° 74877, 23 avril 2026, non accordée. La licence MIT du code ne comporte pas de concession de brevet. Voir `NOTICE`.

## Conditions de publication

Dossier de livraison : [livraison-v0.2.0.md](livraison-v0.2.0.md). Voir aussi [checklist](release-checklist.md), [recette iPhone](recette-iphone-v0.2.0.md) et [préparation GitHub et Zenodo](publication-v0.2.0.md).
