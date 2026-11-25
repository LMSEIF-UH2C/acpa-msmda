# Correctif : barre d'onglets décentrée sur mobile, 25 novembre 2026

Constat du porteur du projet sur iPhone, application déployée : la barre d'onglets commence au milieu de l'écran.
Seuls « Accueil », « Évaluer » et une partie d'« Explorer » restent visibles.

## Cause

- Depuis la PR #64 (24 novembre), `requirements.txt` fixe `streamlit==1.52.0`.
- Avec cette version, le conteneur `st-key-tabbar` se trouve à la profondeur visée par la règle d'apparition douce :
  `[data-testid="stMainBlockContainer"]>div>div>div{animation:rise .35s ease both}`.
- L'état final de l'animation (`transform:none`, conservé par `both`) l'emporte sur `transform:translateX(-50%)`.
  La barre reste donc à `left:50%` et déborde à droite.
- Sous Streamlit 1.47.1, la barre n'était pas à cette profondeur : le défaut n'apparaissait pas.

## Correctif

Une ligne dans `src/acpa_msmda/ui.py` : `.st-key-tabbar{animation:none!important}`. La barre fixe n'est plus animée.
Aucune autre règle ni aucun autre élément ne change.

Test ajouté : `tests/test_interface_consistency.py`, `test_tab_bar_centred_and_never_animated`.

## Mesures (iPhone 13 émulé, Chromium, fenêtre de 390 px)

| Version | Bord gauche | Bord droit | Transformation calculée |
|---|---|---|---|
| Application déployée (`main`, `84f107f`) | 195 | 566 | identité (centrage annulé) |
| `main` en local, Streamlit 1.52.0 | 195 | 566 | identité |
| Branche corrigée, Streamlit 1.52.0, accueil FR et AR, Laboratoire FR et AR | 10 | 380 | `translateX(-185 px)` |
| Branche corrigée, ordinateur, fenêtre de 1280 px | 360 | 920 | centrée |

Dans tous les cas : aucun débordement horizontal. Capture : [barre_onglets_avant_apres.jpg](barre_onglets_avant_apres.jpg).
Scripts : [scripts/mesure_tabbar.py](scripts/mesure_tabbar.py), [scripts/sonde_tabbar.py](scripts/sonde_tabbar.py).

## Hors de ce correctif

L'avatar et le badge rouge de Streamlit Community Cloud sont ajoutés par l'hébergeur en bas à droite, hors de la page
de l'application. Ils recouvrent encore la droite de la barre sur téléphone. Point N5, reporté au lot 6 par le
porteur du projet ; il n'est pas modifié ici.
