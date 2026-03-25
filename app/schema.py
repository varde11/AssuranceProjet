from pydantic import BaseModel,Field
from typing import Literal,Optional
from datetime import datetime
from enum import Enum



class Client_In(BaseModel):
    id_client:str = Field(...,min_length=3,max_length=10)
    nom:str = Field(...,max_length=20,min_length=3)
    password : str = Field(...,max_length=20,min_length=3)

class Client_Login(BaseModel):
    id_client:str = Field(...,min_length=3,max_length=10)
    password : str = Field(...,max_length=20,min_length=3)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Client_out(BaseModel):
    id_client:str = Field(...,min_length=3,max_length=10)
    nom:str = Field(...,max_length=20,min_length=3)
    total_estimation : int =  Field(default=0)

    model_config = {"from_attributes":True}


class Prediction_out(BaseModel):
    id_prediction : int  = Field(ge=1)
    id_client:str = Field(...,min_length=3,max_length=10)
    decodage_texte : str
    exclusions_detectees : Literal['True','true','False','false']
    raison_exclusion : str
    details_degats : list[dict]
    decision_finale : Literal['remboursé','non remboursé']
    montant_remboursement_total: Optional[str] = None
    time_stamp : datetime

    model_config = {"from_attributes": True}
    
class EnumDecision(str,Enum):
    all = "all"
    remboursé  = "remboursé"
    non_remboursé  = "non remboursé"


class degats(BaseModel):
    piece: str
    couvert: Literal['true','false']
    franchise: str
    montant_remboursement: str


class llm_schema(BaseModel):
    decodage_texte : str
    exclusions_detectees : Literal['True','true','False','false']
    raison_exclusion : str
    details_degats : list[degats]
    decision_finale : Literal['remboursé','non remboursé']
    montant_remboursement_total: Optional[str] = None
    time_stamp : datetime

    model_config = {"from_attributes":True}


