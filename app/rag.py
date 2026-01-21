import os
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.vectorstores import Chroma

from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from constat import analyse_constat
from yolo import objet_detection

from json_repair import repair_json
import json
import os


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
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cnd_path = os.path.join(BASE_DIR,"ConditionGeneralAssuranceVarde.pdf")
    load_rag_artificats() # A retirer, se chargera au lifespan

    loader = PyPDFLoader(cnd_path)
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
    

    prompt = f"""
   You are an expert in auto insurance investigations, specializing in analyzing complex handwritten accident reports and fraud detection.

    STRICT RULES (MUST BE FOLLOWED):

    1. The damage list detected by vision ({damage_list}) is the definitive source of information.

    2. ALL items in damage_list MUST appear in "details_degats".

    3. NO damage from damage_list should be ignored, even if it was not reported by vehicle A.

    4. If damage is detected by vision but not reported by A, it must be included in the analysis.

    5. All part and damage names in the final JSON MUST be in French.

    - If a term is provided in English, you must translate it.

    - If the exact translation is uncertain, use a generic automotive term in French.
    CONTEXT:

    An accident occurred between car A and car B.

    Applicable insurance rules (extracted from the RAG):

    {vectorstore.similarity_search(query)}

    Declarations from vehicle A regarding vehicle B :
    -   {constat_element['vehicule A']['Observation faite par A']}

    Damage that vehicle A reported having received : 
    -   {constat_element['vehicule A']['Damage subit par A']}

    Declarations from vehicle B regarding vehicle A:
    -   {constat_element['vehicule B']['Observation faite par B']}

    Damage observed on vehicle A by automatic vision (exhaustive list):
    -   {damage_list}

    MISSION:

    - Compare the witness statements with the actual observed damage.

    - Identify any applicable insurance exclusions.

    - Determine whether vehicle A (only vehicle A) is covered by insurance.

    OUTPUT FORMAT — STRICT JSON ONLY:

    {{
    "decodage_texte": "Detailed and logical explanation of the analysis, including any inconsistencies",

    "exclusions_detectees": true/false,

    "raison_exclusion": "None or Specify the reason why the vehicle A cannot be covered by insurance.",

    "details_degats": [
    {{
    "piece": "name of the piece in French",

    "couvert": true/false,

    "franchise": "actual amount in euros or 'None'"

    }}

    ],

    "decision_finale": "remboursé " or "non remboursé"

    }}

    IMPORTANT:

    - The details_degats list must contain exactly all the damages present in damage_list.

    - Returns NO text outside of the JSON, the JSON must be in french language.
    """

    reponse_raw = llm.invoke(prompt)
    reponse = repair_json(reponse_raw.content)
    return json.loads(reponse)


# damage_list = objet_detection("app\model\dam5.jpg")
# constat_element = analyse_constat("app\model\constat2.jpg")

# print(final_decision(damage_list,constat_element))





