# Journal append-only des interventions
| Date UTC | Acteur | Intervention | Tâche | Action / résultat | Preuve | Suite |
|---|---|---|---|---|---|---|
| 2026-11-28 | interactive_assistant | BASELINE-0140 | P2-05 | Rapprochement global : 321 paires intersources; 263 nouvelles nominales, 6/6 tests; 0 fusion | [Run 46148006624](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46148006624) · [commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/d4b8f20533192aad701ad178da71f89a6271bcf0) | P2-06 |
| 2026-11-28 13:14 UTC | scheduled_agent | FIRST-RUN | — | Activation terminée selon historique; aucun résultat vérifié ni changement déclaré; pas de validation technique supplémentaire | Historique de la tâche ChatGPT, état HEAD inchangé constaté lors de coordination | P2-06 |
| 2026-11-28 | interactive_assistant | COORD-0001 | coordination | Initialisation de l'état partagé, checklist et règles de réservation, sans nouvelle collecte. Verrou libre. | [ETAT.json](ETAT.json) · [README.md](README.md) | P2-06 |
| 2026-11-28 | interactive_assistant | COORD-0001 | coordination | Correction du total de jalons : 24, contrôlé sur les IDs de l'état machine; 7/7/5/5, aucune modification scientifique | [ETAT.json](ETAT.json) | P2-06 |
| 2026-11-28 | interactive_assistant | INT-P2-06-0002 | P2-06 | Réservation exclusive avant audit ciblé | HEAD 1412afe6a87103429b3bde61d1af95c252d1d357 | Diagnostic des écarts |
| 2026-11-28 | interactive_assistant | INT-P2-06-0002 | P2-06 | Programme et protocole enregistrés, exécution déclenchée | [Protocole](../RESIDUAL_IDENTITY_PROTOCOL_V01.md) | Vérifier run |
| 2026-11-28 13:43 UTC | interactive_assistant | INT-P2-06-0002 | P2-06 | Clôture : 6/6 tests, deux écarts expliqués, source_url diagnostiqué, aucune fusion; verrou libéré | [Run 46151020904](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46151020904) · [audit](../AUDIT_RESIDUAL_IDENTITY_V01.json) | P2-07 |
| 2026-11-28 | interactive_assistant | INT-P2-07-0003 | P2-07 | Réservation exclusive | HEAD 29f3ffa9bbb60c3489dcd547954b446df3d5692d | Sensibilité et identifiants de listing |
| 2026-11-28 | interactive_assistant | INT-P2-07-0003 | P2-07 | Programme et protocole enregistrés | [Protocole](../IDENTITY_SENSITIVITY_PROTOCOL_V01.md) | Vérifier exécution |
| 2026-11-28 | interactive_assistant | INT-P2-07-0003 | P2-07 | Clôture : 8/8 tests, 204 correspondances listing, union 349, groupe 63 différé; verrou libéré | [Run 46151743685](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46151743685) · [audit](../AUDIT_IDENTITY_SENSITIVITY_V01.json) | P2-08 |
| 2026-11-28 14:16 UTC | interactive_assistant | INT-P2-08-0004 | P2-08 | Réservation exclusive | HEAD 0341fdadc65e7c18e94b5abce1adb0103d380df2 | Plan indépendant et contrôle hors candidats |
| 2026-11-28 | interactive_assistant | INT-P2-08-0004 | P2-08 | Plan et métriques préparés; tests synthétiques déclenchés | [Plan](../IDENTITY_INDEPENDENT_VALIDATION_PLAN_V01.md) | Vérifier exécution |
| 2026-11-28 | interactive_assistant | INT-P2-08-0004 | P2-08 | Clôture préparatoire : plan indépendant, 10/10 tests métriques; aucune sélection ni jugement humain; verrou libéré | [Run 46153948988](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46153948988) · [plan](../IDENTITY_INDEPENDENT_VALIDATION_PLAN_V01.md) | P2-10 |
| 2026-11-28 | interactive_assistant | INT-P2-10-0005 | P2-10 | Réservation exclusive | HEAD 50b23624488871a3e830974ed0762302926cd5d1 | Essai réel et reprise inter-runners |
| 2026-11-28 | interactive_assistant | INT-P2-10-0005 | P2-10 | Pilote borné et workflow inter-jobs enregistrés | [Protocole](../LIVE_CHECKPOINT_PROTOCOL_V01.md) | Vérifier run |
| 2026-11-28 | interactive_assistant | INT-P2-10-0005 | P2-10 | Clôture : 4 requêtes réelles, reprise 2+2, 0 nouvel appel en vérification, archive relue, verrou libéré | [Run 46154207305](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46154207305) · [audit](../AUDIT_LIVE_CHECKPOINT_V01.json) | P2-11 |
| 2026-11-28 | interactive_assistant | INT-P2-11-0006 | P2-11 | Réservation exclusive | HEAD 656df3884ba0a650e6ee9cd824c0a68990b4990b | Comparateurs et saturation |
| 2026-11-28 | interactive_assistant | INT-P2-11-0006 | P2-11 | Protocole et tests enregistrés | [Protocole](../SATURATION_COMPARISON_PROTOCOL_V01.md) | Vérifier run |
| 2026-11-28 | interactive_assistant | INT-P2-11-0006 | P2-11 | Clôture préparatoire : 7/7 tests, 10 scénarios, pertes et protections documentées, aucun seuil adopté; verrou libéré | [Run 46157245970](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46157245970) · [audit](../AUDIT_SATURATION_COMPARISON_V01.json) | P1-04 |
| 2026-11-28 | interactive_assistant | INT-P1-04-0007 | P1-04 | Réservation exclusive | HEAD cdc4aaf98246bddf8713ce9b75e274bea684283b | Inventaire et droits |
| 2026-11-28 | interactive_assistant | INT-P1-04-0007 | P1-04 | Inventaire 35 artefacts, 2 kits et projection vérifiés, revue droits; clôture préparatoire et verrou libéré | [Inventaire](../EVIDENCE_INVENTORY_V02.csv) | P2-12 |
| 2026-11-28 | interactive_assistant | INT-P2-12-0008 | P2-12 | Réservation exclusive | HEAD 9f5d9e646908d480a26e85de9adf95d9719eaff4 | Couverture pédagogique |
| 2026-11-28 | interactive_assistant | INT-P2-12-0008 | P2-12 | Plan scénarios, références et audit hors ligne enregistrés | [Protocole](../COVERAGE_TARGETED_PROTOCOL_V02.md) | Vérifier run |
| 2026-11-28 | interactive_assistant | INT-P2-12-0008 | P2-12 | Audit structurel réussi, préparation clôturée; verrou libéré, plus de READY | [Run 46158365439](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46158365439) · [dossier de décision](../GATE_VALIDATION_EQUIPE_V01.md) | Équipe, cinq préconditions |
| 2026-11-28 | interactive_assistant | INT-PREP-HUM-0009 | préparation humaine | Récupération partielle 207 descriptions; dossier organisateur et huit lots, aucun verdict; commit administratif CAS, verrou libre | [Note](../PREPARATION_VALIDATION_HUMAINE_V01.md) | Équipe, préconditions humaines |
| 2026-11-28 | interactive_assistant | INT-RECOVERY-HIST-0010 | P1-02 partiel | Archive Apple du porteur relue, 2412 liste identique; union native descriptive 26319; aucun ajout | [Audit](../AUDIT_HISTORICAL_APPLE_RECOVERY_V01.json) | Archives Android et décisions |
| 2026-11-28 | interactive_assistant | INT-RECOVERY-HIST-0011 | P1-02 partiel | Registre 45676 réconcilié, κ IA-IA reproduit, 6 fichiers privés relus; aucune validation humaine | [Audit](../AUDIT_HISTORICAL_DECISIONS_V01.json) | Bruts Android et provenance Claude |
| 2026-11-28 | interactive_assistant | INT-RECOVERY-HIST-0012 | P1-02 partiel | Index F-Droid 5026/5026; copie privée vérifiée; aucune collecte | [Audit](../AUDIT_HISTORICAL_FDROID_RECOVERY_V01.json) | Aptoide et provenance |
| 2026-11-28 | interactive_assistant | INT-PREP-FINAL-0013 | clôture exploratoire | Rejeu final non conforme, 16 tests synthétiques, dossier privé relu; fin recherche répétitive, aucun nouveau jalon scientifique clos | [Audit](../AUDIT_FINALISATION_EXPLORATOIRE_V01.json) | Décision équipe et juges |
| 2026-11-28 | interactive_assistant | INT-APP-A1-0014 | A1 application | Réservation explicite du porteur, branche intégration distincte, aucun passage confirmatoire | HEAD ba09fc99c279a0678e273503aa738ce62121da48 | Adaptateur et régression |
| 2026-11-28 | interactive_assistant | INT-APP-A1-0014 | A1 application | PR82, 48/48 ciblés, régression PENDING; verrou libéré | [Audit](../AUDIT_APPLICATION_A1_V01.json) | A1 |
| 2026-11-28 | interactive_assistant | INT-APP-A2-0015 | A2 | A1 CI 7/7, réservation A2 distincte, deux entrées | PR82 | Persistance et quarantaine |
| 2026-11-28 | interactive_assistant | INT-APP-A2-0015 | A2 | 2500 enregistrements, 34 pistes, 38/38 tests, CI générale PENDING; verrou libéré | [Audit](../AUDIT_APPLICATION_A2_V01.json) | Recette double entrée |
| 2026-11-28 | interactive_assistant | INT-APP-A2-0016 | A2 recette | CI précédente 7/7; réservation navigateur et note de perspective | PR82 | Test trois modes |
| 2026-11-28 | interactive_assistant | INT-APP-A2-0016 | A2 recette | Test navigateur lancé, résultats non encore vérifiés | run 46169706644 | Reprendre au résultat terminal |
| 2026-11-28 | interactive_assistant | INT-APP-A2-0016 | A2 reprise | Premier run en échec, correction test-only, relance 46170522696 | Audit navigateur | Résultats terminaux avant A3 |
| 2026-11-28 | interactive_assistant | INT-APP-A2-0016 | A2 clôture | 18/18 navigateur, 5/5 CI, artefact relu, verrou libéré | run 46170522696 | A3 READY |
| 2026-11-28 | interactive_assistant | INT-APP-A3-0017 | A3 | Réservation, A2 accepté | PR82 | Qualification documentaire |
| 2026-11-28 | interactive_assistant | INT-APP-A3-0017 | A3 | 34 propositions documentaires, 30/30 ciblés; CI générale en cours | run 46171020031 | Liaison preuve et recette UI |
| 2026-11-28 | interactive_assistant | INT-APP-A3-0017 | demande porteur | Création registre transversal de 12 entrées, règle permanente de conservation; A3 et verrou inchangés | [Registre](../REGISTRE_ECHECS_ANOMALIES_LIMITES_V01.md) | Reprendre recette A3 |
| 2026-11-28 | interactive_assistant | INT-APP-A3-0017 | A3 renforcement | 10/10 CI précédente; liaison SHA locale, 34/34 tests, recette navigateur en cours | run 46171523523 | Vérifier recette avant A4 |
| 2026-11-28 | interactive_assistant | INT-APP-A3-0017 | Préparation A4 | Contrat et 16 cas proposés, non exécutés; A3 9/10 CI réussis | [Plan](../PLAN_APPLICATION_A4_V01.md) | Recette A3 terminale |
| 2026-11-28 | interactive_assistant | INT-APP-A3-0017 | A3 clôture | 10/10 CI, 18/18 parcours, 6/6 panneaux, archive relue | [Audit](../AUDIT_APPLICATION_A3_V01.json) | A4 READY |
| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 réservation | A3 accepté, prototype de décision isolé | [Plan](../PLAN_APPLICATION_A4_V01.md) | Implémenter et tester |
| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 prototype | 36/36 ciblés; 34 pistes non admises; limites et CI à contrôler | [Audit](../AUDIT_APPLICATION_A4_V01.json) | Durcissement A4 |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 reprise | A4 reprise du 28/11/2026 : huit runs du commit applicatif 01b83f7 terminaux, 12/12 jobs réussis. Reprise par le même propriétaire logique INT-APP-A4-0018 après clôture du précédent échange et vérification des runs. RET-013, adaptateur de preuves et comparateur historique restent ouverts. Aucun gate scientifique levé. | [Audit A4](../AUDIT_APPLICATION_A4_V01.json) | RET-013 |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 RET-013 | Correction implémentée, huit workflows non terminaux; verrou conservé | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/78771bb10eb721f014bcf0fd3a1c5cdffaa7a40f) · [retest](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46172415369) | Vérifier les résultats |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 reprise | 6/8 workflows réussis, 2 en cours au contrôle; audit des 34 propositions et identification du moteur historique; verrou conservé | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/78771bb10eb721f014bcf0fd3a1c5cdffaa7a40f) | Recettes terminales puis adaptateur |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 adaptateur et comparateur | RET-013 8/8 workflows réussis; adaptateur de lignée et appel natif implémentés, nouveaux tests en cours | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/5857b0f4bef45ee7c3709bae890c265aa099648f) | Vérifier les résultats terminaux |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 préparation oracle | 8/8 workflows réussis au contrôle, plan prospectif commun | [Protocole](../PLAN_APPLICATION_A4_COMMON_POOL_V01.md) | Exécuter après CI terminale |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 oracle | 8/8 CI précédente; tests communs 10 scénarios +100 pools implémentés, résultats à vérifier | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/b81690de34e135d5f5d23df66d9c5a7de9073706) | Lire résultats et limites |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | Décision porteur | Réutilisation validation E3; A6 recette interne documentée, pas de nouveau panel pour piste applicative | Rapport maître et ETAT.json | Continuer A4 puis A5 |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | Gouvernance | Orientations d'équipe communiquées par le porteur après consultation, selon sa déclaration; éviter les approbations redondantes | ETAT.json et rapport maître | Appliquer aux prochaines décisions |

| 2026-11-28 | interactive_assistant | INT-APP-A4-0018 | A4 clôture | 5/5 CI; 52/52 tests; I 2/10, P 7/10, E 8/10; verrou libéré | [Run](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46173324214) | A5 READY |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | A5 réservation | Interface expérimentale trilingue, abstention réelle et simulation fictive | ETAT.json | Implémenter et tester |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | A5 implémentation et ASC-01 | Interface trilingue, recette en cours; encadré permanent abstention décisionnelle à la demande du porteur | [Code](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/d3bc403532a6bf775ea7b01b88db86d28246609c) | Recette et preuves |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | Pilote réel | 4 technologies documentées; Calc réel PASS; chaîne non testée | [PILOTE_ECOSYSTEMES_REELS_V01.md](../PILOTE_ECOSYSTEMES_REELS_V01.md) | Recette et qualification réelle |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | Admission réelle | 7/7 CI interface; contrat admission réelle implémenté, nouvelle CI en cours | [Code](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/d00f75afb6ecc16d14cbc7558de945b51aa7f367) | Recette puis dossier réel |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | RET-014 et dossiers | Calc réel 25/30→30/30; quatre dossiers brouillons; aucune admission | [AUDIT_TRANSFERT_CSV_REEL_V02.json](../AUDIT_TRANSFERT_CSV_REEL_V02.json) | Recette et tests extrémités |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | Rejeu RET-014 et UI interne | 8/8 CI antérieure, mêmes SHA Calc, panneau conditionnel et contrôle transfert réel | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/65aab6dac578688e89ba3259e8fb48eb38c1fecc) | CI puis recette mode activé |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | Références BORIS | 6/6 intervalles rapprochés, écart de structure documenté, aucun runtime | [AUDIT_BORIS_REFERENCE_V01.json](../AUDIT_BORIS_REFERENCE_V01.json) | Recette et essai isolé |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | Recette activée et BORIS | CI précédente 8/8, deux nouveaux workflows implémentés | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/422a3e992e4897d591a4945c4eda99690bcebe60) | Lire résultats terminaux |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | Recette activée et RET-016 | 12/12 navigateur, BORIS installation OK/export bloqué libEGL, archive vérifiée | [BORIS](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46175483107) | Retest environnement |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | RET-016 retest | 5/6 succès antérieurs; correctif EGL et diagnostic CLI | [Retest](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46175844527) | Lire preuves terminales |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | RET-016/017 | QtWidgets OK; export arrêté par MPV, code 5; correctif libmpv2 | [Retest EGL](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46175844527) | Retest MPV |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | RET-018 | EGL/MPV chargés; CLI appelle une fonction absente; protocole natif distinct | [Run](https://github.com/LMSEIF-UH2C/acpa-msmda/actions/runs/46176972870) | Retest natif puis diversification |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | RET-018 voie native | 4/4 régressions précédentes; test natif déclenché, aucun succès présumé | [Commit](https://github.com/LMSEIF-UH2C/acpa-msmda/commit/b13e9cbd4cf4a375a7e653b02a93637f9704b783) | Lire preuve et diversifier |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | BORIS natif + transfert réel Calc | 8/8 événements, 4/4 intervalles, 168/168 valeurs, 144/144 types sous politique explicite | [AUDIT_TRANSFERT_BORIS_CALC_V01.json](../AUDIT_TRANSFERT_BORIS_CALC_V01.json) | Qualification et recette positive |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | ASC-03 | Observation du porteur capitalisée : diagnostic reproductible des technologies tierces, rétroaction potentielle; aucune amélioration amont revendiquée | [Rapport](../RAPPORT_SCIENTIFIQUE_EVOLUTIF.md#asc-03--fonction-diagnostique-et-rétroaction-vers-les-technologies-évaluées-contribution-émergente-exploratoire) | A5 inchangée |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | F14 Calc + recette positive | Recalcul réel sur données de contrôle, dossier positif synthétique temporaire, 18 cas navigateur prévus | [AUDIT_CALC_F14_V01.json](../AUDIT_CALC_F14_V01.json) | CI puis qualification réelle |

| 2026-11-28 | interactive_assistant | INT-APP-A5-0019 | RET-020 + robustesse Calc | 14/18 navigateur, 11/11 classifications Calc, retest ciblé | [AUDIT_CALC_F14_ROBUSTESSE_V02.json](../AUDIT_CALC_F14_ROBUSTESSE_V02.json) | Vérifier 18 cas puis qualification |
