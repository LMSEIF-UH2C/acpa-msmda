# Outils d'enrichissement du catalogue

Scripts utilisés pour identifier des applications réelles et les ajouter à
`data/real_tools_catalog.json`. Aucune fiche n'est inventée : chaque ajout provient
d'une source vérifiable, et les fonctions pédagogiques restent à documenter.

| Script | Rôle |
|---|---|
| `collect_appstore.py` | Recherche publique de l'App Store par mots-clés, par catégorie EPS (États-Unis, France, Royaume-Uni). |
| `lookup_details.py` | Description officielle, genres et site de l'éditeur pour les applications d'au moins 100 avis. |
| `select_relevant.py` | Garde les applications dont le nom ou la description contient des termes propres à leur catégorie ; exclut le contenu 17+ et les domaines hors sujet. |
| `verify_candidates.py` | Pour une liste nom + site officiel : page accessible et nom présent dans la page. |
| `resolve_names.py` | Confirme un nom de la liste de prospection par correspondance exacte sur l'App Store (au moins 20 avis). |
| `build_catalog.py` | Fusionne les sources, retire les doublons, plafonne chaque catégorie et recalcule l'en-tête. |

Les fiches ajoutées ont le statut `OFFICIAL_LINK_ADDED_PENDING_FEATURE_REVIEW` :
masquées par défaut dans l'application et jamais suggérées tant que leurs fonctions
n'ont pas été relevées sur une source officielle.
