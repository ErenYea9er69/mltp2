CATEGORIES = ["facturation", "technique", "compte", "commercial"]

def accuracy(vrais, predits):
    """Calcule la part de prédictions correctes (exactitude globale)."""
    if not vrais:
        return 0.0
    return sum(1 for v, p in zip(vrais, predits) if v == p) / len(vrais)

def scores_par_classe(vrais, predits, classes=CATEGORIES):
    """
    Calcule VP, FP, FN, precision, recall et F1 pour chaque classe.
    Gère les divisions par zéro si une classe n'est jamais prédite.
    """
    resultat = {}
    for c in classes:
        vp = sum(1 for v, p in zip(vrais, predits) if v == c and p == c)
        fp = sum(1 for v, p in zip(vrais, predits) if v != c and p == c)
        fn = sum(1 for v, p in zip(vrais, predits) if v == c and p != c)
        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) else 0.0)
        resultat[c] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": vp + fn
        }
    return resultat

def f1_macro(scores):
    """Calcule la moyenne non pondérée des F1-scores de chaque classe."""
    if not scores:
        return 0.0
    return sum(d["f1"] for d in scores.values()) / len(scores)

def taux_invalides(predits, classes=CATEGORIES):
    """Calcule la proportion de réponses hors nomenclature ou malformées."""
    if not predits:
        return 0.0
    return sum(1 for p in predits if p not in classes) / len(predits)

def matrice_confusion(vrais, predits, classes=CATEGORIES):
    """
    Construit la matrice de confusion.
    Lignes = vérité terrain, Colonnes = prédiction (incluant 'invalide').
    """
    colonnes = list(classes) + ["invalide"]
    matrice = {c: {col: 0 for col in colonnes} for c in classes}
    for v, p in zip(vrais, predits):
        if v in matrice:
            col = p if p in colonnes else "invalide"
            matrice[v][col] += 1
    return matrice

def afficher_rapport(etiquette, vrais, predits, classes=CATEGORIES):
    """
    Affiche le rapport détaillé (accuracy, macro-F1, F1 par classe, matrice de confusion)
    et retourne le dictionnaire récapitulatif pour la sérialisation JSON.
    """
    acc = accuracy(vrais, predits)
    sc = scores_par_classe(vrais, predits, classes)
    macro = f1_macro(sc)
    inv = taux_invalides(predits, classes)
    mat = matrice_confusion(vrais, predits, classes)

    print(f"\n=== {etiquette} ===")
    print(f"accuracy  : {acc:.3f}")
    print(f"macro-F1  : {macro:.3f}")
    print(f"invalides : {inv:.3f}\n")
    print(f"{'categorie':<14} {'precision':<10} {'recall':<10} {'F1':<10} {'n':<6}")
    for c in classes:
        p = sc[c]["precision"]
        r = sc[c]["recall"]
        f = sc[c]["f1"]
        n = sc[c]["support"]
        print(f"{c:<14} {p:<10.3f} {r:<10.3f} {f:<10.3f} {n:<6}")

    print("\nConfusion matrix (lignes = vérité, colonnes = prédiction)")
    header = " " * 14 + " ".join(f"{c[:6]:>6}" for c in classes) + "  invali"
    print(header)
    for c in classes:
        ligne = f"{c:<14}"
        for col in classes:
            ligne += f"{mat[c][col]:>6} "
        ligne += f"{mat[c]['invalide']:>7}"
        print(ligne)
    print()

    return {
        "accuracy": acc,
        "macro_f1": macro,
        "macro-F1": macro,
        "taux_invalides": inv,
        "scores_par_classe": sc,
        "matrice_confusion": mat
    }
