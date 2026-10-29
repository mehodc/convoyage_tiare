"""Construit l'inventaire de l'outil à partir du ticket Pepito du 28/10/2026.

Entrées : ticket-pepito-2026-10-28.csv (109 lignes transcrites du ticket)
          denrees.csv (unité et rayon de chaque denrée)
         marche-2026-10-29.csv (achats du marché, ajoutés au ticket)
Sorties : inventaire.json (inventaire injecté dans l'outil)
Contrôles : nombre de lignes, total et remises comparés au pied du ticket.
"""
import csv, json, sys
from collections import OrderedDict
from pathlib import Path

ICI = Path(__file__).parent
TICKET_LIGNES, TICKET_TOTAL, TICKET_REMISE = 109, 21_822_947, 256_250
RAYONS = {"Féculents", "Légumineuses", "Conserves", "Protéines (congélo)", "Œufs et frais", "Légumes", "Fruits",
          "Petit-déj et boissons", "Épicerie et condiments", "Collations", "Boissons", "Autre"}

lignes = list(csv.DictReader(open(ICI / "ticket-pepito-2026-10-28.csv", encoding="utf-8"), delimiter=";"))
denrees = OrderedDict((d["denree"], d) for d in csv.DictReader(open(ICI / "denrees.csv", encoding="utf-8"), delimiter=";"))

erreurs = []
if len(lignes) != TICKET_LIGNES:
    erreurs.append(f"{len(lignes)} lignes au lieu de {TICKET_LIGNES}")
total = sum(int(l["total"]) for l in lignes)
remise = sum(int(l["remise"]) for l in lignes)
if total != TICKET_TOTAL:
    erreurs.append(f"total {total:,} au lieu de {TICKET_TOTAL:,}")
if remise != TICKET_REMISE:
    erreurs.append(f"remises {remise:,} au lieu de {TICKET_REMISE:,}")
for d in denrees.values():
    if len(d) != 3 or None in d.values() or d["rayon"] not in RAYONS:
        erreurs.append(f"denrees.csv : ligne mal formée pour « {d['denree']} »")
for l in lignes:
    q, pu, t = float(l["qte"]), int(l["prix_unitaire"]), int(l["total"])
    if abs(q * pu - t) > pu * 0.0005 + 1:  # poids imprimé arrondi au gramme
        erreurs.append(f"ligne {l['ligne']} : {q} × {pu} ≠ {t}")
    if l["denree"] and l["denree"] not in denrees:
        erreurs.append(f"ligne {l['ligne']} : denrée inconnue « {l['denree']} »")
if erreurs:
    sys.exit("Contrôle du ticket échoué :\n- " + "\n- ".join(erreurs))

stock = OrderedDict((n, 0.0) for n in denrees)
hors_alim = []
for l in lignes:
    if l["denree"]:
        stock[l["denree"]] += float(l["qte_denree"])
    else:
        hors_alim.append(l["libelle_ticket"])

def ident(prefixe, nom):
    import unicodedata, re
    n = unicodedata.normalize("NFD", nom)
    n = "".join(c for c in n if unicodedata.category(c) != "Mn").lower().strip()
    return prefixe + re.sub(r"[^a-z0-9]+", "-", n)

inv = [{"id": ident("t1-", n), "name": n, "unit": d["unite"], "cat": d["rayon"], "initial": round(stock[n], 3)}
       for n, d in denrees.items() if stock[n] > 0]

# Achats du marché du 29/10/2026 (ajoutés à côté du ticket, sans rien remplacer)
marche = list(csv.DictReader(open(ICI / "marche-2026-10-29.csv", encoding="utf-8"), delimiter=";"))
noms = {i["name"] for i in inv}
for m in marche:
    if m["rayon"] not in RAYONS or len(m) != 6:
        sys.exit(f"marche-2026-10-29.csv : ligne mal formée pour « {m['denree']} »")
    if m["denree"] in noms:
        sys.exit(f"« {m['denree']} » existe déjà dans le ticket : fusionner à la main")
    inv.append({"id": ident("t2-", m["denree"]), "name": m["denree"], "unit": m["unite"], "cat": m["rayon"], "initial": float(m["qte"])})
print(f"Marché : {len(marche)} denrées ajoutées.")

# Stock déjà à bord, quantité à saisir dans l'outil
inv.append({"id": "t3-riz", "name": "Riz", "unit": "kg", "cat": "Féculents", "initial": 0})
json.dump(inv, open(ICI / "inventaire.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Ticket contrôlé : {len(lignes)} lignes, total {total:,} IDR, remises {remise:,} IDR.")
print(f"{len(inv)} denrées dans l'inventaire ; hors alimentation exclus : {', '.join(hors_alim)}.")
