import glob
import json
import os
import sys

# Assure l'encodage utf-8 pour la console Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def charger_resultats():
    """Charge tous les fichiers JSON du dossier resultats/."""
    dossier = os.path.join(os.path.dirname(__file__), "..", "resultats")
    fichiers = glob.glob(os.path.join(dossier, "*.json"))
    resultats = []
    for f in fichiers:
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
                resultats.append(data)
        except Exception as e:
            print(f"[-] Erreur de lecture de {f}: {e}")
    return resultats

def afficher_tableau_comparatif(resultats):
    if not resultats:
        print("Aucun fichier de résultat trouvé dans resultats/.")
        return

    # Tri par Macro-F1 décroissant
    resultats.sort(key=lambda x: x.get("macro_f1", x.get("macro-F1", 0.0)), reverse=True)

    meilleur = resultats[0]
    meilleur_acc = meilleur.get("accuracy", 0.0)

    print("\n" + "=" * 80)
    print("TABLEAU COMPARATIF DES MODÈLES")
    print("=" * 80)
    print(f"{'Modèle':<35} {'Accuracy':<10} {'Macro-F1':<10} {'Écart (tickets)':<18} {'Durée':<10}")
    print("-" * 80)

    for res in resultats:
        nom = res.get("etiquette", res.get("modele", "inconnu"))
        acc = res.get("accuracy", 0.0)
        macro = res.get("macro_f1", res.get("macro-F1", 0.0))
        duree = f"{res.get('duree_s', 0.0):.1f}s"
        ecart_tickets = round((meilleur_acc - acc) * 72)
        ecart_str = "0 (référence)" if ecart_tickets == 0 else f"-{ecart_tickets} tickets"
        print(f"{nom:<35} {acc:<10.3f} {macro:<10.3f} {ecart_str:<18} {duree:<10}")

    print("-" * 80)
    print("Règle de décision : un écart n'est significatif qu'à partir de 5 tickets (~7 pts macro-F1).\n")

def afficher_divergences(resultats):
    if len(resultats) < 2:
        return

    print("=" * 80)
    print("ANALYSE DES DIVERGENCES ENTRE MODÈLES")
    print("=" * 80)

    ids = resultats[0].get("ids", [])
    vrais = resultats[0].get("vrais", [])
    
    chemin_csv = os.path.join(os.path.dirname(__file__), "..", "data", "tickets.csv")
    textes = {}
    if os.path.exists(chemin_csv):
        import csv
        with open(chemin_csv, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                textes[row["id"]] = row["texte"]

    nb_divergences = 0
    for idx, ticket_id in enumerate(ids):
        preds = [res.get("predits", [])[idx] for res in resultats if idx < len(res.get("predits", []))]
        if len(set(preds)) > 1:
            nb_divergences += 1
            vraie_cat = vrais[idx] if idx < len(vrais) else "?"
            texte = textes.get(ticket_id, "")
            print(f"\n[Ticket {ticket_id}] Vérité: <{vraie_cat}>")
            print(f"  Texte: \"{texte}\"")
            for res in resultats:
                nom = res.get("etiquette", res.get("modele", "inconnu"))
                p = res.get("predits", [])[idx] if idx < len(res.get("predits", [])) else "?"
                statut = "[OK]" if p == vraie_cat else "[FAUX]"
                print(f"   - {nom:<32} -> {p:<12} {statut}")

    print(f"\nTotal des tickets divergents : {nb_divergences} / {len(ids)}\n")

if __name__ == "__main__":
    res = charger_resultats()
    afficher_tableau_comparatif(res)
    afficher_divergences(res)
