from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import JSON,TEXT


class Base(DeclarativeBase):
    pass

class Client(Base):
    __tablename__ = 'client'

    id_client = Column (Integer,primary_key=True,index=True,autoincrement=True)
    nom = Column (String,nullable=False)


class Prediction(Base):
    __tablename__ = 'prediction'

    id_prediction = Column (Integer,primary_key=True,autoincrement=True,index=True)
    id_client = Column (Integer,ForeignKey("client.id_client"),nullable=False)
    decodage_texte = Column (TEXT,nullable=False)
    exclusions_detectees = Column(String,nullable=False)
    raison_exclusion = Column(TEXT,nullable=False)
    details_degats = Column(JSON,nullable=False)
    decision_finale = Column(String,nullable=False)
    time_stamp = Column(DateTime,nullable=False)
    
    