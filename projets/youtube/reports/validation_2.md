# Validation 2 — Est-ce bien ce que vous vouliez tester ?

À faire relire par l'auteur du Word (ou via la fiche Word : `w2r fiche-word`). Si c'est correct, cocher « Conforme » puis lancer `/valider`.

## SC-001 — Rechercher une vidéo
_vérifier que la recherche renvoie des résultats pertinents_  
Source : Recette_YouTube_v0.3.docx § SC-001 – Rechercher une vidéo · Persona : `visiteur_anonyme` · Statut : `actif`

**Scénario**
1. Étant donné que le visiteur ouvre le site
2. Et il refuse les cookies si le bandeau s'affiche ⚠️
3. Quand il recherche "lofi"
4. Alors au moins "10" vidéos sont proposées
5. Et au moins un des "3" premiers titres contient "lofi" ⚠️

- [ ] Conforme à l'intention    - [ ] À corriger : …

## SC-002 — Lire une vidéo
_vérifier la lecture automatique, la pause et le plein écran du lecteur_  
Source : Recette_YouTube_v0.3.docx § SC-002 – Lire une vidéo · Persona : `visiteur_anonyme` · Statut : `actif`

**Préconditions**
1. Étant donné que le visiteur a recherché "lofi"
**Scénario**
2. Quand il ouvre la première vidéo des résultats
3. Et une éventuelle publicité se termine ou est passée ⚠️
4. Alors la vidéo se lance toute seule et avance normalement
5. Quand il met la vidéo en pause
6. Alors la vidéo est arrêtée ⚠️
7. Quand il passe en plein écran
8. Alors le lecteur occupe tout l'écran
9. Quand il quitte le plein écran
10. Alors le lecteur reprend sa taille normale

- [ ] Conforme à l'intention    - [ ] À corriger : …

## SC-003 — Ajouter une vidéo à « À regarder plus tard »
_vérifier qu'une vidéo enregistrée apparaît dans la liste « À regarder plus tard »_  
Source : Recette_YouTube_v0.3.docx § SC-003 – Ajouter une vidéo à « À regarder plus tard » · Persona : `utilisateur_connecte` · Statut : `a_valider`

**Préconditions**
1. Étant donné que l'utilisateur est connecté à son compte de test
**Scénario**
2. Quand il ouvre la vidéo de test ⚠️
3. Et il l'enregistre dans "À regarder plus tard"
4. Alors la vidéo figure dans sa liste "À regarder plus tard"

**Nettoyage** : Retirer La Vidéo De La Playlist

- [ ] Conforme à l'intention    - [ ] À corriger : …

