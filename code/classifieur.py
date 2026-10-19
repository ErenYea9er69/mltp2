import json
import os
import time
from dotenv import load_dotenv
from groq import Groq, RateLimitError

# Chargement des variables d'environnement (.env a la racine ou dans le parent)
load_dotenv()
load_dotenv("../.env")

CATEGORIES = ["facturation", "technique", "compte", "commercial"]

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CONSIGNE = """Tu es un agent de tri du service client.
Classe le ticket dans exactement une catégorie :
- facturation : montant, facture, paiement, remboursement.
- technique : un service ne fonctionne pas comme prévu.
- compte : accès au compte ou données personnelles.
- commercial : choix d'offre, abonnement, résiliation.
Si plusieurs catégories semblent possibles, retiens l'intention
principale du client : ce qu'il veut obtenir.
Réponds uniquement par un objet JSON de la forme
{"categorie": "<une des quatre>"}."""

CONSIGNE_EXEMPLES = CONSIGNE + """

Exemples :
"Le geste commercial promis n'est pas sur mon relevé." ->
 {"categorie": "facturation"}
"Je paie chaque mois et rien ne marche depuis jeudi." ->
 {"categorie": "technique"}
"Mon associé doit consulter les mêmes documents." ->
 {"categorie": "compte"}
"Je déménage à l'étranger en septembre." ->
 {"categorie": "commercial"}"""

def classer(texte, modele, consigne=CONSIGNE, temperature=0.0):
    """
    Envoie un ticket au modèle via l'API Groq et retourne la catégorie prédite.
    Gère les RateLimitError par une attente et réessai automatique,
    et retourne 'invalide' si le JSON est corrompu ou la catégorie inconnue.
    """
    # Boucle de réessai en cas de RateLimitError (30 req/min sur le palier gratuit)
    max_retries = 5
    for tentative in range(max_retries):
        try:
            reponse = client.chat.completions.create(
                model=modele,
                temperature=temperature,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": consigne},
                    {"role": "user", "content": texte}
                ],
            )
            break
        except RateLimitError as e:
            if tentative == max_retries - 1:
                return "invalide"
            # Pause de sécurité avant nouvel essai
            time.sleep(3.0)
        except Exception as e:
            return "invalide"
    else:
        return "invalide"

    try:
        data = json.loads(reponse.choices[0].message.content)
        categorie = data.get("categorie", "")
    except (json.JSONDecodeError, AttributeError):
        return "invalide"

    categorie = str(categorie).strip().lower()
    return categorie if categorie in CATEGORIES else "invalide"
