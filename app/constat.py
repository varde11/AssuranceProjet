import os
from dotenv import load_dotenv
import base64
from groq import Groq
from json_repair import repair_json
import json

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
def analyse_constat (image_path):

    base64_image = encode_image(image_path)
    load_dotenv()
    client = Groq(api_key=os.getenv("myfirstApiKey"))


    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """
                        
                            Tu es un expert en lecture de manuscrits des accidents automobile en France.
                            Analyse cette image de Constat Amiable d'Accident.

                            Sur l'image, tu retrouveras les info des véhicule A et B. Voici ce que tu fera pour chaque véhicule ( le contenu est à rendre au format JSON, renvoie uniquement le JSON):
                            D'abord, pour les points numéro 11 (Dégâts appartenant au véhicule) et 14 (Observations) relève ce que l'usager a renseigné, si ce qui est renseigné est trop illisible, renvoie None dans la partie du JSON.
                            Format JSON que tu retournes :{"vehicule A": {"Damage subit par A": "", "Observation faite par A": ""}, "vehicule B": {"Damage subit par B": "", "Observation faite par B": ""}} .
                            Il est possible que les informations sur le document soient un peu mal écrites, fais un effort intense pour les comprendre, vérifie si tes réponses au point 14 et 11 ont un sens logique dans le context des accidents automobile.
                        """},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct", 
            temperature=0.1, 
        )
    
    
    reponse = repair_json(chat_completion.choices[0].message.content)
    # Le JSON renvoiyé n'était pas très bien formé
    return json.loads(reponse) # converti le str JSON en dict pyhton

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
resulta=analyse_constat(os.path.join(BASE_DIR,"model","constat_aimable1.jpg"))
print(resulta)

# Exemple de résultat:
#{'vehicule A': {'Damage subit par A': 'Pare choc droit endommage', 'Observation faite Par A': "N'avait pas de clignotant !"}, 
#'vehicule B': {'Damage subit Par B': 'Aile arrière droite pare-choc (bas de caisse)', 'Observation faite Par B': 'Etait sur son telephone !'}}

# print(type(resulta))



#{"vehiculeA": {"DamageSubitParA": "", "OberservationFaiteParA": ""}, "vehiculeB": {"DamageSubitParB": "", "OberservationFaiteParB": ""}}

    


