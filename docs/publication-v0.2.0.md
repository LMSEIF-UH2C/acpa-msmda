# Préparation de la publication v0.2.0 (GitHub et Zenodo)

Document préparatoire. Rien n'est publié tant que le porteur du projet n'a pas donné son accord final.

## 1. Préconditions

1. PR #68 puis la PR de préparation de version fusionnées dans `main`.
2. Recette physique iPhone complétée sur le déploiement consolidé ([grille](recette-iphone-v0.2.0.md)), sans anomalie bloquante.
3. Sur le commit final de `main` : workflows Tests (3.12 et 3.14), Public web demo, Independent R validation et Mobile navigation réussis ; noter le nombre de tests affiché par la CI.
4. Révision déployée sur Streamlit Community Cloud identique au commit final.
5. Aucun tag `v0.2.0` ni release du même nom existants (vérifié le 25 novembre 2026 : seuls `v0.1.0`, `v0.1.1` et `v0.2.0-rc.1` existent).
6. `CITATION.cff` : ajouter `date-released` à la date du tag. Ne pas y inscrire de DOI avant attribution par Zenodo.

## 2. Création du tag et de la release (après accord)

```bash
git checkout main && git pull
git tag -a v0.2.0 -m "ACPA/MSMDA v0.2.0" <commit-final>
git push origin v0.2.0
```

Créer ensuite la release GitHub `v0.2.0` à partir de ce tag, non marquée « pre-release », avec le texte de la section 3.

## 3. Texte proposé pour la release GitHub

> **ACPA/MSMDA v0.2.0**
>
> Trilingual (French, Arabic, English) research demonstrator for EPS technology evaluation, contextual recommendation, pedagogical scenario design, teaching support and a field Laboratory, designed for Moroccan teaching contexts.
>
> Highlights since v0.2.0-rc.1: Laboratory with 32 field instruments, common statistics and repeated measures checked against R 4.5.2 (29/29 metrics), three-level restitution (Understand, Analyse, Investigate), optional visual cues; teacher Excel backups that can be restored; Safari Arabic dictation; mobile navigation fixes; Python 3.14 compatibility.
>
> Verification: <N> automated tests on the release commit (Python 3.12 and 3.14), independent R comparison, mobile navigation workflow, physical iPhone acceptance run. Details: `docs/release-v0.2.0.md`, `CHANGELOG.md`, `docs/validation/`.
>
> Scientific status: this public implementation is distinct from the doctoral prototype evaluated in the associated research; the prototype's empirical results do not apply to it (`docs/statut-scientifique-v0.2.0.md`).
>
> Limits: software stability is not empirical validation of the instruments, evidence of educational efficacy or institutional production readiness. Teacher data is temporary on the server and must be saved as Excel. Illustrations are AI-generated and non-normative.
>
> Licences: code MIT; Laboratory illustrations CC BY 4.0 to the extent of the rights held; OpenMoji pictograms CC BY-SA 4.0; fonts under SIL OFL and their own licences. OMPIC patent application No. 74877 (23 April 2026), not granted; no patent licence is granted.
>
> Cite this version with its own DOI once assigned. The v0.1.1 DOI (10.5281/zenodo.23244629) refers only to the archived engine.

`<N>` est à remplacer par le nombre affiché par la CI du commit final (262 sur `96ad264`).

## 4. Métadonnées Zenodo proposées

Si l'intégration GitHub et Zenodo est active, la release crée automatiquement un dépôt avec un DOI propre à v0.2.0 ; il n'est rattaché au même concept que v0.1.1 que si v0.1.1 a été archivée par la même intégration (point non vérifié ici). Sinon, créer le dépôt à la main comme nouvelle version de l'enregistrement v0.1.1. Vérifier les champs avant validation du dépôt.

| Champ | Valeur proposée |
|---|---|
| Type | Software |
| Titre | ACPA/MSMDA: EPS Technology Evaluation and Teaching Assistant |
| Version | v0.2.0 |
| Créateurs | Moudettir, Youness ; Ouhrir, Siham ; Lotfi, Said (ordre et graphie confirmés par le porteur le 25 novembre 2026 ; repris de `CITATION.cff`) |
| Affiliations | LMSEIF, École Normale Supérieure de Casablanca, Hassan II University of Casablanca (les trois auteurs ; rattachement au LMSEIF confirmé par le porteur) |
| ORCID | Moudettir 0000-0002-6793-740X ; Ouhrir 0000-0001-9870-5655 ; Lotfi 0000-0002-0008-6145 |
| Licence | MIT (code) ; préciser dans la description les licences CC BY 4.0 et CC BY-SA 4.0 des ressources visuelles |
| Mots-clés | physical education; educational technology; Morocco; context-aware recommendation; field testing; trilingual interface |
| Description | Texte de la section 3, sans le passage sur la citation |
| Identifiant lié | `isSupplementTo` le dépôt GitHub ; `isNewVersionOf` 10.5281/zenodo.23244629 |
| Note | Demande de brevet OMPIC n° 74877 (23 avril 2026), non accordée |

Après attribution : ajouter le DOI v0.2.0 au README et à `CITATION.cff` dans une PR distincte, sans modifier les mentions de v0.1.1.

## 5. Traçabilité des contributions

- Porteur du projet : conception scientifique et pédagogique, choix des instruments, sélection des illustrations, arbitrages et validation de chaque fusion.
- Assistants d'IA (ChatGPT et Claude) : contributions de code, de documentation, d'audit et de recette, proposées dans des pull requests relues et fusionnées par le porteur. Leur attribution par PR est conservée dans l'historique GitHub et dans `docs/validation/`.
- Ressources tierces : OpenMoji (pictogrammes), IBM Plex Sans Arabic et Amiri (polices), DejaVu.

Les commits sont signés au nom du dépôt ; ne pas inférer l'auteur d'une contribution à partir du seul compte GitHub (voir `docs/validation/README.md`).
