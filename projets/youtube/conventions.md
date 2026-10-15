# Conventions du projet youtube

Décisions propres à YouTube. Elles s'ajoutent à `commun/conventions.md`.

| # | Sujet | Décision | Origine |
|---|---|---|---|
| C1 | Environnement | Production (www.youtube.com, `hl=fr&gl=FR`) : pas d'environnement de recette | SC-001 Q7 |
| C2 | Comptes | Pas de compte pour l'instant : un scénario qui exige une connexion est `@auto:non` | SC-003 Q6 |
| C3 | Captures du Word | Ce sont des maquettes (libellés et boutons différents du site) : les tests suivent le site réel | SC-001 Q8 (proposition, non répondue) |

## Limites connues

- **Données de production** : les tests dépendent du contenu réel (résultats, publicités).
- **Adresse IP** : selon l'IP (poste, réseau), YouTube affiche le bandeau cookies ou redirige vers
  `consent.youtube.com` ; les deux sont gérés par `Fermer Le Bandeau Cookies` (la redirection n'a pas pu
  être reproduite depuis le conteneur : sélecteur relevé, parcours complet non testé).
