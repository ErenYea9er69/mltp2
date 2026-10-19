import os
import sys
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
load_dotenv("../.env")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("[-] ERREUR: GROQ_API_KEY n'est pas definie.")
    sys.exit(1)

client = Groq(api_key=api_key)

modele = sys.argv[1] if len(sys.argv) > 1 else "openai/gpt-oss-20b"

try:
    print(f"[*] Test de connexion avec le modele '{modele}'...")
    reponse = client.chat.completions.create(
        model=modele,
        messages=[{"role": "user", "content": "Reponds : OK"}]
    )
    print(f"[+] Succes ! Reponse recue de Groq : {reponse.choices[0].message.content}")
except Exception as e:
    print(f"[-] Erreur avec le modele '{modele}': {e}")
