import csv
import json
import os
import sys
import time
from classifieur import CONSIGNE, classer
from evaluation import afficher_rapport

# Assure l'encodage utf-8 pour le terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PAUSE = 2.1  # 30 requêtes/minute au maximum pour respecter le quota Groq gratuit

def charger(chemin=None):
    """Lit le fichier tickets et retourne la liste des tickets sous forme de dictionnaires."""
    candidats = [
        chemin,
        os.path.join(os.path.dirname(__file__), "..", "tickets - tickets.csv"),
        os.path.join(os.path.dirname(__file__), "..", "data", "tickets.csv"),
        "tickets - tickets.csv",
        "../tickets - tickets.csv",
        "data/tickets.csv",
        "../data/tickets.csv",
    ]
    chemin_trouve = next((c for c in candidats if c and os.path.exists(c)), None)
    if not chemin_trouve:
        raise FileNotFoundError("Fichier de tickets introuvable (recherché dans 'tickets - tickets.csv' et 'data/tickets.csv').")
    
    with open(chemin_trouve, encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    print(f"[*] Fichier chargé : {chemin_trouve} ({len(lignes)} tickets)")
    return lignes

def evaluer(modele, lignes, consigne=CONSIGNE, etiquette=None):
    """
    Évalue un modèle sur les tickets avec une pause de sécurité de 2,1s entre chaque appel.
    Affiche le rapport complet et enregistre les résultats au format JSON dans resultats/.
    """
    etiquette = etiquette or modele
    vrais, predits = [], []
    debut = time.time()
    total = len(lignes)

    print(f"[*] Démarrage de l'évaluation : {etiquette} ({total} tickets)...")

    for i, ligne in enumerate(lignes, 1):
        prediction = classer(ligne["texte"], modele, consigne=consigne)
        predits.append(prediction)
        vrais.append(ligne["categorie"])
        print(f"[{i:02d}/{total:02d}] {ligne['id']}: Réel='{ligne['categorie']}' | Prédit='{prediction}'")
        time.sleep(PAUSE)

    # Calcul et affichage du rapport
    resume = afficher_rapport(etiquette, vrais, predits)
    resume.update(
        modele=modele,
        etiquette=etiquette,
        duree_s=round(time.time() - debut, 1),
        predits=predits,
        vrais=vrais,
        ids=[l["id"] for l in lignes]
    )

    # Sauvegarde du JSON dans resultats/<etiquette_nettoyee>.json
    dossier_resultats = os.path.join(os.path.dirname(__file__), "..", "resultats")
    os.makedirs(dossier_resultats, exist_ok=True)
    nom_fichier = etiquette.replace("/", "_").replace(" ", "_") + ".json"
    chemin_sauvegarde = os.path.join(dossier_resultats, nom_fichier)

    with open(chemin_sauvegarde, "w", encoding="utf-8") as f:
        json.dump(resume, f, indent=2, ensure_ascii=False)

    print(f"[+] Résultat sauvegardé dans : {chemin_sauvegarde}")
    return resume

if __name__ == "__main__":
    modele = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-oss-20b"
    fichier_csv = sys.argv[2] if len(sys.argv) > 2 else None
    lignes = charger(fichier_csv)
    evaluer(modele, lignes)
