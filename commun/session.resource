*** Settings ***
Documentation    Mots-clés communs à tous les projets : navigateur, ouverture de l'application, personas,
...              capture de fin. Aucun secret ne transite par ce fichier : les personas désignent une
...              variable d'environnement, résolue à l'exécution.
...
...              Chaque projet fournit (projets/<projet>/projet.yaml et resources/locators.resource) :
...              PROJET, URL_ACCUEIL, PERSONAS, PAGE_PRETE, INDICATEUR_CONNECTE.

Library          OperatingSystem
Library          Browser    timeout=15s    run_on_failure=Take Screenshot
Variables        commun.yaml


*** Keywords ***
Démarrer Le Navigateur
    [Documentation]    Setup de suite : un seul navigateur, un contexte isolé par test.
    ...    CHEMIN_NAVIGATEUR (facultatif) force un exécutable précis, ex. un Chromium imposé par la DSI.
    IF    $CHEMIN_NAVIGATEUR
        New Browser    ${NAVIGATEUR}    headless=${HEADLESS}    executablePath=${CHEMIN_NAVIGATEUR}
    ELSE
        New Browser    ${NAVIGATEUR}    headless=${HEADLESS}
    END

Ouvrir L Application
    [Documentation]    Contexte vierge (visiteur anonyme), langue forcée pour des libellés stables.
    New Context    locale=${LOCALE}    viewport=${VIEWPORT}
    New Page    ${URL_ACCUEIL}
    Attendre Que La Page Soit Prête

Attendre Que La Page Soit Prête
    [Documentation]    Attend l'élément ${PAGE_PRETE} s'il est défini, sinon le chargement du réseau.
    IF    $PAGE_PRETE
        Wait For Elements State    ${PAGE_PRETE}    visible
    ELSE
        Wait For Load State    networkidle
    END

Terminer Le Test
    [Documentation]    Teardown de chaque test : capture d'écran finale dans log.html, à comparer en V4
    ...    avec les captures du Word. Sans page ouverte (test ignoré), ne fait rien.
    Run Keyword And Ignore Error    Take Screenshot    filename=fin-{index}

Ouvrir Une Session Persona
    [Documentation]    Réutilise une session préparée à la main (storage state Playwright).
    ...    Fichier : .auth/<projet>/<persona>.json, ou le chemin donné par la variable d'environnement du
    ...    persona (autre emplacement). Absent → le test est ignoré (SKIP), pas en échec.
    [Arguments]    ${persona}
    VAR    ${nom_variable}=    ${PERSONAS}[${persona}][storage_state_env]
    Should Not Be Equal    ${nom_variable}    ${None}    Le persona « ${persona} » n'a pas de session
    ${chemin}=    Get Environment Variable    ${nom_variable}    ${EXECDIR}/.auth/${PROJET}/${persona}.json
    ${existe}=    Run Keyword And Return Status    File Should Exist    ${chemin}
    Skip If    not ${existe}    Session « ${persona} » absente : la préparer (voir docs/credentials.md)
    New Context    locale=${LOCALE}    viewport=${VIEWPORT}    storageState=${chemin}
    New Page    ${URL_ACCUEIL}
    Should Not Be Empty    ${INDICATEUR_CONNECTE}
    ...    INDICATEUR_CONNECTE à relever dans projets/${PROJET}/resources/locators.resource
    Wait For Elements State    ${INDICATEUR_CONNECTE}    visible
    ...    message=La session « ${persona} » a expiré : la régénérer (voir docs/credentials.md)

Se Connecter Par Formulaire
    [Documentation]    Pour les applications à formulaire de connexion classique (sans SSO ni MFA).
    ...    Variables d'environnement <PROJET>_<PERSONA>_USER et _PASSWORD (ex. CRM_GESTIONNAIRE_USER).
    ...    Fill Secret lit la valeur depuis l'environnement sans l'écrire dans log.html.
    [Arguments]    ${persona}    ${champ_identifiant}    ${champ_mot_de_passe}    ${bouton}
    ${prefixe}=    Evaluate    f"{$PROJET}_{$persona}".upper()
    ${identifiant}=    Get Environment Variable    ${prefixe}_USER
    Fill Text    ${champ_identifiant}    ${identifiant}
    Fill Secret    ${champ_mot_de_passe}    %${prefixe}_PASSWORD
    Click    ${bouton}
