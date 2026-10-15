*** Settings ***
Documentation    Localisateurs YouTube, regroupés par écran.
...              Relevés sur le site réel le 14/10/2026 (visiteur anonyme, interface en français, 1366×900).
...              Règle : rôle / attribut stable / texte visible, jamais de XPath positionnel.


*** Variables ***
# --- Attendus par commun/session.resource ---
# Application prête : barre de recherche ✓, ou page de consentement consent.youtube.com ✓
${PAGE_PRETE}
...                              :is(input[name="search_query"], form[action*="consent.youtube.com"]) >> nth=0
# À CONFIRMER : élément visible seulement une fois connecté (inutile tant que SC-003 n'est pas automatisé)
${INDICATEUR_CONNECTE}           ${EMPTY}

# --- Consentement cookies, deux variantes --- ✓
# 1. bandeau ytd-consent-bump-v2-lightbox, affiché quelques secondes après le chargement ; après refus,
#    le bouton reste dans la page mais caché (0×0) : on attend l'état « hidden » ;
# 2. page consent.youtube.com (redirection selon l'IP) : bouton « Tout refuser » d'un formulaire /save,
#    qui renvoie ensuite vers YouTube (relevé le 14/10/2026).
${COOKIES_TOUT_REFUSER}
...                              :is(button[aria-label^="Refuser l'utilisation de cookies"],
...                              form[action*="consent.youtube.com"] button[aria-label="Tout refuser"]) >> nth=0

# --- En-tête --- ✓
${ENTETE_RECHERCHE}              input[name="search_query"]

# --- Résultats de recherche --- ✓ (14 vidéos pour « lofi » ; les Shorts sont dans des étagères à part)
${RESULTATS_VIDEOS}              ytd-search ytd-video-renderer
${RESULTATS_TITRES}              ytd-search ytd-video-renderer a#video-title
# Vidéo « normale » = vignette avec une durée ; exclut directs et premières (SC-002 Q4) ✓
${VIGNETTE_AVEC_DUREE}           ytd-thumbnail-overlay-time-status-renderer[overlay-style="DEFAULT"]
${RESULTATS_PREMIERE_VIDEO}
...                              ytd-search ytd-video-renderer:has(${VIGNETTE_AVEC_DUREE}) a#video-title >> nth=0

# --- Lecteur --- ✓
${LECTEUR}                       \#movie_player
${LECTEUR_VIDEO}                 \#movie_player video
${LECTEUR_EN_ANNONCE}            \#movie_player.ad-showing
# API du lecteur (#movie_player) : getPlayerState() 1 = lecture, 2 = pause ; getCurrentTime() = position de
# la vidéo elle-même (pas de la publicité). Vidéo démarrée = pas de publicité, en lecture, position > 0,5 s.
${JS_VIDEO_DEMARREE}
...                              (p) => !p.classList.contains('ad-showing') && p.getPlayerState() === 1
...                              && p.getCurrentTime() > 0.5
# Libellé « Ignorer » (le Word parle de « passer ») ; un clic JavaScript est ignoré, un vrai clic est requis
${LECTEUR_BOUTON_IGNORER}        \#movie_player button.ytp-skip-ad-button
# aria-label « Pause (k) » en lecture, « Lire … » en pause
${LECTEUR_BOUTON_LECTURE}        \#movie_player .ytp-play-button
# Plein écran vérifié au 1er run (conteneur) : document.fullscreenElement est un conteneur du lecteur ✓
${LECTEUR_BOUTON_PLEIN_ECRAN}    \#movie_player .ytp-fullscreen-button
