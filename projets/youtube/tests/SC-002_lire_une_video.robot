*** Settings ***
Documentation    SC-002 — Lire une vidéo
...              Source : Recette_YouTube_v0.3.docx § SC-002 – Lire une vidéo
...              Pivot : projets/youtube/features/SC-002_lire_une_video.feature

Resource         ../resources/metier.resource

Suite Setup      Démarrer Le Navigateur
Test Teardown    Terminer Le Test

Test Tags        projet:youtube    SC-002    persona:visiteur_anonyme    lecture


*** Test Cases ***
SC-002 Lire, Mettre En Pause Et Passer En Plein Écran
    [Documentation]    Lecture automatique de la première vidéo, pause, plein écran puis retour.
    Given Avoir Recherché    lofi
    When Ouvrir Le Premier Résultat
    And Attendre La Fin Des Annonces
    Then La Vidéo Est En Lecture
    When Mettre En Pause
    Then La Vidéo Est En Pause
    When Passer En Plein Écran
    Then Le Lecteur Est En Plein Écran
    When Quitter Le Plein Écran
    Then Le Lecteur Est En Taille Normale
