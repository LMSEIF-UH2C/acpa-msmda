# Sauvegardes des enseignants : Excel

Les espaces pédagogiques utilisent désormais des classeurs XLSX. Le JSON reste interne ou réservé à la recherche avancée (Lab, Investiguer).

- Évaluation formative : séance active, historique, critères, codes non nominatifs et observations.
- Cahier journalier : cycles, séances, créneaux, interruptions et projets.
- Projets de cycle : sauvegarde séparée, à restaurer avec les cycles correspondants.
- Les exports de consultation ne sont pas des sauvegardes restaurables. Les rapports PDF sont conservés.
- Les en-têtes des sauvegardes restent stables en français, quelle que soit la langue de l'interface. Ne pas modifier leur structure, ni la feuille ACPA.
- Les sauvegardes restent locales chez l'enseignant. Ne pas inclure de données nominatives. Limite d'import : 10 Mo, avec contrôles supplémentaires par module. Les formules sont refusées à la restauration.

## Migration technique (hors interface, hors ligne)

Depuis le dépôt, avec les dépendances installées :

```sh
python scripts/migrate_teacher_backup.py formative ancien.json evaluations.xlsx
python scripts/migrate_teacher_backup.py journal ancien_journal.json journal.xlsx
python scripts/migrate_teacher_backup.py projects anciens_projets.json projets.xlsx --journal journal.xlsx
```

Le script ne modifie pas les originaux et refuse d'écraser un fichier existant.
Les versions historiques prises en charge sont celles des validateurs préexistants (évaluation v1, journal v2–v4, projets v1).
