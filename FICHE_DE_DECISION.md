# FICHE DE DÉCISION — CHOIX DU MODÈLE DE ROUTAGE DE TICKETS

**Auteur :** Binôme 3e année DSI  
**Date :** 19 octobre 2026  
**Projet :** Automatisation du routage des tickets du service client (Machine Learning Appliqué — Atelier 2)

---

## 1. Contexte & Protocole d'Évaluation

* **Tâche & Jeu de test :** Routage automatique des tickets clients vers 4 équipes (`facturation`, `technique`, `compte`, `commercial`). Jeu de test de **72 tickets annotés à la main**, reflétant le langage réel des clients (SMS, fautes, absence d'accents) avec classes volontairement déséquilibrées (`facturation` 30,6 %, `technique` 27,8 %, `compte` 22,2 %, `commercial` 19,4 %).
* **Métrique de décision :** **Macro-F1**, fixée **avant** de consulter les résultats. Le macro-F1 accorde un poids équivalent (25 %) à chaque catégorie, empêchant ainsi de masquer de mauvais résultats sur les classes minoritaires (`commercial`), contrairement à l'Accuracy.
* **Seuil de significativité retenu :** 1 ticket = 1,4 point. Un modèle n'est déclaré supérieur qu'à partir de **5 tickets d'écart** (~7 points de macro-F1). En-deçà, l'écart est considéré comme du bruit statistique non mesurable.

---

## 2. Tableau Récapitulatif des Candidats Évalués

| Candidat | Accuracy | Macro-F1 | Taux Invalides | Écart en tickets | Durée totale (72 tickets) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **openai/gpt-oss-20b** (zero-shot) | **0.958** (69/72) | **0.962** | 1,4 % (1/72) | **0 (référence)** | 196.6 s |
| **gpt-oss-120b + 4 exemples** (few-shot) | **0.958** (69/72) | **0.962** | **0.0 %** | **0 (référence)** | 209.6 s |
| **qwen/qwen3.8-27b** (zero-shot) | **0.958** (69/72) | **0.956** | **0.0 %** | **0 (référence)** | **178.7 s** |
| **openai/gpt-oss-120b** (zero-shot) | **0.917** (66/72) | **0.918** | **0.0 %** | -3 tickets | 198.7 s |

---

## 3. Analyse des Résultats & Décision

### A. Rôle de la taille du modèle vs le prompting
* Passer de `openai/gpt-oss-20b` à `openai/gpt-oss-120b` (6x plus volumineux) en zero-shot **ne produit aucun gain** : le modèle 120b perd même 3 tickets (Macro-F1 0.918 vs 0.962).
* En revanche, l'ajout de **4 exemples hors jeu de test** (Few-Shot) permet au modèle 120b de rattraper le score maximal (gain de **+3 tickets**, soit **+4,4 points de macro-F1**).
* **Conclusion d'ingénierie :** Le levier principal de performance n'est **pas la taille brute du modèle**, mais la précision de la consigne et le contexte fourni.

### B. Modèle Retenu : `qwen/qwen3.8-27b` (ou `openai/gpt-oss-20b` avec consigne enrichie)
* **Score du modèle retenu (`qwen/qwen3.8-27b`) :** Macro-F1 de **0.956** (69/72 tickets bien classés, 95,8 % d'accuracy).
* **Écart avec les concurrents :** **0 ticket d'écart** avec le meilleur score possible (69/72).
* **Justification du choix (Qualité vs Latence/Coût) :**
  > *« Si deux modèles sont séparés par moins de 5 tickets et que l'un est plus rapide et plus léger, on choisit le modèle léger : le gain de qualité est nul ou non mesurable, tandis que le gain de latence et de coût de calcul est réel et immédiat. »*
  `qwen/qwen3.8-27b` est le plus rapide de tous les candidats testés (178,7 s), dispose d'un taux d'invalides nul (0.0 %) et ne nécessite pas de surcharger le prompt en tokens d'exemples.

---

## 4. Analyse des Risques et Faiblesses Identifiés

1. **Catégorie la plus sensible :**
   * La catégorie `commercial` et les chevauchements avec `facturation` constituent la quasi-totalité des confusions (ex: ticket T004 *"Je paie 40 euros pour un service que j'utilise deux fois par mois"* où 3 modèles sur 4 confondent contestation d'offre commerciale et facture).
2. **Risque sur les messages ultra-courts :**
   * Le ticket T006 (*« stop »*) a provoqué une sortie `invalide` sur `openai-20b`.
3. **Recommandation pour la mise en production :**
   * Implémenter une règle de routage déterministe préalable pour les mots-clés d'arrêt/désabonnement explicites (ex: regex sur `^stop$`).
   * Adopter `qwen/qwen3.8-27b` en production avec un monitoring régulier des cas de litige prix/facture.
