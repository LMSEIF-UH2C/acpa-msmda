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
