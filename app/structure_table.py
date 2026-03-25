from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON,TEXT


class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'client'

    id_client = Column (String,primary_key=True,index=True)
    nom = Column (String,nullable=False)
    password_hash = Column(String,nullable=False)
    total_estimation = Column(Integer,default=0)

 
class Prediction(Base):
    __tablename__ = 'prediction'

    id_prediction = Column (Integer,primary_key=True,autoincrement=True,index=True)
    id_client = Column (String,ForeignKey("client.id_client"),nullable=False)
    decodage_texte = Column (TEXT,nullable=False)
    exclusions_detectees = Column(String,nullable=False)
    raison_exclusion = Column(TEXT,nullable=False)
    details_degats = Column(JSON,nullable=False)
    decision_finale = Column(String,nullable=False)
    montant_remboursement_total = Column(String, nullable=True)
    time_stamp = Column(DateTime,nullable=False)
    
    