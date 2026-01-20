import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma

from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from constat import analyse_constat
from yolo import objet_detection

llm = None
embedding_model = None

def load_rag_artificats():

    global llm,embedding_model

    if llm is None:
        load_dotenv()

        llm = ChatGroq(
            api_key= os.getenv("myfirstApiKey") ,
            model="llama-3.3-70b-versatile", 
            temperature=0.1
        )

    if embedding_model is None:
        embedding_model = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")


def final_decision(damage_list:list,constat_element:dict):

    load_rag_artificats() # A retirer, se chargera au lifespan

    loader = PyPDFLoader("app/ConditionGeneralAssuranceVarde.pdf")
    docs = loader.load()

    for i in docs:
        i.metadata = {
            'auteur':"varde11",
            'page label' : '1'
        }
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    docs_chunk = splitter.split_documents(docs)
    
    vectorstore = Chroma.from_documents(
    documents=docs_chunk,
    embedding=embedding_model 
    )

    query =""

    for dam in damage_list:
        query = query + " " + dam
    
    try :
        query = query + " " + constat_element["vehicule A"]["Observation faite par A"]
        query = query + " " + constat_element["vehicule B"]["Observation faite par B"] 
        # si le dico n'a pas les éléments pointé
        #{"vehicule A": {"Damage subit par A": "", "Observation faite par A": ""}, "vehicule B": {"Damage subit par B": "", "Observation faite par B": ""}}

    except KeyError as e:
        print("Something went wrong:",e)
    #print()
    #print("Look here",vectorstore.similarity_search("bonnet-dent Rear-windscreen-Damage N'avait pas de clignotant ! Etait sur son telephone !",k=2))
    #return query

    prompt = f"""
    Tu es un expert en investigation d'assurances automobiles, spécialisé dans l'analyse de constats manuscrits difficiles et la détection de fraudes.

    RÈGLES STRICTES (À RESPECTER ABSOLUMENT) :
    1. La liste des dégâts détectés par vision ({damage_list}) est la source de vérité exhaustive.
    2. TOUS les éléments présents dans damage_list DOIVENT apparaître dans "details_degats".
    3. AUCUN dégât de damage_list ne doit être ignoré, même s’il n’a pas été déclaré par le véhicule A.
    4. Si un dégât est détecté par vision mais non déclaré par A, il doit apparaître comme tel dans l’analyse.
    5. Tous les noms de pièces et dégâts dans le JSON final DOIVENT être en français.
    - Si un terme est fourni en anglais, tu dois le traduire.
    - Si la traduction exacte est incertaine, utilise un terme automobile générique en français.

    CONTEXTE :
    Un accident a eu lieu entre la voiture A et la voiture B.

    Règles d'assurance applicables (extraites du RAG) :
    {vectorstore.similarity_search(query)}

    Déclarations du véhicule A (JSON brut) :
    {constat_element['vehicule A']}

    Déclarations du véhicule B (JSON brut) :
    {constat_element['vehicule B']}

    Dégâts observés sur le véhicule A par vision automatique (liste exhaustive) :
    {damage_list}

    MISSION :
    - Comparer les déclarations humaines avec les dégâts réellement observés.
    - Identifier toute exclusion d'assurance applicable.
    - Déterminer si le véhicule A est remboursé ou non.

    FORMAT DE SORTIE — JSON STRICT UNIQUEMENT :
    {{
    "decodage_texte": "Explication détaillée et logique de l’analyse, y compris les incohérences éventuelles",
    "exclusions_detectees": true/false,
    "raison_exclusion": "Néant ou justification précise",
    "details_degats": [
        {{
        "piece": "nom de la pièce en français",
        "couvert": true/false,
        "franchise": "montant réel en euros ou 'Néant'"
        }}
    ],
    "decision_finale": "REMBOURSÉ" ou "NON REMBOURSÉ"
    }}

    IMPORTANT :
    - La liste details_degats doit contenir exactement tous les dégâts présents dans damage_list.
    - Ne retourne AUCUN texte hors du JSON.
    """

    reponse = llm.invoke(prompt)

    return reponse.content

damage_list = objet_detection("app\model\dam2.jpg")
constat_element = analyse_constat("app\model\constat_aimable1.jpg")

print(final_decision(damage_list,constat_element))




