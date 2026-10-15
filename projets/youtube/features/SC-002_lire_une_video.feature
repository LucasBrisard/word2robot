# language: fr
@SC-002 @persona:visiteur_anonyme @statut:actif @auto:total @lecture
Fonctionnalité: Lire une vidéo
  Source: Recette_YouTube_v0.3.docx § SC-002 – Lire une vidéo
  Images: image_03
  Objectif: vérifier la lecture automatique, la pause et le plein écran du lecteur

  Contexte:
    Étant donné que le visiteur a recherché "lofi"
    # mot-clé: Avoir Recherché | origine: texte | confiance: moyenne

  Scénario: Lire, mettre en pause et passer en plein écran
    Quand il ouvre la première vidéo des résultats
    # mot-clé: Ouvrir Le Premier Résultat | origine: texte | confiance: moyenne
    Et une éventuelle publicité se termine ou est passée
    # mot-clé: Attendre La Fin Des Annonces | origine: texte, image_03 | confiance: basse
    Alors la vidéo se lance toute seule et avance normalement
    # mot-clé: La Vidéo Est En Lecture | origine: texte, image_03 | confiance: moyenne
    Quand il met la vidéo en pause
    # mot-clé: Mettre En Pause | origine: texte | confiance: haute
    Alors la vidéo est arrêtée
    # mot-clé: La Vidéo Est En Pause | origine: deduit | confiance: basse
    Quand il passe en plein écran
    # mot-clé: Passer En Plein Écran | origine: texte | confiance: haute
    Alors le lecteur occupe tout l'écran
    # mot-clé: Le Lecteur Est En Plein Écran | origine: deduit | confiance: moyenne
    Quand il quitte le plein écran
    # mot-clé: Quitter Le Plein Écran | origine: texte | confiance: haute
    Alors le lecteur reprend sa taille normale
    # mot-clé: Le Lecteur Est En Taille Normale | origine: deduit | confiance: moyenne

# Q1 | « publicité se termine » | action_vague | bloquant
#   question: « Vérifier que la pub ne gêne pas la lecture » : que faut-il vérifier exactement ? Les publicités sont aléatoires (la capture 3 en montre une de 5 s).
#   proposition: on ne vérifie pas la publicité, on la neutralise : attendre sa fin (ou cliquer « Passer » dès que possible), 90 s au maximum, puis vérifier que la vidéo avance
#   réponse: proposition acceptée
# Q2 | « se lance toute seule » | action_vague | non bloquant
#   question: « La vidéo doit avancer normalement (cf capture) » : comment le mesurer ? La capture 3 montre seulement 0:15 / 3:42.
#   proposition: après la publicité, la position avance d'au moins 1 seconde en 3 secondes d'observation, sans clic sur « Lecture »
#   réponse: proposition acceptée
# Q3 | « la vidéo est arrêtée » | attendu_manquant | non bloquant
#   question: le Word ne donne aucun résultat attendu pour la pause, le plein écran et le retour. Que doit-on constater ?
#   proposition: pause = la position n'avance plus ; plein écran = le lecteur occupe l'écran ; retour = le lecteur revient à sa taille d'origine
#   réponse: proposition acceptée
# Q4 | « ouvre la première vidéo » | non_deterministe | non bloquant
#   question: la « première vidéo » des résultats peut être un direct (c'est le cas sur la capture 2), qui ne se met pas en pause ni n'avance comme une vidéo normale. Faut-il l'ignorer ?
#   proposition: ouvrir la première vidéo qui n'est ni un direct ni un Short
#   réponse: proposition acceptée
# Q5 | « a recherché » | dependance | non bloquant
#   question: « Faire une recherche comme dans SC-001 » : ce test doit-il dépendre de l'exécution de SC-001 ?
#   proposition: non, il refait lui-même l'ouverture du site, le refus des cookies et la recherche « lofi », pour pouvoir tourner seul
#   réponse: proposition acceptée
# Q6 | - | etapes_fusionnees | non bloquant
#   question: le Word décrit ce scénario dans un seul paragraphe. Le découpage en 10 étapes ci-dessus correspond-il à votre intention ?
#   proposition: oui, dans l'ordre du paragraphe
#   réponse: proposition acceptée
