# A6 — Audit de sécurité et d'intégrité applicative (préparation V01)

Date : 28 novembre 2026. Décision du porteur : exploiter le prompt communautaire comme inspiration, sans détourner A5. A6 reste bloquée par A5. Audit en lecture seule, puis corrections ciblées sur branche expérimentale après validation des constats. Aucun test actif contre la démonstration publique, aucune donnée personnelle, aucune rotation automatique de secret, aucun changement de main, aucune prétention de certification.

## Références
- Checklist communautaire consultée : https://github.com/Vidaaieg/vibe-code-security-audit/blob/main/README.md (blob accb5c150574d14d17d754cca4a647ba7d235a6a, pas de licence déclarée; inspiration seulement, pas de reproduction).
- OWASP ASVS 5.0.0 : https://owasp.org/projects/ASVS ; sélection contextualisée, pas de conformité ASVS revendiquée.
- OWASP WSTG CSV injection : https://wstg.owasp.org/latest/4-Web_Application_Security_Testing/07-Injection/21-CSV_Injection/
- OWASP File Upload : https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- Streamlit security : https://docs.streamlit.io/develop/concepts/connections/security-reminders
- PyPA pip-audit : https://github.com/pypa/pip-audit

## Pré-audit statique limité
SHA examiné d5199bb10d7c8df6f6d74c038ea385c81607060b. Inventaire arbre et lecture ciblée, pas audit exhaustif; pas de scan Git historique ni dépendances exécuté.
- .streamlit/config.toml lignes 1–12 : CORS/XSRF true, maxUploadSize 10, gatherUsageStats false. Déclaration de configuration, pas preuve de réglage effectif de production.
- .gitignore : exclusions Python, venv et feedback; absence de règles explicites pour .env, .streamlit/secrets.toml et clés. Hygiène à renforcer; aucune fuite démontrée.
- experimental_real_admission.py : dossier épinglé côté opérateur, vérification SHA, documentation explicite « Configuration is not authentication ». Activation par environnement ne protège pas les visiteurs si exposée; maintien désactivé en public, contrôle d'accès serveur ou déploiement isolé à prouver avant activation réelle.
- teacher_workbooks.py lignes 77–105 : garde archive et rejet des formules, load_workbook read_only=True, data_only=False, keep_links=False. Couverture autres entrées à vérifier.
- experimental_registry.py lignes 50–55 et 129–147 : valeurs SQL paramétrées, noms de tables/colonnes construits (provenance des identifiants à vérifier), lecture preview via mode=ro. Ne pas conclure absence globale d'injection.
- ui.py lignes 400–405 et 437–440 : rendu HTML autorisé pour CSS/traductions; vérifier provenance et échappement de toutes valeurs dynamiques. Pas de XSS démontrée.
- docs/privacy-deployment.md : avertissements sur données nominatives, session serveur, photos, dictée potentiellement distante, avis persistés et services externes. Isolation et conservation effectives non testées.
- requirements.txt épinglé : reproductibilité partielle, pas absence de CVE.

## Matrice prospective A6
| ID | Domaine | Test attendu | État initial |
|---|---|---|---|
| SEC-01 | Accès interne et séparation public/privé | Vérifier absence route interne publique par défaut, accès non autorisé refusé, auth serveur ou isolation de déploiement; jamais confondre pin et auth | À vérifier |
| SEC-02 | Isolation des sessions et objets | Deux sessions locales distinctes, mesures/journal/photos/exports non partagés; pas de cache intersession sensible | À vérifier |
| SEC-03 | Secrets et historique Git | Inventaire complet des branches/références accessibles, scan redacted, règles gitignore, aucun secret dans rapport | À vérifier |
| SEC-04 | Dépendances et CI | Audit pip-audit sur exigences réelles, date/base/versions/limites, examiner permissions workflows et actions; aucune mise à jour automatique | À vérifier |
| SEC-05 | Imports CSV/XLSX/JSON et photos | Limites taille/décompression/types, erreurs contrôlées, contenu non exécutable, fixtures locales sans données personnelles | À vérifier |
| SEC-06 | Exports scientifiques | Valeurs non fiables traitées en texte dans tableurs, fidélité numérique et sémantique, CSV/XLSX/PDF; test inoffensif | À vérifier |
| SEC-07 | Injection et chemins | HTML, SQL, chemin local/URL, arguments, validation côté serveur et revue des sources de valeurs | À vérifier |
| SEC-08 | Intégrité scientifique | Refuser dossier modifié, contexte différent, observations périmées, tests synthétiques non présentés comme réels, résultats non finis ou invalides | À vérifier |
| SEC-09 | Disponibilité | Bornes d'import, calcul et recherche; rejet des entrées excessives sur banc local limité | À vérifier |
| SEC-10 | Confidentialité et conservation | Examiner données reçues, logs, exports, fichiers temporaires, dictée et liens externes; revue institutionnelle distincte | À vérifier |
| SEC-11 | Sauvegarde et restauration | Restaurer copie locale, vérifier schéma, provenance et empreintes, non-régression | À vérifier |
| SEC-12 | Publication | Contrôle artefacts, configuration effective, limites documentées, acceptation explicite | À vérifier |

Paiements/coupons/commandes : non applicables sous réserve de vérification d'architecture; chatbot agentique, comptes/OTP/RBAC : applicabilité à confirmer selon déploiement. Pour chaque résultat : statut PASS_BOUNDED / FINDING / NEEDS_CHECK / NOT_APPLICABLE, SHA, fichier:ligne, preuve, impact, priorité, correction proposée et retest. Ne pas étiqueter SAFE sans preuve. Toute anomalie critique ou haute confirmée et non résolue bloque publication de la fonctionnalité concernée; inconnues critiques explicitement traitées avant A7. Pas de nouvelle phase ni de panel supplémentaire. Le registre scientifique RET et les encadrés ASC restent intacts.