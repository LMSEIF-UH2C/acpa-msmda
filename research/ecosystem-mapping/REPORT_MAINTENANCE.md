# Maintenance du rapport scientifique maître
Le rapport [RAPPORT_SCIENTIFIQUE_EVOLUTIF.md](RAPPORT_SCIENTIFIQUE_EVOLUTIF.md) est le point d'entrée documentaire du projet de recherche. Toute prochaine contribution méthodologique doit mettre à jour ce fichier dans le même commit que le protocole ou le code concerné, ou dans un commit de clôture distinct après vérification des résultats. Conserver les résultats intermédiaires, même négatifs, et les dates UTC.
- Avant exécution : protocole/version, hypothèse, paramètres, conditions de passage, accès et limites; marquer comme prévu.
- Après exécution : état exact, run et artefact, effectifs réconciliés, tests réellement réussis/échoués, erreurs, empreintes disponibles, interprétation, limites et éventuel amendement.
- Si collecte/validation en cours : indiquer date du contrôle et aucun résultat anticipé.
- Séparer observations, résultats synthétiques, tests techniques, validation humaine, et propositions. Ne jamais transformer un résultat de pilote en validation confirmatoire. Ne pas supprimer la trace d'une décision antérieure.
- Avant nouvelle rédaction : relire rapport maître et documents sources; vérifier le HEAD de la PR 81 et le statut des runs; préserver main et publication. Pas de collecte ou de workflow réseau déclenché par simple modification du rapport.
- À chaque jalon : produire une version numérotée et préparer un manifeste de preuves autorisées; conserver les données brutes soumises à droits hors dépôt public. Le rapport ne doit pas contenir de données privées, secrets, descriptions commerciales intégrales ou images non autorisées.
- La maintenance se réalise au fil des contributions, pas automatiquement entre les conversations. Ne pas annoncer d'exécution autonome si aucun mécanisme n'a été configuré.
