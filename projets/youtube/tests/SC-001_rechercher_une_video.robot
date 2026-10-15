*** Settings ***
Documentation    SC-001 — Rechercher une vidéo
...              Source : Recette_YouTube_v0.3.docx § SC-001 – Rechercher une vidéo
...              Pivot : projets/youtube/features/SC-001_rechercher_une_video.feature

Resource         ../resources/metier.resource

Suite Setup      Démarrer Le Navigateur
Test Teardown    Terminer Le Test

Test Tags        projet:youtube    SC-001    persona:visiteur_anonyme    recherche    smoke


*** Test Cases ***
SC-001 Rechercher Une Vidéo Par Mot-clé
    [Documentation]    Recherche « lofi », puis contrôle du nombre et de la pertinence des résultats.
    Given Ouvrir L Application
    And Fermer Le Bandeau Cookies
    When Rechercher    lofi
    Then La Recherche Retourne Au Moins    10
    And Les Premiers Résultats Contiennent    3    lofi
