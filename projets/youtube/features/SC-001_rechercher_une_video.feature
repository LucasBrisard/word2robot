# language: fr
@SC-001 @persona:visiteur_anonyme @statut:actif @auto:total @recherche @smoke
Fonctionnalité: Rechercher une vidéo
  Source: Recette_YouTube_v0.3.docx § SC-001 – Rechercher une vidéo
  Images: image_01, image_02
  Objectif: vérifier que la recherche renvoie des résultats pertinents

  Scénario: Rechercher une vidéo par mot-clé
    Étant donné que le visiteur ouvre le site
    # mot-clé: Ouvrir L Application | origine: tableau | confiance: haute
    Et il refuse les cookies si le bandeau s'affiche
    # mot-clé: Fermer Le Bandeau Cookies | origine: tableau, image_01 | confiance: basse
    Quand il recherche "lofi"
    # mot-clé: Rechercher | origine: tableau | confiance: haute
    Alors au moins "10" vidéos sont proposées
    # mot-clé: La Recherche Retourne Au Moins | origine: legende, image_02 | confiance: moyenne
    Et au moins un des "3" premiers titres contient "lofi"
    # mot-clé: Les Premiers Résultats Contiennent | origine: deduit, image_02 | confiance: basse

# Q1 | « premiers titres contient » | action_vague | bloquant
#   question: « Vérifier les résultats → C'est OK » ne dit pas quoi vérifier. Que veut dire « résultats pertinents » ?
#   proposition: au moins 10 vidéos (légende de la capture 2) ET « lofi » dans le titre d'au moins un des 3 premiers résultats, sans tenir compte des majuscules
#   réponse: proposition acceptée
# Q2 | « il refuse les cookies » | action_vague | non bloquant
#   question: « Valider les cookies » : faut-il cliquer sur « Tout accepter » ou « Tout refuser » ? La capture 1 montre les deux boutons.
#   proposition: « Tout refuser » (pas de cookies de suivi pendant les tests, comportement plus stable)
#   réponse: proposition acceptée
# Q3 | « il refuse les cookies » | attendu_manquant | non bloquant
#   question: aucun résultat attendu pour l'étape « Valider les cookies ». Le bandeau doit-il simplement disparaître ?
#   proposition: oui, le bandeau disparaît et la page d'accueil reste affichée ; si le bandeau n'apparaît pas, l'étape est ignorée
#   réponse: proposition acceptée
# Q4 | « vidéos sont proposées » | contradiction_texte_image | non bloquant
#   question: la légende exige au moins 10 vidéos mais la capture 2 n'en montre que 3, et l'ovale « vérifier ici » entoure une zone vide entre le 1er et le 2e résultat. Que fallait-il vérifier à cet endroit ?
#   proposition: la capture est un extrait ; on garde la règle des 10 vidéos et on ignore l'ovale
#   réponse: proposition acceptée
# Q5 | « vidéos sont proposées » | contradiction_texte_image | non bloquant
#   question: la capture 2 montre le filtre « Vidéos » sélectionné, ce que le texte ne demande pas. Faut-il l'appliquer ? Les directs et les Shorts comptent-ils dans les 10 vidéos ?
#   proposition: pas de filtre ; on compte les vidéos de la liste de résultats, directs compris, Shorts exclus
#   réponse: proposition acceptée
# Q6 | « premiers titres contient » | non_deterministe | non bloquant
#   question: les résultats changent tous les jours (la capture 2 montre un direct en tête). Faut-il vérifier des titres précis ?
#   proposition: non, on vérifie seulement le nombre de résultats et la présence du terme recherché
#   réponse: proposition acceptée
# Q7 | - | technique | non bloquant
#   question: le Word indique la production (www.youtube.com, pas d'environnement de recette) et Chrome. Les tests peuvent-ils tourner sur la production, avec Chromium sans fenêtre et la langue forcée en français ? (vaut pour SC-001 à SC-003)
#   proposition: oui : production, Chromium sans fenêtre, interface en français pour des libellés stables
#   réponse: proposition acceptée
# Q8 | - | contradiction_texte_image | non bloquant
#   question: relevé du 14/10/2026 : les captures ne ressemblent pas au site réel (bouton « Connexion » au lieu de « Se connecter », bouton « OK » au lieu de la loupe, bandeau cookies plus long et affiché quelques secondes après le chargement). Les captures sont-elles de simples maquettes ?
#   proposition: oui ; les tests suivent le site réel, les captures servent seulement à comprendre l'intention
#   réponse:
