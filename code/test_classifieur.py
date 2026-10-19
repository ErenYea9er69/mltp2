import sys
from classifieur import classer

# Assure l'encodage utf-8 pour le terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

modele = "openai/gpt-oss-20b"
tests = [
    "Ma facture est trop élevée",
    "Je ne peux plus me connecter à mon compte",
    "L'application ne fonctionne plus",
    "Je souhaite changer mon abonnement",
    " bonjour ! ",
]

print("=" * 60)
print(f"TEST DU CLASSIFIEUR AVEC {modele}")
print("=" * 60)

for texte in tests:
    resultat = classer(texte, modele)
    print(f"Ticket    : {texte}")
    print(f"Catégorie : {resultat}\n")
