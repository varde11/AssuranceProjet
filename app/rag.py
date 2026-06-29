import re
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from schema import llm_schema

load_dotenv()

llm = None
CONDITIONS_GENERALES_RAW = None

# Mapping dégâts→articles nécessaires
DAMAGE_ARTICLE_MAP = {
    
    r"windscreen|lunette|vitre|pare.brise|rear.windscreen|glass": ["ARTICLE 4"],
    
    r"bonnet|capot|door|portiere|bumper|pare.choc|fender|aile|mirror|retroviseur|scratch|rayure|dent": ["ARTICLE 8"],
    
    r"engine|moteur|mecanique|boite|direction|train": ["ARTICLE 9"],
    
    r"vol|stolen|theft": ["ARTICLE 5"],
    
    r"fire|incendie|explosion": ["ARTICLE 6"],
}

#déclenchent Article 12
EXCLUSION_KEYWORDS = [
    r"clignotant", r"telephone|téléphone|portable",
    r"alcool|alcoolisé|ivre", r"drogue|stupefiant|stupefiants",
    r"feu rouge|sens interdit|stop|vitesse",
    r"fuite|scappé|scappee", r"permis",
]


def load_conditions():
    global CONDITIONS_GENERALES_RAW
    if CONDITIONS_GENERALES_RAW is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "ConditionGeneralAssuranceVarde.txt")
        with open(path, "r", encoding="utf-8") as f:
            CONDITIONS_GENERALES_RAW = f.read()


def extract_article(text: str, article_name: str) -> str:
    """Extrait un article complet depuis le texte des CG."""

    pattern = rf"({re.escape(article_name)}.*?)(?=ARTICLE \d+|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def get_relevant_articles(damage_list: list, obs_A: str, obs_B: str) -> str:
    """Sélectionne uniquement les articles pertinents selon les dégâts et observations."""
    load_conditions()

    needed_articles = {"ARTICLE 2", "ARTICLE 12"}  

    
    combined_damage = " ".join(damage_list).lower()
    for pattern, articles in DAMAGE_ARTICLE_MAP.items():
        if re.search(pattern, combined_damage, re.IGNORECASE):
            needed_articles.update(articles)

    
    combined_obs = f"{obs_A} {obs_B}".lower()
    for kw in EXCLUSION_KEYWORDS:
        if re.search(kw, combined_obs, re.IGNORECASE):
            needed_articles.add("ARTICLE 12") 
            break

    
    result = []
    for article in sorted(needed_articles, key=lambda x: int(x.split()[1])):
        content = extract_article(CONDITIONS_GENERALES_RAW, article)
        if content:
            result.append(content)

    print(f"Articles extraits : {sorted(needed_articles)}")
    return "\n\n".join(result)


def load_rag_artificats():
    global llm
    if llm is None:
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="qwen/qwen3-32b",
            temperature=0,
        ).with_structured_output(llm_schema)
    load_conditions()


def final_decision(damage_list: list, constat_element: dict):
    load_rag_artificats()

    try:
        obs_A = constat_element["vehicule A"]["Observation faite par A"] or "Aucune observation"
        dmg_A = constat_element["vehicule A"]["Damage subit par A"] or "Non précisé"
        obs_B = constat_element["vehicule B"]["Observation faite par B"] or "Aucune observation"
    except KeyError as e:
        print("KeyError constat:", e)
        obs_A = dmg_A = obs_B = "Non disponible"

    
    regles = get_relevant_articles(damage_list, obs_A, obs_B)

    prompt = f"""
Tu es un expert en assurance automobile. Analyse ce dossier de sinistre et rends une décision précise pour le véhicule A (l'assuré).

═══════════════════════════════════════
RÈGLES APPLICABLES (extraites du contrat VARDE11) :
{regles}
═══════════════════════════════════════

DONNÉES DU SINISTRE :

Dégâts détectés par vision IA sur le véhicule A (liste DÉFINITIVE) :
{damage_list}

Dégâts que le conducteur A déclare avoir subis :
{dmg_A}

Ce que le conducteur A a observé pendant l'accident:
{obs_A}

Ce que le conducteur B a observé  pendant l'accident :
{obs_B}

═══════════════════════════════════════
INSTRUCTIONS :

ÉTAPE 1 — TRADUCTION DES DÉGÂTS
- bonnet-dent → capot (bosse)
- Rear-windscreen-Damage → lunette arrière
- windscreen-damage → pare-brise avant
- door-dent → portière (bosse)
- bumper-dent → pare-choc (bosse)
- fender-dent → aile (bosse)
- mirror-damage → rétroviseur
- headlight-damage → optique de phare
- scratch → rayure
Autre terme : traduis en français automobile courant.

ÉTAPE 2 — EXCLUSIONS (Article 12)
RÈGLE FONDAMENTALE : les observations du conducteur A décrivent ce qu'il a vue durant l'accident. Si A écrit "il a bougé", il parle de B.

Une exclusion s'applique au véhicule A UNIQUEMENT dans ces deux cas :
- CAS 1 : Le conducteur A est accusé d'une faute
  
- CAS 2 : Un rapport de police ou document officiel mentionne une faute du conducteur A

Dans tous les autres cas → exclusions_detectees="False", raison_exclusion="Aucune exclusion détectée"

Exemples concrets :
- obs_A contient juste "il n'a pas respecté le code de la route" → décrit B → PAS une exclusion pour A

- obs_B contient "A était en état d'ivresse" → décrit A → exclusion pour A

ÉTAPE 3 — ANALYSE PIÈCE PAR PIÈCE
Pour chaque élément de damage_list :
- Si exclusion sur A → couvert="false", franchise="N/A", montant_remboursement="0€"
- Lunette arrière / pare-brise / vitre → Article 4
  * En réseau agréé : franchise="0€", montant jusqu'à 600€ (lunette), 800€ (pare-brise)
  * Hors réseau : franchise="50€", déduis du montant
- Capot / aile / portière / pare-choc / rétroviseur → Article 8
  * obs_B mentionne explicitement que B est 100% responsable → franchise="0€"
  * Sinon → franchise="450€", déduis du montant, plafond 2000€ par pièce

ÉTAPE 4 — TOTAL
Somme des montant_remboursement des pièces couvertes = montant_remboursement_total
Si non remboursé → montant_remboursement_total="0€"

RÈGLES ABSOLUES :
- Tous les éléments de damage_list dans details_degats
- Noms de pièces en français uniquement
- Cohérence obligatoire entre exclusions/decision/montant
- JSON uniquement, aucun texte autour
═══════════════════════════════════════
"""
    
    print("damage A:",dmg_A)
    print("*************************")
    print("obA:",obs_A)
    print("********************************")
    print("obB",obs_B)

    reponse_raw = llm.invoke(prompt)
    return llm_schema.model_validate(reponse_raw).model_dump()