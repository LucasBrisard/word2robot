*** Settings ***
Documentation    Localisateurs du projet {{PROJET}}, regroupés par écran, relevés sur l'application réelle
...              (/automatiser). Règle : rôle / attribut stable / texte visible, jamais de XPath positionnel.


*** Variables ***
# --- Attendus par commun/session.resource ---
# À CONFIRMER : élément visible quand l'application est prête (ex. menu principal, barre de recherche)
${PAGE_PRETE}             ${EMPTY}
# À CONFIRMER : élément visible seulement une fois connecté (ex. avatar, « Se déconnecter »)
${INDICATEUR_CONNECTE}    ${EMPTY}
