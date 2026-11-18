"""Jeu de données d'exemple « Immo » : 800 ventes d'appartements, générées de façon déterministe.

    from immo import charger
    df = charger()        # DataFrame pandas

Colonnes : surface (m²), pieces, etage, ascenseur (0/1), annee_construction, quartier,
distance_metro_m, balcon (0/1), dpe (A à G), prix (euros). Quelques valeurs manquantes
(distance_metro_m, annee_construction) et des valeurs aberrantes, comme dans la vraie vie.
"""
import numpy as np
import pandas as pd

QUARTIERS = {"Centre": 9800, "Gare": 7600, "Université": 6900, "Port": 6400, "Périphérie": 4700}
DPE = list("ABCDEFG")


def charger(n=800, graine=7):
    rng = np.random.default_rng(graine)
    quartier = rng.choice(list(QUARTIERS), size=n, p=[0.18, 0.2, 0.22, 0.15, 0.25])
    surface = np.clip(rng.gamma(4.5, 13, n), 14, 220).round(0)
    pieces = np.clip(np.round(surface / 22 + rng.normal(0, 0.6, n)), 1, 8).astype(int)
    etage = rng.integers(0, 9, n)
    ascenseur = (rng.random(n) < np.where(etage >= 3, 0.75, 0.35)).astype(int)
    annee = rng.integers(1890, 2024, n).astype(float)
    distance = np.clip(rng.exponential(450, n), 30, 3000).round(0)
    balcon = (rng.random(n) < 0.35).astype(int)
    dpe = rng.choice(DPE, size=n, p=[0.04, 0.10, 0.22, 0.28, 0.18, 0.11, 0.07])
    base = np.array([QUARTIERS[q] for q in quartier])
    prix_m2 = (base
               * (1 - 0.00012 * distance)
               * (1 + 0.012 * np.minimum(etage, 6) * ascenseur - 0.01 * etage * (1 - ascenseur))
               * (1 + 0.05 * balcon)
               * (1 - 0.035 * np.array([DPE.index(d) for d in dpe]))
               * (1 + 0.04 * ((annee > 1990) & (annee < 2010)) + 0.08 * (annee >= 2010))
               * rng.lognormal(0, 0.08, n))
    prix = (prix_m2 * surface * (1 - 0.0008 * np.maximum(surface - 60, 0))).round(-3)
    df = pd.DataFrame({"surface": surface, "pieces": pieces, "etage": etage, "ascenseur": ascenseur,
                       "annee_construction": annee, "quartier": quartier, "distance_metro_m": distance,
                       "balcon": balcon, "dpe": dpe, "prix": prix})
    trous = rng.random(n)
    df.loc[trous < 0.06, "distance_metro_m"] = np.nan
    df.loc[(trous > 0.06) & (trous < 0.10), "annee_construction"] = np.nan
    df.loc[[13, 404], "prix"] = df.loc[[13, 404], "prix"] * 10          # deux erreurs de saisie
    return df
