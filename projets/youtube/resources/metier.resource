*** Settings ***
Documentation    Mots-clés métier YouTube : une intention par mot-clé, avec ses attentes et assertions.
...              Utilisés par tests/SC-001 et SC-002 (pivots dans features/).

Library          Collections
Variables        ../projet.yaml
Resource         ../../../commun/session.resource
Resource         locators.resource


*** Keywords ***
Fermer Le Bandeau Cookies
    [Documentation]    Refuse les cookies si le bandeau (affiché en différé) ou la page consent.youtube.com
    ...    apparaît, puis attend son départ et la barre de recherche. Sans bandeau, ne fait rien (SC-001 Q2, Q3).
    ${present}=    Run Keyword And Return Status
    ...    Wait For Elements State    ${COOKIES_TOUT_REFUSER}    visible    timeout=10s
    IF    ${present}
        Click    ${COOKIES_TOUT_REFUSER}
        Wait For Elements State    ${COOKIES_TOUT_REFUSER}    hidden
    END
    Wait For Elements State    ${ENTETE_RECHERCHE}    visible

Rechercher
    [Documentation]    Saisit le terme dans la barre de recherche, valide, attend la liste de résultats.
    [Arguments]    ${terme}
    Fill Text    ${ENTETE_RECHERCHE}    ${terme}
    Keyboard Key    press    Enter
    Wait For Elements State    ${RESULTATS_VIDEOS} >> nth=0    visible

Avoir Recherché
    [Documentation]    Précondition autonome : ouvre le site, refuse les cookies, recherche le terme
    ...    (remplace « comme dans SC-001 », SC-002 Q5).
    [Arguments]    ${terme}
    Ouvrir L Application
    Fermer Le Bandeau Cookies
    Rechercher    ${terme}

La Recherche Retourne Au Moins
    [Documentation]    Nombre minimal de vidéos dans les résultats, sans filtre, Shorts exclus (SC-001 Q5).
    [Arguments]    ${nombre}
    Get Element Count    ${RESULTATS_VIDEOS}    >=    ${nombre}

Les Premiers Résultats Contiennent
    [Documentation]    Au moins un des ${n} premiers titres contient le terme, sans tenir compte des majuscules
    ...    (SC-001 Q1).
    [Arguments]    ${n}    ${terme}
    ${titres}=    Evaluate JavaScript    ${RESULTATS_TITRES}
    ...    (els, n) => els.slice(0, n).map(e => e.textContent.trim())
    ...    arg=${{int($n)}}    all_elements=True
    Should Contain Match    ${titres}    *${terme}*    case_insensitive=True
    ...    msg=Aucun des ${n} premiers titres ne contient « ${terme} » : ${titres}

Ouvrir Le Premier Résultat
    [Documentation]    Ouvre la première vidéo qui n'est ni un direct ni une première (SC-002 Q4).
    Click    ${RESULTATS_PREMIERE_VIDEO}
    Wait For Elements State    ${LECTEUR_VIDEO}    attached
    Get Url    contains    /watch

Attendre La Fin Des Annonces
    [Documentation]    Les publicités sont aléatoires : on ne les vérifie pas, on attend que la vidéo elle-même
    ...    ait démarré (une publicité peut commencer après l'ouverture), en cliquant « Ignorer » dès que
    ...    possible, ${DUREE_MAX_ANNONCES} au maximum (SC-002 Q1).
    WHILE    True    limit=${DUREE_MAX_ANNONCES}
    ...    on_limit_message=La vidéo n'a pas démarré après ${DUREE_MAX_ANNONCES} (publicité ?)
        ${demarree}=    Evaluate JavaScript    ${LECTEUR}    ${JS_VIDEO_DEMARREE}
        IF    ${demarree}    BREAK
        ${ignorable}=    Get Element States    ${LECTEUR_BOUTON_IGNORER}    then    bool(value & visible)
        IF    ${ignorable}    Click    ${LECTEUR_BOUTON_IGNORER}
        Run Keyword And Return Status
        ...    Wait For Function    ${JS_VIDEO_DEMARREE}    selector=${LECTEUR}    timeout=1s
    END

La Vidéo Est En Lecture
    [Documentation]    Sans clic sur « Lecture », la vidéo (pas une publicité) avance d'au moins 1 s
    ...    en 5 s d'observation (SC-002 Q2).
    ${depart}=    Evaluate JavaScript    ${LECTEUR}    (p) => p.getCurrentTime()
    Wait For Function
    ...    (p) => !p.classList.contains('ad-showing') && p.getPlayerState() === 1 && p.getCurrentTime() >= ${depart} + 1
    ...    selector=${LECTEUR}
    ...    timeout=5s
    ...    message=La vidéo n'avance pas (position de départ ${depart} s)

Mettre En Pause
    [Documentation]    Clique sur le bouton Lecture/Pause du lecteur (les commandes s'affichent au survol).
    Hover    ${LECTEUR}
    Click    ${LECTEUR_BOUTON_LECTURE}

La Vidéo Est En Pause
    [Documentation]    La vidéo est arrêtée, sa position ne bouge plus pendant 1 s et le bouton propose « Lire »
    ...    (SC-002 Q3).
    Wait For Function    (p) => p.getPlayerState() === 2    selector=${LECTEUR}
    ${ecart}=    Evaluate JavaScript
    ...    ${LECTEUR}
    ...    (p) => new Promise(r => { const t = p.getCurrentTime(); setTimeout(() => r(p.getCurrentTime() - t), 1000); })
    Should Be Equal As Numbers    ${ecart}    0    msg=La position avance encore de ${ecart} s
    Get Attribute    ${LECTEUR_BOUTON_LECTURE}    aria-label    starts    Lire

Passer En Plein Écran
    [Documentation]    Clique sur le bouton plein écran du lecteur.
    Hover    ${LECTEUR}
    Click    ${LECTEUR_BOUTON_PLEIN_ECRAN}

Le Lecteur Est En Plein Écran
    [Documentation]    L'élément affiché en plein écran contient le lecteur (YouTube met en plein écran un
    ...    conteneur du lecteur, pas le lecteur lui-même) (SC-002 Q3).
    Wait For Function    () => !!document.fullscreenElement?.contains(document.querySelector('#movie_player'))
    ...    message=Le lecteur n'est pas passé en plein écran

Quitter Le Plein Écran
    [Documentation]    Quitte le plein écran par le même bouton.
    Hover    ${LECTEUR}
    Click    ${LECTEUR_BOUTON_PLEIN_ECRAN}

Le Lecteur Est En Taille Normale
    [Documentation]    Plus aucun élément en plein écran : le lecteur a repris sa place dans la page (SC-002 Q3).
    Wait For Function    () => document.fullscreenElement === null
    ...    message=Le lecteur est resté en plein écran
