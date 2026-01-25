from pydantic import BaseModel,Field
from typing import Literal
from datetime import datetime
from enum import Enum

class Client_out(BaseModel):
    id_client:int = Field(ge=1)
    nom : str 
    model_config = {"from_attributes":True}

class Client_In(BaseModel):
    nom:str

class Prediction_out(BaseModel):
    id_prediction : int  = Field(ge=1)
    id_client : int = Field(ge=1)
    decodage_texte : str
    exclusions_detectees : Literal['True','true','False','false']
    raison_exclusion : str
    details_degats : list[dict]
    decision_finale : Literal['remboursé','non remboursé']
    time_stamp : datetime

    model_config = {"from_attributes": True}
    

class EnumDecision(str,Enum):
    all = "all"
    remboursé  = "remboursé"
    non_remboursé  = "non remboursé"