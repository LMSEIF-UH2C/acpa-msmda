# A5 — Matrice de qualification contextuelle Calc F14
Statut : dossier prospectif non approuvé ; aucune admission. Date 2026-11-28.
Scénario REAL-S09-02_PROPOSED : analyse descriptive après séance, données de contrôle agrégées, saisie manuelle dans un tableur sur un ordinateur enseignant déjà disponible. F14 uniquement. Pas de nécessité de F06 ou F10, pas de prétention à couvrir le scénario S09 intégral. Les essais ont porté sur Linux 25.2.3.2 ; Windows scolaire non vérifié. Le scénario n'est pas un compte rendu d'une séance réelle.

## Bilan des preuves fonctionnelles
- AUDIT_CALC_F14_V01.json : calcul sur 5 lignes construites, 3 valides, 510/900 s.
- AUDIT_CALC_F14_ROBUSTESSE_V02.json : 11/11 classifications attendues, 5 valides, 560/1030 s, 6 exclusions.
- AUDIT_TRANSFERT_BORIS_CALC_V01.json : transfert réel sur fichier public ; non nécessaire au scénario à outil unique.
- COUVERTURE_FONCTIONS_V01.csv : fonction F14 proposée, pas validation confirmatoire.
- Documentation éditeur : https://help.libreoffice.org/latest/en-US/text/scalc/01/func_sumif.html et https://www.libreoffice.org/get-help/system-requirements/

## Neuf portes critiques : preuves et limites
| Porte | Preuve disponible | Condition restant à établir |
|---|---|---|
| connectivity | exécution locale Linux, sans isolement réseau attesté | essai hors connexion sur version et machine cibles |
| equipment | exécution Linux sur banc | appareil réellement disponible, OS et version compatibles |
| age_privacy | tests sans données personnelles | procédure réelle de minimisation, stockage et accès ; pas de données nominatives |
| accessibility | aucun essai utilisateur spécifique | besoins d'accessibilité du professeur et conditions d'usage |
| physical_safety | scénario après séance proposé, sans interaction pendant activité | confirmation du périmètre réel hors aire motrice |
| morocco_availability | logiciel officiel distribuable | installation/disponibilité effectivement confirmée dans le contexte marocain |
| identity | Calc 25.2.3.2 Linux identifié lors des essais | correspondance avec variante installée cible, adjudication d'identité |
| source_current | sources documentaires et essais datés | applicabilité à la version cible et provenance courante |
| transfer | saisie manuelle prévue, export testé sur banc | confirmer qu'aucun transfert inter-applications n'est exigé, format cible |

Ressources : coût logiciel et coût obligatoire total à distinguer ; budget nul ne signifie pas équipement gratuit. Confirmer disponibilité du matériel, temps de préparation, une place appareil après séance, dépendances et contraintes. Pas de quantité de charge inventée. Pas de manifeste exécutable avant preuve et décision explicite portant sur ce contexte. Aucun des neuf statuts n'est promu COMPATIBLE par cette matrice. Les tests synthétiques de l'interface ne prouvent aucune porte.

## Séquence de clôture
1. Recette positive et négative A5 : 18/18, intégrité du registre, logs.
2. Consolider conditions de la variante cible ; contrôler fonctionnement local réellement hors réseau si exigé et documenter les contraintes, solliciter uniquement les confirmations indispensables du porteur.
3. Évaluer le dossier sur la base des preuves ; si incomplet, abstention motivée. Ne jamais assouplir les portes pour obtenir un candidat. A6 sécurité et recette interne selon plan distinct.