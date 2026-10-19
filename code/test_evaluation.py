import os
import sys
import json
from evaluation import (
    accuracy,
    scores_par_classe,
    f1_macro,
    taux_invalides,
    matrice_confusion,
    afficher_rapport
)

# Assure l'encodage utf-8 pour le terminal Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def test_unitaire():
    """Test unitaire avec les 4 tickets du PDF (page 7)."""
    print("=" * 60)
    print("1. TEST UNITAIRE (Exemple du PDF - 4 tickets)")
    print("=" * 60)
    vrais = ["compte", "technique", "compte", "commercial"]
    predits = ["compte", "technique", "commercial", "commercial"]

    acc = accuracy(vrais, predits)
    sc = scores_par_classe(vrais, predits)
    macro = f1_macro(sc)
    print(f"Accuracy attendue: 0.75 | Obtenue: {acc:.2f}")
    print(f"Macro-F1 attendu : 0.583| Obtenu : {macro:.3f}")
    assert acc == 0.75, "Erreur sur l'accuracy unitaire !"
    print("[+] Test unitaire validé avec succès !\n")

def evaluation_sur_fichier_reel():
    """Évalue et affiche les métriques sur les résultats de votre VRAI fichier de tickets."""
    dossier_res = os.path.join(os.path.dirname(__file__), "..", "resultats")
    fichiers = [f for f in os.listdir(dossier_res) if f.endswith(".json")] if os.path.exists(dossier_res) else []

    if not fichiers:
        print("[-] Aucun résultat JSON trouvé dans resultats/. Lancez d'abord evaluer.py.")
        return

    print("=" * 60)
    print("2. ÉVALUATION SUR VOS VRAIES DONNÉES (Fichier de 72 tickets)")
    print("=" * 60)
    
    # On prend le premier modèle ou celui passé en argument
    nom_fichier = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".json") else fichiers[0]
    chemin = os.path.join(dossier_res, nom_fichier)

    with open(chemin, encoding="utf-8") as f:
        data = json.load(f)

    vrais = data.get("vrais", [])
    predits = data.get("predits", [])
    etiquette = data.get("etiquette", nom_fichier)

    if not vrais or not predits:
        print(f"[-] Données incomplètes dans {nom_fichier}")
        return

    print(f"Modèle analysé : {etiquette} ({len(vrais)} tickets réels)")
    afficher_rapport(etiquette, vrais, predits)

if __name__ == "__main__":
    test_unitaire()
    evaluation_sur_fichier_reel()
