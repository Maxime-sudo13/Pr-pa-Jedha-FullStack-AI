"""Base de données d'exemple « Brewly » (chaîne de cafés), générée de façon déterministe.

    from brewly import connecter
    con = connecter()          # base SQLite en mémoire, déjà remplie
"""
import random
import sqlite3
from datetime import date, timedelta

PRENOMS = ["Léa", "Hugo", "Inès", "Lucas", "Chloé", "Nathan", "Manon", "Yanis", "Camille", "Adam",
           "Sarah", "Louis", "Jade", "Mehdi", "Emma", "Tom", "Lina", "Noah", "Zoé", "Rayan"]
VILLES = ["Paris", "Lyon", "Bordeaux", "Lille", "Nantes"]
PRODUITS = [
    ("Espresso", "café", 2.2), ("Cappuccino", "café", 3.6), ("Latte", "café", 3.9),
    ("Flat white", "café", 4.1), ("Cold brew", "café", 4.5), ("Thé matcha", "thé", 4.3),
    ("Chaï latte", "thé", 4.2), ("Thé vert", "thé", 2.9), ("Croissant", "viennoiserie", 1.4),
    ("Pain au chocolat", "viennoiserie", 1.6), ("Cookie", "pâtisserie", 2.5), ("Banana bread", "pâtisserie", 3.2),
]
MAGASINS = ["Bastille", "Part-Dieu", "Chartrons", "Vieux-Lille", "Bouffay"]

SCHEMA = """
CREATE TABLE clients   (id INTEGER PRIMARY KEY, prenom TEXT, ville TEXT, inscrit_le TEXT);
CREATE TABLE produits  (id INTEGER PRIMARY KEY, nom TEXT, categorie TEXT, prix REAL);
CREATE TABLE commandes (id INTEGER PRIMARY KEY, client_id INTEGER REFERENCES clients(id), date TEXT, magasin TEXT);
CREATE TABLE lignes    (commande_id INTEGER REFERENCES commandes(id), produit_id INTEGER REFERENCES produits(id), quantite INTEGER);
"""


def remplir(con):
    rng = random.Random(42)
    cur = con.cursor()
    cur.executescript(SCHEMA)
    debut = date(2026, 1, 1)
    for i in range(1, 61):
        cur.execute("INSERT INTO clients VALUES (?, ?, ?, ?)",
                    (i, rng.choice(PRENOMS), rng.choice(VILLES), str(debut + timedelta(days=rng.randint(0, 120)))))
    for i, (nom, cat, prix) in enumerate(PRODUITS, 1):
        cur.execute("INSERT INTO produits VALUES (?, ?, ?, ?)", (i, nom, cat, prix))
    for c in range(1, 501):
        client = rng.randint(1, 55)            # les clients 56 à 60 n'ont jamais commandé
        jour = debut + timedelta(days=rng.randint(0, 180))
        cur.execute("INSERT INTO commandes VALUES (?, ?, ?, ?)", (c, client, str(jour), rng.choice(MAGASINS)))
        for p in rng.sample(range(1, len(PRODUITS) + 1), rng.randint(1, 3)):
            cur.execute("INSERT INTO lignes VALUES (?, ?, ?)", (c, p, rng.choice([1, 1, 1, 2, 2, 3])))
    con.commit()
    return con


def connecter(chemin=":memory:"):
    """Ouvre une connexion SQLite remplie avec les données Brewly."""
    return remplir(sqlite3.connect(chemin))
