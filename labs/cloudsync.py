"""Base de connaissances d'exemple : le support client de « CloudSync », un service de stockage en ligne.

    from cloudsync import DOCS, QUESTIONS_TEST
"""

DOCS = [
    {"id": "tarifs", "titre": "Offres et tarifs",
     "texte": "CloudSync propose trois offres. L'offre Gratuite inclut 5 Go de stockage. L'offre Plus coûte 4,99 euros par mois "
              "et inclut 200 Go. L'offre Pro coûte 11,99 euros par mois et inclut 2 To, avec l'historique des versions sur 180 jours. "
              "Le paiement annuel donne deux mois offerts."},
    {"id": "partage", "titre": "Partager un fichier",
     "texte": "Pour partager un fichier, fais un clic droit puis choisis Partager. Tu peux créer un lien public ou inviter une "
              "personne par e-mail. Les liens publics peuvent être protégés par un mot de passe et expirer à une date choisie, "
              "uniquement avec les offres Plus et Pro."},
    {"id": "synchro", "titre": "Problèmes de synchronisation",
     "texte": "Si un fichier ne se synchronise pas, vérifie d'abord ta connexion internet, puis que l'application est à jour. "
              "Les fichiers de plus de 50 Go ne sont pas synchronisés. Les noms de fichiers contenant les caractères deux-points "
              "ou point d'interrogation sont refusés sous Windows. Redémarrer l'application résout la plupart des blocages."},
    {"id": "corbeille", "titre": "Récupérer un fichier supprimé",
     "texte": "Les fichiers supprimés restent dans la corbeille pendant 30 jours avec l'offre Gratuite et 180 jours avec l'offre Pro. "
              "Pour restaurer un fichier, ouvre la corbeille depuis le site web, sélectionne le fichier puis clique sur Restaurer."},
    {"id": "securite", "titre": "Sécurité et chiffrement",
     "texte": "Tous les fichiers sont chiffrés en AES-256 sur nos serveurs, et les transferts utilisent TLS. La double "
              "authentification se configure dans Paramètres, Sécurité. Nos serveurs sont situés en Union européenne, "
              "et CloudSync respecte le RGPD."},
    {"id": "resiliation", "titre": "Résilier son abonnement",
     "texte": "Tu peux résilier à tout moment depuis Paramètres, Abonnement. La résiliation prend effet à la fin de la période payée. "
              "Si ton stockage dépasse alors 5 Go, tes fichiers restent consultables mais tu ne peux plus en ajouter."},
    {"id": "appareils", "titre": "Appareils compatibles",
     "texte": "L'application CloudSync fonctionne sous Windows 10 et plus récent, macOS 12 et plus récent, iOS, Android et Linux "
              "(Ubuntu et Fedora). Un même compte peut être connecté sur 3 appareils avec l'offre Gratuite et sans limite avec Plus et Pro."},
    {"id": "contact", "titre": "Contacter le support",
     "texte": "Le support répond par chat de 9 heures à 19 heures du lundi au vendredi. Les clients Pro ont accès à un support "
              "prioritaire par téléphone. Le délai moyen de réponse par e-mail est de 24 heures."},
]

QUESTIONS_TEST = [
    {"question": "Combien coûte l'offre Pro par mois ?", "pertinents": ["tarifs"]},
    {"question": "Comment protéger un lien de partage par mot de passe ?", "pertinents": ["partage"]},
    {"question": "Mon fichier ne se synchronise pas, que faire ?", "pertinents": ["synchro"]},
    {"question": "Combien de temps les fichiers supprimés restent dans la corbeille ?", "pertinents": ["corbeille"]},
    {"question": "Mes fichiers sont-ils chiffrés ?", "pertinents": ["securite"]},
    {"question": "Comment résilier mon abonnement ?", "pertinents": ["resiliation"]},
    {"question": "L'application fonctionne-t-elle sous Linux ?", "pertinents": ["appareils"]},
    {"question": "Quels sont les horaires du support par chat ?", "pertinents": ["contact"]},
]
