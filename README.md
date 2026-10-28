# Tableau des quarts — convoyage Tiaré

Outil de bord pour la traversée Lombok → Thaïlande, en une seule page sans serveur (`index.html`).

- **Quarts** : répartition automatique équitable (heures, heures de nuit, levers et couchers de soleil), plage de nuit paramétrable, option « nuit uniquement », quarts décalés (relève à mi-quart), modifications quart par quart.
- **Plannings de corvées** (vaisselle, ménage, repas, et tout planning ajouté) : personnes par occurrence, horaires, participants, répartition qui évite les personnes de quart.
- **Repas** : recette et ingrédients par repas, avec autocomplétion depuis l'inventaire ; pré-remplissage possible avec le menu prévu (30 jours).
- **Général** : équipage, battement minimum entre deux tâches (toutes tâches confondues) et export agenda (.ics / .csv Google) en choisissant quoi exporter (quarts, repas, corvées), sauvegarde et transfert entre téléphones.
- **Inventaire** : rangement de chaque denrée (avec filtre), stock de départ, consommé (repas faits + sorties hors repas), reste, besoins des menus prévus et alertes de manque.

Les données sont gardées dans le navigateur de chaque téléphone et la page fonctionne hors ligne. Pour travailler à plusieurs, l'onglet **Général › Partage entre téléphones** propose deux voies, qui fusionnent les changements de chacun : pour chaque élément (équipier, repas, quart modifié, denrée…), la modification la plus récente l'emporte.

## Partage sans réseau

« Partager mes changements » crée un fichier `.json` à envoyer par AirDrop, Quick Share ou Bluetooth. Le destinataire choisit « Intégrer un fichier ». Aucun compte ni internet nécessaire.

## Synchronisation en ligne (quand il y a du réseau)

À faire une fois, par une seule personne :

1. Créer un compte et un projet gratuits sur [supabase.com](https://supabase.com).
2. Dans le projet : **SQL Editor › New query**, coller le contenu de [`supabase-setup.sql`](supabase-setup.sql), puis **Run**.
3. Dans **Project Settings › API** : copier l'adresse du projet (`https://xxxx.supabase.co`) et la clé publique (`anon` ou `publishable`).
4. Dans l'outil, onglet **Général › En ligne** : coller l'adresse et la clé, toucher « Créer un code » (code du bateau), puis « Enregistrer la configuration », puis « Enregistrer les changements ».
5. Partager une fois un fichier (voie sans réseau) aux autres téléphones : ils reçoivent la configuration avec, et n'ont plus qu'à toucher « Récupérer les changements ».

Ensuite : « Enregistrer les changements » envoie les siens et récupère ceux des autres ; « Récupérer les changements » ne fait que récupérer.

Sécurité : la table n'est accessible qu'au travers de deux fonctions qui exigent le code du bateau. Toute personne qui connaît l'adresse, la clé publique et le code peut lire et modifier le planning : ne les publie pas (ils ne sont pas dans ce dépôt).

Sur un téléphone neuf, commencer par récupérer ou intégrer avant de modifier quoi que ce soit. La synchronisation en ligne ne fonctionne pas depuis la version claude.ai de la page (le partage par fichier, si).

## Inventaire de départ

L'inventaire de l'outil vient du ticket Pepito Senggigi du 28/10/2026, transcrit ligne par ligne dans [`courses/ticket-pepito-2026-10-28.csv`](courses/ticket-pepito-2026-10-28.csv). `python3 courses/inventaire_depuis_ticket.py` vérifie la transcription contre le pied du ticket (109 lignes, 21 822 947 IDR, 256 250 IDR de remises) et produit `courses/inventaire.json`. Le regroupement des articles en denrées (unités, rayons) est dans [`courses/denrees.csv`](courses/denrees.csv). Les articles hors alimentation (papier toilette, crème solaire, sacs, javel, brosse à dents) sont exclus.
