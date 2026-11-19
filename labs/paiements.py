"""Transactions de paiement en ligne, avec environ 1 % de fraudes, pour le projet d'infrastructure.

    from paiements import charger
    df = charger()            # 10 000 transactions
    df.head()

Colonnes : montant (€), heure (0-23), pays_carte, pays_ip, nb_tx_24h (transactions de la carte
sur les dernières 24 h), anciennete_compte_j, appareil_nouveau (0/1), categorie, fraude (0/1).
"""
import numpy as np
import pandas as pd

PAYS = ["FR", "FR", "FR", "FR", "BE", "DE", "ES", "IT", "GB", "US", "NG", "BR"]
CATEGORIES = ["alimentaire", "mode", "électronique", "voyage", "jeux", "services"]


def charger(n=10000, graine=3):
    rng = np.random.default_rng(graine)
    pays_carte = rng.choice(PAYS, n)
    autre_pays = rng.random(n) < 0.12
    pays_ip = np.where(autre_pays, rng.choice(PAYS, n), pays_carte)
    categorie = rng.choice(CATEGORIES, n, p=[0.3, 0.2, 0.15, 0.1, 0.1, 0.15])
    montant = np.round(np.exp(rng.normal(3.6, 0.9, n)) + np.where(categorie == "électronique", 120, 0), 2)
    heure = rng.choice(24, n, p=np.r_[np.full(6, 0.012), np.full(18, (1 - 0.072) / 18)])
    nb_tx = rng.poisson(1.6, n)
    anciennete = np.round(rng.exponential(420, n)).astype(int)
    appareil = (rng.random(n) < 0.15).astype(int)
    z = (-10.2 + 3.4 * (pays_ip != pays_carte) + 1.4 * np.log1p(montant / 100) + 0.6 * nb_tx
         + 3.0 * (anciennete < 30) + 2.6 * appareil + 2.2 * (heure < 6)
         + 1.6 * np.isin(categorie, ["électronique", "jeux"]))
    fraude = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    return pd.DataFrame({"montant": montant, "heure": heure, "pays_carte": pays_carte, "pays_ip": pays_ip,
                         "nb_tx_24h": nb_tx, "anciennete_compte_j": anciennete, "appareil_nouveau": appareil,
                         "categorie": categorie, "fraude": fraude})
