# language: fr
@SC-003 @persona:utilisateur_connecte @statut:a_valider @auto:non @playlist
Fonctionnalité: Ajouter une vidéo à « À regarder plus tard »
  Source: Recette_YouTube_v0.3.docx § SC-003 – Ajouter une vidéo à « À regarder plus tard »
  Images: image_04
  Objectif: vérifier qu'une vidéo enregistrée apparaît dans la liste « À regarder plus tard »
  Raison auto: nécessite un compte connecté ; hors périmètre tant que les tests tournent sans compte (Q6)

  Contexte:
    Étant donné que l'utilisateur est connecté à son compte de test
    # mot-clé: Ouvrir Une Session Persona | origine: texte | confiance: moyenne

  Scénario: Enregistrer une vidéo pour plus tard
    Quand il ouvre la vidéo de test
    # mot-clé: NOUVEAU: Ouvrir La Vidéo De Test | origine: texte | confiance: basse
    Et il l'enregistre dans "À regarder plus tard"
    # mot-clé: NOUVEAU: Enregistrer Dans La Playlist | origine: texte, image_04 | confiance: moyenne
    Alors la vidéo figure dans sa liste "À regarder plus tard"
    # mot-clé: NOUVEAU: La Vidéo Est Dans La Playlist | origine: texte | confiance: moyenne
    # nettoyage: NOUVEAU: Retirer La Vidéo De La Playlist

# Q1 | - | securite | non bloquant
#   question: le Word contient un identifiant et un mot de passe en clair (masqués à l'extraction). S'ils sont réels, il faut les faire changer et les retirer du Word. Le test utilisera le rôle « utilisateur connecté » et une session que vous préparez vous-même.
#   proposition: compte Google de test dédié ; vous vous connectez une fois dans un navigateur, la session est enregistrée à part (.auth/)
#   réponse: proposition acceptée
# Q2 | « ouvre la vidéo de test » | non_deterministe | non bloquant
#   question: « Ouvrir une vidéo au hasard » rend le test non reproductible. Quelle vidéo utiliser ?
#   proposition: une vidéo publique stable fixée une fois pour toutes (ni direct, ni Short), dont l'identifiant sera mis dans les variables du projet
#   réponse: proposition acceptée ; identifiant de la vidéo à fournir avant /automatiser
# Q3 | « il l'enregistre » | action_vague | non bloquant
#   question: « Cocher la bonne case » : la capture 4 encadre « À regarder plus tard ». Est-ce bien cette case (et pas « Ma playlist recette ») ?
#   proposition: oui, « À regarder plus tard », comme le titre du scénario
#   réponse: proposition acceptée
# Q4 | « figure dans sa liste » | action_vague | non bloquant
#   question: « Aller dans la bibliothèque, la vidéo doit y être » : la bibliothèque regroupe plusieurs listes. Faut-il vérifier la liste « À regarder plus tard » elle-même ?
#   proposition: oui, ouvrir directement la liste « À regarder plus tard » et y chercher la vidéo
#   réponse: proposition acceptée
# Q5 | - | dependance | non bloquant
#   question: « Penser à supprimer la vidéo de la liste à la fin sinon le test suivant plante » : quel test suivant ? Et si un test précédent a échoué en laissant la vidéo dans la liste ?
#   proposition: retirer la vidéo en fin de test, même en cas d'échec, sans erreur si elle n'y est plus ; la retirer aussi au début si elle y est déjà
#   réponse: proposition acceptée
# Q6 | - | technique | non bloquant
#   question: les tests doivent-ils tourner sans aucun compte ? Ce scénario ne peut pas se faire sans connexion.
#   proposition: oui, pas de compte : SC-003 reste documenté mais n'est pas automatisé
#   réponse: oui, pas de compte pour l'instant (demande du 2026-10-14) ; SC-003 non automatisé
