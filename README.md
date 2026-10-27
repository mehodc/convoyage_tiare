# Tableau des quarts — convoyage Tiaré

Outil de bord pour la traversée Lombok → Thaïlande, en une seule page sans serveur (`index.html`).

- **Quarts** : répartition automatique équitable (heures, heures de nuit, levers et couchers de soleil), plage de nuit paramétrable, option « nuit uniquement », quarts décalés (relève à mi-quart), modifications quart par quart.
- **Plannings de corvées** (vaisselle, ménage, repas, et tout planning ajouté) : personnes par occurrence, horaires, participants, répartition qui évite les personnes de quart.
- **Repas** : recette et ingrédients par repas, avec autocomplétion depuis l'inventaire ; pré-remplissage possible avec le menu prévu (30 jours).
- **Général** : battement minimum entre deux tâches (toutes tâches confondues) et export agenda (.ics / .csv Google) en choisissant quoi exporter : quarts, repas, corvées.
- **Inventaire** : stock de départ, consommé (repas faits + sorties hors repas), reste, besoins des menus prévus et alertes de manque.

Les données restent dans le navigateur de chaque appareil (localStorage). La section « Sauvegarde et transfert » permet de copier l'état complet d'un téléphone à l'autre. La page fonctionne hors ligne une fois chargée.
