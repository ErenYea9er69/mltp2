import sys
from evaluer import evaluer, charger
from classifieur import CONSIGNE_EXEMPLES

if __name__ == "__main__":
    modele = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-oss-120b"
    etiquette = "gpt-oss-120b + 4 exemples" if modele == "openai/gpt-oss-120b" else f"{modele.split('/')[-1]} + 4 exemples"
    print(f"[*] Évaluation de la consigne enrichie (Few-Shot) : {etiquette}...")
    evaluer(
        modele=modele,
        lignes=charger(),
        consigne=CONSIGNE_EXEMPLES,
        etiquette=etiquette
    )
