# botmafieux
Le Bot Discord du serveur des Mafieux.

## Fonctionnalités

### Annonces d'anniversaire

Chaque utilisateur peut paramétrer sa date d'anniversaire, un message personnalisé qui sera envoyé à minuit le jour J et l'activation de l'envoi à l'aide de la commande `birthday_set` dans le salon défini.
La fonctionnalité peut être configurée par un administrateur avec la commande `birthday_config` qui peut activer/désactiver la fonctionnalité sur le serveur courant et choisir le salon dans lequel les annonces d'anniversaires seront envoyées.

### Rappels de productivité

Chaque utilisateur peut paramétrer un message à envoyer tous les $x$ jours dans le salon choisi et son activation à l'aide de la commande `productivity_set`. Un message sera envoyé tous les $x$ jours après le dernier message de l'utilisateur dans le salon défini.
La fonctionnalité peut être configurée par un administrateur avec la commande `productivity_config` qui peut activer/désactiver la fonctionnalité sur le serveur courant.

## Commandes

### Commandes utilisateurs

| Commande | Description | Options requises | Options facultatives |
| --- | --- | --- | --- |
| `help` | Afficher la description des commandes | | |
| `birthday_set` | Paramétrer son anniversaire | `date`: date d'anniversaire au format "*JJ/MM*"<br>`announcements`: activation/désactivation des annonces d'anniversaire | `message`: message personnalisé à envoyer à minuit le jour J<br>`for_user`: utilisateur à paramétrer (administrateurs uniquement) |
| `productivity_set` | Paramétrer ses rappels de productivité | `days`: nombre de jours entre chaque rappel<br>`channel`: salon dans lequel envoyer les rappels<br>`enable`: activation/désactivation des rappels de productivité | `message`: message à envoyer<br>`for_user`: utilisateur à paramétrer (administrateurs uniquement) |

### Commandes administrateurs
| Commande | Description | Options requises | Options facultatives |
| --- | --- | --- | --- |
| `birthday_config` | Configurer les annonces d'anniversaire sur le serveur | `enable`: activation/désactivation des annonces d'anniversaire<br>`channel`: salon dans lequel envoyer les annonces d'anniversaire | |
| `productivity_config` | Configurer les rappels de productivité sur le serveur | `enable`: activation/désactivation des rappels de productivité | |
| `reload` | Recharger une fonctionnalité | `feature`: fonctionnalité à recharger | |