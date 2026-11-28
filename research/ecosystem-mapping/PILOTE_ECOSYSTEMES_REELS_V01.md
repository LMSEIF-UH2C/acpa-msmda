# Pilote d'écosystèmes réels — V0.1

Décision du porteur : passer des fixtures algorithmiques aux technologies réelles, sans confondre documentation et qualification opérationnelle. Pilote exploratoire, aucune promotion au catalogue stable ni levée de gate confirmatoire. Relecture de sources officielles le 28/11/2026. Identifiants du registre conservés; correspondances F proposées, non validées. Voir [audit structuré](AUDIT_PILOTE_ECOSYSTEMES_REELS_V01.json).

## Kinovea — doc_web:WD02
- Variante : desktop Windows; documentation 0.9.5, release page 2025.1.
- Documentation : Annotation vidéo, mesures et export CSV de séries; gratuit et open source; Windows uniquement.
- Correspondances proposées : F06, F07.
- Limites : Pas de test d'installation, hors réseau, précision, accessibilité ou données scolaires; contrôle de mise à jour et chemins locaux à examiner. Aucun enregistrement vidéo élève.
- Sources : [1](https://www.kinovea.org/features) · [2](https://www.kinovea.org/help/en/export/data.html) · [3](https://www.kinovea.org/download/) · [4](https://kinovea.org/privacy.html)

## BORIS — doc_web:WD16
- Variante : desktop; manuel 9.15.0.
- Documentation : Codage vidéo/audio ou observation directe, export des événements agrégés en CSV avec durées pour événements STATE; gratuit et open source.
- Correspondances proposées : F06, F14.
- Limites : Mises à jour pouvant utiliser Internet; test hors réseau et exécution non effectués; protocole de codage, durée, catégories et confidentialité à établir.
- Sources : [1](https://www.boris.unito.it/user_guide/) · [2](https://www.boris.unito.it/user_guide/export_events/) · [3](https://www.boris.unito.it/user_guide/create_project/) · [4](https://www.boris.unito.it/user_guide/preferences/)

## LibreOffice Calc — doc_web:WD07
- Variante : desktop; guide 26.2, binaire testé 25.2.3.2.
- Documentation : Tableur, import CSV et traitement local. Test effectif de conversion CSV vers XLSX puis CSV sur version installée.
- Correspondances proposées : F10, F14.
- Limites : Essai sur trois lignes techniques sans personnes uniquement; fonctionnement réseau désactivé non vérifié par isolement; accès et version à vérifier au Maroc; aucune mesure pédagogique réelle.
- Sources : [1](https://books.libreoffice.org/en/CG262/CG26201-Introduction.html) · [2](https://www.libreoffice.org/system-requirements/) · [3](https://www.libreoffice.org/download/)

## jamovi — doc_web:WD04
- Variante : desktop, distinct du cloud.
- Documentation : Analyse statistique locale; application gratuite, import CSV, fonctionnement hors ligne annoncé.
- Correspondances proposées : F10, F14.
- Limites : Pas de binaire disponible dans l'environnement d'essai; import effectif, version, modules, exactitude et paramètres statistiques non testés.
- Sources : [1](https://www.jamovi.org/download.html) · [2](https://www.jamovi.org/user-manual.html) · [3](https://www.jamovi.org/troubleshooting.html) · [4](https://www.jamovi.org/privacy.html)

## Premier scénario REAL-S09-01
Sous-cas de S09 (analyse après séance), différent du scénario S09 complet : F06 observation, F14 analyse de pratique, F10 suivi facultatif; F01 planification du S09 complet non couverte ici. Hypothèse à vérifier : ordinateur Windows déjà disponible, traitements séquentiels, données sans identifiants, budget logiciel direct nul mais coûts matériels/temps non établis. Comparer BORIS seul, BORIS→jamovi, BORIS→Calc→jamovi. Calc uniquement si nettoyage/contrôle utile; Kinovea est une variante de collecte pour analyse du mouvement, non un ajout automatique. Les formats CSV documentés aux extrémités permettent de proposer un transfert manuel, pas d'affirmer l'interopérabilité. Vérifier séparateurs, décimales, unités, valeurs manquantes, doublons, événements POINT/STATE et agrégation avant tout calcul pédagogique. Aucun gain ou couverture complète réelle revendiqué.

## Essai effectivement exécuté
LibreOffice Calc 25.2.3.2, mode headless, profil temporaire isolé : CSV→XLSX→CSV, 3 lignes, 9 cellules numériques et 6 libellés préservés; totaux techniques MOTOR 24.5 s, WAIT 5.5 s vérifiés par Decimal. Entrée construite sans données humaines, aucune observation d'élève; ce n'est pas un export BORIS réel. Empreintes, commandes et contenu exact dans l'audit JSON. BORIS, Kinovea et jamovi non installés dans cet environnement; chaîne complète non exécutée, réseau désactivé non éprouvé. Aucun résultat d'apprentissage ou ALT-PE inféré.

## Critères de prochaine recette
1. Contrôler variantes installées, coûts obligatoires, disponibilité locale, accessibilité, autorisation de données, exigences hors ligne et ressources de la situation.
2. Tester export BORIS réel sur une démonstration sans données personnelles, import direct jamovi et passage facultatif par Calc; comparer nombres de lignes, unités, valeurs, types et résultats attendus. Consigner le cas où Calc est inutile.
3. Construire la fiche d'évidence explicite par fonction et contrainte, revue du porteur assisté par IA, puis adapter le moteur à une admission réelle contrôlée, distincte des fixtures. Garder ASC-01 : si une exigence manque, abstention motivée.

## Relecture fonctionnelle — parcimonie
Le manuel officiel [analyse BORIS](https://www.boris.unito.it/user_guide/analysis/) documente déjà nombres d'occurrences, durées et pourcentages. BORIS seul peut couvrir un descriptif simple; l'ajout de Calc et jamovi doit satisfaire une exigence supplémentaire démontrable. Voir [CONTRAT_ADMISSION_REELLE_V01.md](CONTRAT_ADMISSION_REELLE_V01.md). Aucun essai BORIS ni jamovi exécuté dans cette passe.

## ASC-02 — Intégrité sémantique des transferts (proposition à capitaliser)

> La compatibilité des formats ne garantit pas l'intégrité des données transférées. La complémentarité technique doit être démontrée au niveau des données et de leur interprétation, pas seulement au niveau de l'extension du fichier.

RET-014 : exécution réelle Calc 25.2.3.2 sous Linux, CSV→XLSX→CSV, 5 lignes × 6 champs, identifiants 001–004, texte FR/AR, décimales et champs vides. Import standard : 25/30 champs exacts, cinq identifiants altérés (zéros initiaux perdus). Import avec types de colonnes explicites : 30/30 champs exacts dans ce cas. Les deux commandes terminent avec code 0; le succès de la commande n'est pas un contrôle d'intégrité. [Audit intégral](AUDIT_TRANSFERT_CSV_REEL_V02.json). Ce résultat est borné à un fichier construit et une version, ne prouve ni un échange BORIS/jamovi ni la préservation des types et significations dans tous les logiciels. L'échec et le retest sont conservés. Ne pas élargir la revendication à une validation scientifique externe.

Dossiers par technologie : [DOSSIERS_QUALIFICATION_REELLE_V01.json](DOSSIERS_QUALIFICATION_REELLE_V01.json), brouillons de revue, non manifestes d'approbation. Aucun résultat opérationnel nouveau.
