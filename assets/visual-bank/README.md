# Banque visuelle ACPA/MSMDA — lot initial

Cette branche prépare des ressources, sans modifier l'interface ni le moteur. Les images doivent rester facultatives, adaptées aux moyens locaux et ne pas être présentées comme preuves de validation scientifique.

## Inventaire
- 14 illustrations IA acceptées par le porteur du projet : à importer depuis le ZIP de remise dans `assets/lab/` ; elles ne sont pas encore présentes dans cette branche. Handgrip exclu du lot illustré, test conservé.
- 18 tests : pictogramme de famille et matériel requis, sans représentation trompeuse d'un autre protocole.
- 14 SVG OpenMoji réellement copiés, inchangés, depuis le commit 5acb7f049c45c57a98449122d470de9f09bb6794. Ce sont des pictogrammes, pas des démonstrations.
- 8 références Wikimedia avec licence déclarée et auteur identifiés. Leur fichier original n'est pas copié ici : téléchargement bloqué dans l'environnement de préparation, contrôle visuel et import local par Claude nécessaires.

## Affectations proposées
| Section | Visuels | Usage |
|---|---|---|
| Laboratoire | 14 JPEG + pictogrammes | Repérage du test ; matériel et protocole dans le texte |
| Scénarisation / Espace EPS | fonds de terrain badminton, volley, handball, basket | préparer situations, espaces et variantes à effectifs différents |
| Organisation des ateliers | fonds de terrain + pictogrammes | repérage des zones ; pas d'échelle implicite |
| Studio pédagogique | cycle de course, vidéo, smartphone | observation, phases du geste, annotation pédagogique |
| Évaluation formative | observation, gestes | critères observables ; pas de diagnostic automatisé |
| Mode terrain | chrono, terrain | repères légers ; hors ligne pour les fichiers locaux |
| Cahier journalier | observation | repère discret, pas de photos de mineurs |
| Technothèque / Technologies réelles | Cardboard, AR.js, smartphone | ouverture facultative selon compatibilité ; alternative 2D |

## Intégration confiée à Claude
1. Importer le ZIP des 14 JPEG sans handgrip, remplacer Ruffier par la séquence en cinq étapes. Ne pas importer les planches de 32 tests rejetées.
2. Adapter la PR #59 plutôt que créer des doublons ; vérifier l'inventaire des 32 IDs. Ne pas rendre l'image obligatoire. Vérifier que le texte des protocoles reste la référence et que la circulaire non vérifiée n'est pas présentée comme validée.
3. Pour les ressources Wikimedia, consulter la page de chaque fichier, confirmer la licence et la provenance (y compris œuvres dérivées), récupérer les fichiers, inspecter réellement les visuels, contrôler les SVG (scripts/ressources externes) et conserver les crédits. Préférer un fichier local optimisé à un hotlink ; ne pas télécharger à l'exécution.
4. Pas de modification des calculs, dépendances ou navigation principale. Alternative sans image, texte alternatif FR/AR/EN, contrôle mobile et RTL ; traduire les légendes de Ruffier dans l'interface plutôt que présenter le français comme universel.
5. Ressources AR/VR : exploration assise et supervisée, pas de course avec casque, pas de promesse de mesure validée, vérifier âge, compatibilité et moyens ; ne pas ajouter une fonctionnalité immersive complète dans cette livraison.

## Licences
Tous les pictogrammes sont conçus par [OpenMoji](https://openmoji.org/) – projet open source d'emojis et d'icônes, licence [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Ils ne sont pas couverts par MIT. Conserver ces crédits dans l'application et dans toute redistribution. Pour les adaptations, respecter le partage à l'identique. Les images IA : documenter provenance et éventuelles retouches ; décision de licence du porteur avant publication. Ne pas utiliser les photos de mineurs identifiables sans droits appropriés.

Voir [manifest.json](manifest.json) et [références visuelles](REFERENCES.md).
