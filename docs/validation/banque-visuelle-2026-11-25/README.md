# Banque visuelle du Laboratoire : intégration des 14 illustrations, 25 novembre 2026

Branche `lab/visual-integration` (PR #68, qui reprend la PR #67 et remplace la PR #59). Rôles : porteur du projet
(acceptation des images, décisions ouvertes ci-dessous), assistant de développement (contrôle, intégration, tests,
preuves). Gel fonctionnel respecté : moteur statistique, registre des 32 tests, calculs, exports et navigation
inchangés. Aucune publication stable ni archivage Zenodo.

## 1. Réception de la remise

| Élément | Constat |
|---|---|
| Archive | `ACPA_MSMDA_banque_visuelle_14.zip`, 1 915 266 octets, SHA-256 `9d7a56fbb39b18ccedd18115a2885f8c6db12b06694a8cc75091b8de15447d7c`, reçue le 25 novembre 2026 depuis l'espace partagé du projet |
| Contenu | 14 JPEG dans `assets/lab/`, `manifest.json`, `README.md` ; aucun chemin absolu ni remontée de dossier ; extraction dans un dossier isolé |
| Intégrité | 14/14 empreintes SHA-256 et tailles conformes au manifeste de remise |
| Format | JPEG RVB progressif, sans EXIF ; de 383 × 522 à 1400 × 1050 px ; de 35 841 à 294 572 octets, tous sous 500 000 |
| Retouche | Aucune : fichiers déposés tels que remis, sans réencodage |
| Exclusions | Pas d'illustration de handgrip (test conservé, pictogramme de famille) ; aucune planche de 32 tests |

Le README et le manifeste de remise sont conservés sans modification dans [remise/](remise/).

## 2. Inspection visuelle des 14 images

Chaque image a été comparée à la fiche du registre (`data/performance_tests.json`) et à la note de remise.

| Épreuve | Contenu observé | Écart ou point à décider |
|---|---|---|
| Navette Léger 20 m | Groupe en course entre deux lignes balisées, enseignant avec porte-bloc, enceinte | Distance non vérifiable sur l'image (note de remise) |
| Sprint 30 m | Départ individuel en couloir, groupe en attente, enseignant avec chronomètre sur le côté | Le chronométreur se tient au niveau du départ ; sa position reste à fixer dans le protocole (registre : chronométrage à standardiser) |
| Saut horizontal | Pieds joints sans élan, trois phases, ruban depuis la ligne | Modalité d'élan à confirmer (registre) |
| Saut vertical Sargent | Marque debout, marque au sommet du saut, flèche d'écart ; flexion préparatoire à droite | Lecture gauche-droite non chronologique : précisé dans le texte alternatif |
| Médecine-ball 3 kg | Assis dos au mur, jambes tendues, trois phases, ruban depuis le mur | Conforme à « position assise dos au mur » |
| Souplesse assise | Élève chaussé, pieds contre une boîte graduée à curseur | Les protocoles courants de sit-and-reach se passent sans chaussures ; convention du zéro à vérifier |
| Souplesse debout | Pieds nus sur support stable, règle graduée verticale | Zéro et signe à préciser (registre) |
| Flamingo | Équilibre sur une poutre basse, pied tenu, enseignant avec chronomètre | Dimensions de la poutre et décompte à confirmer |
| Taille, poids | Pieds nus, toise, balance ; aucune mise en scène de jugement corporel | Conforme |
| FC de repos | Pouls radial au poignet, élève assis, chronomètre | Conforme |
| Ruffier-Dickson | Cinq vignettes : P1, 30 flexions en 45 s, P2, récupération 1 min, P3 ; légendes françaises incrustées | P1 et P3 sont dessinés assis ; selon les sources, ces prises se font assis ou allongé ; position et durée de comptage à fixer dans le protocole retenu |
| Killy | Dos au mur, cuisses horizontales, bras croisés, enseignante avec chronomètre, sans drapeau | Conforme à la version acceptée |
| Gainage ventral | Avant-bras et pointe des pieds, tapis, chronomètre posé au sol | Le chronomètre dessiné n'indique pas une durée |

Observation transversale : la plupart des images montrent des logos de type « virgule » sur les chaussures et
« trois bandes » sur les survêtements, qui rappellent des marques d'équipement sportif. Décision à prendre avant la
publication stable : accepter, retoucher ou régénérer.

## 3. Intégration

- `assets/lab/<id>.jpg` : 14 fichiers, aucun autre fichier dans ce dossier.
- `assets/visual-bank/manifest.json` : bloc `lab_delivery` (archive, empreinte, date, absence de retouche) et, pour
  chaque image, chemin, dimensions, taille, SHA-256, statut, note de remise et texte alternatif.
- `src/acpa_msmda/visual_bank.py` : sous l'image, texte alternatif puis avertissement non normatif. Le volet
  « Illustration pédagogique » reste replié par défaut ; une image absente ne bloque jamais la page.
- Texte alternatif : ce que montre l'image, puis « Matériel représenté ». Il décrit l'image et ne constitue pas la
  liste du matériel requis : une telle liste dépend du protocole retenu (circulaire 2358/25 et annexe encore à
  vérifier, selon la note de remise). Pour Ruffier, il reproduit les cinq légendes en français, en arabe et en anglais.
- `data/translations.json` : 14 textes traduits en arabe et en anglais. Contrôle `tools/i18n_strings.py` :
  1 062 textes requis, aucun manquant.
- `NOTICE` : licence CC BY-SA 4.0 des pictogrammes OpenMoji ; licence de réutilisation des illustrations IA non
  encore arrêtée.

## 4. Tests automatisés

`tests/test_lab_illustrations.py`, 16 tests :
- couverture des 32 tests (14 illustrations et 18 pictogrammes, handgrip conservé) ;
- licences et sécurité des SVG ;
- présence, format et poids des 14 JPEG ;
- provenance : empreinte, taille et dimensions identiques à la remise, preuve de remise conservée, aucun fichier
  parasite ;
- textes alternatifs traduits, sans tiret cadratin ; légendes de Ruffier dans les trois langues ;
- page du Laboratoire en français, arabe et anglais ; une image manquante ne bloque pas la page.

Suite complète en local (Python 3.12.3, dépendances exactes) : 250 tests réussis. `compileall` et
`scripts/mutation_check.py` réussis. Les workflows de la PR (Python 3.12 et 3.14, smoke, validation R) font foi.

## 5. Recette mobile

iPhone 13 émulé (Chromium sans interface, Playwright), application servie localement depuis la branche. Script :
[scripts/recette_banque_visuelle.py](scripts/recette_banque_visuelle.py). Résultats bruts :
[resultats/recette_iphone.json](resultats/recette_iphone.json). Planche :
[captures/banque_visuelle_iphone.jpg](captures/banque_visuelle_iphone.jpg).

| Cas | Image | Largeur affichée / fenêtre | Débordement horizontal | Sens des légendes | Exceptions, erreurs JS | Requêtes externes |
|---|---|---|---|---|---|---|
| fr / Sargent | chargée | 326 / 390 px | non | ltr | 0, 0 | aucune |
| ar / Ruffier | chargée | 326 / 390 px | non | rtl | 0, 0 | aucune |
| en / médecine-ball | chargée | 326 / 390 px | non | ltr | 0, 0 | aucune |
| ar / souplesse assise | chargée | 326 / 390 px | non | rtl | 0, 0 | aucune |
| en / Killy | chargée | 326 / 390 px | non | ltr | 0, 0 | aucune |
| fr / handgrip (pictogramme) | chargé, 56 px, SVG intégré à la page | sans objet | non | ltr | 0, 0 | aucune |

Dans les six cas, le volet est replié à l'ouverture de la page. Sur téléphone, les légendes incrustées dans l'image de
Ruffier sont trop petites pour être lues : le texte alternatif les reproduit dans la langue de l'interface. Limite :
émulation, pas un appareil réel ; la recette sur iPhone du porteur du projet reste à faire après fusion.

## 6. Points ouverts, à décider par le porteur du projet

1. Licence de réutilisation des 14 illustrations IA, avant publication stable.
2. Logos de marques sur les tenues et les chaussures.
3. Ruffier : position des prises P1 et P3 (assis ou allongé) et durée de comptage du pouls.
4. Souplesse assise : épreuve avec ou sans chaussures.
5. Sprint 30 m : position du chronométreur.
6. Références Wikimedia (fonds de terrain) : absentes de la remise ; le téléchargement depuis l'environnement
   d'intégration est refusé (HTTP 429). Elles ne sont pas intégrées.
7. Circulaire 2358/25 et son annexe : toujours à vérifier avant toute mention de conformité institutionnelle.

## Reproduire

```bash
python -m unittest tests.test_lab_illustrations -v
python tools/i18n_strings.py --missing
python -m streamlit run app.py --server.port 8599 --server.headless true
python docs/validation/banque-visuelle-2026-11-25/scripts/recette_banque_visuelle.py /tmp/recette_banque http://localhost:8599
```

`scripts/integrer_banque14.py` a produit le manifeste et les traductions à partir du manifeste de remise ; une
nouvelle exécution donne le même résultat.
