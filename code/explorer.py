import csv
import os
import sys
from collections import Counter

# Assure l'encodage utf-8 pour le terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

candidats = [
    sys.argv[1] if len(sys.argv) > 1 else None,
    os.path.join(os.path.dirname(__file__), "..", "tickets - tickets.csv"),
    os.path.join(os.path.dirname(__file__), "..", "data", "tickets.csv"),
    "tickets - tickets.csv",
    "../tickets - tickets.csv",
    "data/tickets.csv",
    "../data/tickets.csv",
]

chemin = next((c for c in candidats if c and os.path.exists(c)), None)
if not chemin:
    print("[-] Erreur : Fichier CSV introuvable.")
    sys.exit(1)

print(f"[*] Analyse du fichier : {chemin}")
with open(chemin, encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

print(f"Total de tickets : {len(lignes)}\n")
for cat, n in Counter(l["categorie"] for l in lignes).most_common():
    print(f"{cat:<13}{n:>3} {100*n/len(lignes):>5.1f} % {'#' * n}")
