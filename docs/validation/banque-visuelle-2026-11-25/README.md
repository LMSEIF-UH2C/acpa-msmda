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
| Retouche | À la réception, aucune : fichiers déposés tels que remis. Six images ont ensuite été retouchées sur décision du porteur du projet (section 7) |
| Exclusions | Pas d'illustration de handgrip (test conservé, pictogramme de famille) ; aucune planche de 32 tests |

Le README et le manifeste de remise sont conservés sans modification dans [remise/](remise/).

## 2. Inspection visuelle des 14 images

Chaque image a été comparée à la fiche du registre (`data/performance_tests.json`) et à la note de remise.

| Épreuve | Contenu observé | Écart ou point à décider |
|---|---|---|
| Navette Léger 20 m | Groupe en course entre deux lignes balisées, enseignant avec porte-bloc, enceinte | Distance non vérifiable sur l'image (note de remise) |
| Sprint 30 m | Départ individuel en couloir, groupe en attente, enseignant avec chronomètre sur le côté | Le chronométreur se tient au niveau du départ, alors que les références consultées le placent à l'arrivée ou en retrait ; image conservée, nuance ajoutée à la légende (section 7) |
| Saut horizontal | Pieds joints sans élan, trois phases, ruban depuis la ligne | Modalité d'élan à confirmer (registre) |
| Saut vertical Sargent | Marque debout, marque au sommet du saut, flèche d'écart ; flexion préparatoire à droite | Lecture gauche-droite non chronologique : précisé dans le texte alternatif |
| Médecine-ball 3 kg | Assis dos au mur, jambes tendues, trois phases, ruban depuis le mur | Conforme à « position assise dos au mur » |
| Souplesse assise | Élève chaussé, pieds contre une boîte graduée à curseur | Les protocoles courants de sit-and-reach se passent sans chaussures ; image non modifiée à ce stade (section 7) ; convention du zéro à vérifier |
| Souplesse debout | Pieds nus sur support stable, règle graduée verticale | Zéro et signe à préciser (registre) |
| Flamingo | Équilibre sur une poutre basse, pied tenu, enseignant avec chronomètre | Dimensions de la poutre et décompte à confirmer |
| Taille, poids | Pieds nus, toise, balance ; aucune mise en scène de jugement corporel | Conforme |
| FC de repos | Pouls radial au poignet, élève assis, chronomètre | Conforme |
| Ruffier-Dickson | Cinq vignettes : P1, 30 flexions en 45 s, P2, récupération 1 min, P3 ; légendes françaises incrustées | Position assise et durées conformes à la référence citée par l'application (section 7) ; durée de comptage du pouls non précisée |
| Killy | Dos au mur, cuisses horizontales, bras croisés, enseignante avec chronomètre, sans drapeau | Conforme à la version acceptée |
| Gainage ventral | Avant-bras et pointe des pieds, tapis, chronomètre posé au sol | Le chronomètre dessiné n'indique pas une durée |

Observation transversale : la plupart des images montrent des logos de type « virgule » sur les chaussures et
« trois bandes » sur les survêtements, qui rappellent des marques d'équipement sportif. Décision du porteur du projet :
retouche locale, limitée finalement à six images (section 7).

## 3. Intégration

- `assets/lab/<id>.jpg` : 14 fichiers, aucun autre fichier dans ce dossier.
- `assets/visual-bank/manifest.json` : bloc `lab_delivery` (archive, empreinte, date, retouches, licence) et, pour
  chaque image, chemin, dimensions, taille, empreinte actuelle (`sha256`) et d'origine (`source_sha256`), retouche,
  licence, statut, note de remise et texte alternatif.
- `src/acpa_msmda/visual_bank.py` : sous l'image, texte alternatif puis avertissement non normatif. Le volet
  « Illustration pédagogique » reste replié par défaut ; une image absente ne bloque jamais la page.
- Texte alternatif : ce que montre l'image, puis « Matériel représenté ». Il décrit l'image et ne constitue pas la
  liste du matériel requis : une telle liste dépend du protocole retenu (circulaire 2358/25 et annexe encore à
  vérifier, selon la note de remise). Pour Ruffier, il reproduit les cinq légendes en français, en arabe et en anglais.
- `data/translations.json` : 14 textes traduits en arabe et en anglais. Contrôle `tools/i18n_strings.py` :
  1 062 textes requis, aucun manquant.
- `NOTICE` et `assets/visual-bank/LICENCE-ILLUSTRATIONS.md` : code sous MIT, pictogrammes OpenMoji sous CC BY-SA 4.0,
  illustrations IA sous CC BY 4.0 dans la mesure des droits détenus (section 7). Le crédit affiché dans « Statut
  scientifique et sources » mentionne cette licence en français, en arabe et en anglais.

## 4. Tests automatisés

`tests/test_lab_illustrations.py`, 19 tests :
- couverture des 32 tests (14 illustrations et 18 pictogrammes, handgrip conservé) ;
- licences (OpenMoji, CC BY 4.0 des illustrations, NOTICE) et sécurité des SVG ;
- présence, format et poids des 14 JPEG ;
- provenance : empreinte actuelle conforme au manifeste, empreinte d'origine conforme à la remise, dimensions
  inchangées, preuve de remise conservée, aucun fichier parasite ;
- retouches limitées aux six images documentées, avec masques, zones et statistiques cohérents ;
- textes alternatifs traduits, sans tiret cadratin ; légendes de Ruffier dans les trois langues ; nuance de
  chronométrage du sprint dans les trois langues ;
- page du Laboratoire en français, arabe et anglais ; une image manquante ne bloque pas la page.

Suite complète en local (Python 3.12.3, dépendances exactes) : 253 tests réussis après la retouche et la légende du sprint (250 avant). `compileall` et
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

Recette refaite après la retouche, avec les images finales. Légende du sprint contrôlée ensuite en FR, AR et EN (image chargée, aucun débordement, légende de droite à gauche en arabe, aucune erreur ni requête externe) : [resultats/recette_sprint_iphone.json](resultats/recette_sprint_iphone.json), [captures/sprint30_legende_ar_iphone.jpg](captures/sprint30_legende_ar_iphone.jpg). Dans les six cas, le volet est replié à l'ouverture de
la page. Sur téléphone, les légendes incrustées dans l'image de
Ruffier sont trop petites pour être lues : le texte alternatif les reproduit dans la langue de l'interface. Limite :
émulation, pas un appareil réel ; la recette sur iPhone du porteur du projet reste à faire après fusion.

## 6. Points ouverts

1. Souplesse assise : l'élève est chaussé. Le porteur du projet a retenu que cette illustration pourra être remplacée
   par une version sans chaussures. Le fichier n'est pas encore remis ; à sa réception, il sera contrôlé comme les
   autres (empreinte, format, inspection, texte alternatif FR/AR/EN, tests, recette mobile).
2. Outil de génération des images : non précisé dans la remise ; à ajouter à la provenance s'il est connu.
3. Circulaire 2358/25 et son annexe : toujours à vérifier avant toute mention de conformité institutionnelle.

## 7. Décisions du porteur du projet (25 novembre 2026) et suites

| Décision | Suite donnée |
|---|---|
| 1. Licence CC BY 4.0 des illustrations IA, dans la mesure des droits détenus ; MIT pour le code ; CC BY-SA 4.0 pour OpenMoji | `NOTICE`, `assets/visual-bank/LICENCE-ILLUSTRATIONS.md` (périmètre, provenance, attribution suggérée), champs `license` du manifeste, crédit affiché dans l'application en FR, AR et EN. La CC BY 4.0 ne porte que sur les droits que le concédant peut concéder et exclut les marques |
| 2. Retouche locale des logos, sans modifier postures, personnages ni situations | Faite sur six images, puis arrêtée à la demande du porteur du projet : « garde intact ce qui n'est pas encore touché ». Les huit autres images sont identiques à la remise ; la retouche en cours de la navette Léger a été abandonnée et n'est pas livrée |
| 3. Ruffier-Dickson conservé si la position assise et les durées correspondent au protocole écrit retenu | Conforme à la référence citée par l'application (Bruggeman et al., 2020, PLOS ONE) : repos assis de cinq minutes, 30 flexions en 45 s, récupération assise d'une minute. L'article nomme les prises P0, P1 et P2 ; l'image utilise P1, P2 et P3 pour les mêmes trois moments. L'article ne précise ni la posture de la prise immédiate ni la durée de comptage. Séquence conservée |
| 4. Souplesse assise sans chaussures | Non modifiée ; remplacement possible par une version sans chaussures, sur décision du porteur du projet (point ouvert 1) |
| 5. Vérifier le chronométrage du sprint 30 m | Topend Sports : départ du chronomètre au premier mouvement, arrêt au passage de la poitrine sur la ligne d'arrivée, deux essais, meilleur temps retenu ; la position du chronométreur n'y est pas précisée. NSCA : personnel à l'arrivée, ou au départ et à l'arrivée. Topend Sports, 50 m : chronométreur en retrait de la piste, avec une vue sur le premier mouvement et sur l'arrivée. L'article ESA cité par l'application ne décrit pas le protocole dans le texte accessible. L'image place le chronométreur au départ. Décision du porteur du projet : image conservée, nuance de chronométrage ajoutée à la légende pédagogique en français, en arabe et en anglais |
| 6. Ressources Wikimedia traitées séparément | Hors de la PR #68 ; aucun effet sur les acquis ni obstacle à la fusion |

### Retouche des logos : méthode et contrôle

- Zones définies image par image : `retouche/zones_logos.json`, 51 zones en coordonnées de l'image d'origine.
- Dans chaque zone, les pixels du logo sont sélectionnés selon leur couleur : pixels clairs et peu saturés pour une
  bande ou une virgule blanche, teinte grise pour une virgule sur une chaussure blanche, zone entière pour une virgule
  ton sur ton. Une hystérésis suit la queue des virgules, et les trois bandes sont fusionnées en une seule zone.
- Remplissage par moyenne gaussienne normalisée des seuls pixels voisins de même matière : tissu foncé, chaussure
  blanche ou chaussure bleue. Le blanc d'un séparateur de vignette ou d'une semelle ne peut donc pas couler dans la
  zone.
- Contrôle visuel de chaque zone, avant et après, au grossissement 2 à 6.
- JPEG réenregistré avec les tables de quantification et le sous-échantillonnage d'origine.
- Script : `retouche/scripts/retouche_logos.py`, avec OpenCV 5.0.0, NumPy 2.5.3 et Pillow 12.3.0. Ces outils servent
  à la préparation et ne sont pas des dépendances de l'application.

| Image | Part modifiée | Écart moyen hors masque (sur 255) | 99e centile hors masque | Taille avant / après (octets) |
|---|---|---|---|---|
| Ruffier-Dickson | 2,289 % | 0,54 | 6 | 249 623 / 240 892 |
| Sargent | 0,107 % | 0,32 | 5 | 150 918 / 151 779 |
| Médecine-ball | 0,050 % | 0,20 | 4 | 121 436 / 121 478 |
| Saut horizontal | 0,074 % | 0,19 | 4 | 129 524 / 129 462 |
| Gainage ventral | 0,054 % | 0,13 | 3 | 102 641 / 102 607 |
| Killy | 0,143 % | 0,23 | 4 | 154 974 / 155 970 |

Hors masque, l'écart reste au niveau du bruit de réencodage JPEG : les modifications sont limitées aux logos.

Preuves :
- planche avant/après : [retouche/avant_apres.jpg](retouche/avant_apres.jpg) ;
- masques : `retouche/masques/` ;
- statistiques : [retouche/stats.json](retouche/stats.json).

Le porteur du projet a validé ces six retouches et décidé de ne pas lancer d'autre campagne de retouche : les huit
autres illustrations restent celles de la remise.

Restent visibles, à l'échelle du pixel, quelques fils clairs à l'emplacement de la queue de certaines virgules ; ils ne
sont pas reconnaissables comme logo.

## Reproduire

```bash
python -m unittest tests.test_lab_illustrations -v
python tools/i18n_strings.py --missing
python -m streamlit run app.py --server.port 8599 --server.headless true
python docs/validation/banque-visuelle-2026-11-25/scripts/recette_banque_visuelle.py /tmp/recette_banque http://localhost:8599
```

`scripts/integrer_banque14.py` a produit le manifeste et les traductions initiaux à partir du manifeste de remise,
avant la retouche. La retouche se rejoue à partir des originaux, présents dans l'archive de remise ou au commit
`ef8b54d` :

```bash
python -I docs/validation/banque-visuelle-2026-11-25/retouche/scripts/retouche_logos.py retouche <originaux> \
  docs/validation/banque-visuelle-2026-11-25/retouche/zones_logos.json <sortie>
python -I docs/validation/banque-visuelle-2026-11-25/retouche/scripts/stats_retouche.py <originaux> <sortie> \
  ruffier sargent medecine_ball saut_horizontal front_plank killy
```
