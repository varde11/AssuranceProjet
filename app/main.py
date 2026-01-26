from fastapi import FastAPI, UploadFile,File,Depends,HTTPException
from constat import analyse_constat
from yolo_detection import objet_detection,load_artificats_yolo
from rag import final_decision,load_rag_artificats

from schema import Prediction_out,Client_out,Client_In,EnumDecision
from db import get_db,engine
from sqlalchemy.orm import Session
from structure_table import Base,Client,Prediction
from datetime import datetime
import shutil
import os

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Préparation des ressources....")
    Base.metadata.create_all(bind=engine)
    load_artificats_yolo()
    load_rag_artificats()
    print("Préparation terminé")

    yield

    print("Fermeture de l'application, merci de l'avoir essayer ;)")



app = FastAPI(title="It's not just a test",lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "okayy"}


@app.get("/GetClientById",response_model=Client_out)
async def get_client_by_idClient(id_client:int,db:Session=Depends(get_db)):
    client = db.query(Client).filter(Client.id_client == id_client).first()

    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {id_client} est introuvable")
    
    return client


@app.get("/GetAllClient",response_model=list[Client_out])
async def get_all_client(db:Session=Depends(get_db)):
    clients = db.query(Client).all()
    if not clients :
        raise HTTPException(status_code=404,detail="Something went wrong, contact varde for more information, on dirait qu'il n y a aucun client...")
    return clients


@app.get("/GetPredictionByIdPrediction",response_model=Prediction_out)
async def get_prediction_by_idPrediction(id_prediction:int,db:Session=Depends(get_db)):
    prediction = db.query(Prediction).filter(Prediction.id_prediction == id_prediction).first()

    if not prediction:
        raise HTTPException(status_code=404,detail=f"La prédiction d'identifiant {id_prediction} est introuvable.")
    
    return prediction


@app.get("/GetPredictionByIdClient",response_model=list[Prediction_out])
async def get_prediction_by_idClient(id_client:int,db:Session=Depends(get_db)):

    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le clien d'identifiant {id_client} n'existe pas")

    predictions = db.query(Prediction).filter(Prediction.id_client==id_client).all()
    if not predictions:
        return []
    return predictions


@app.get("/GetAllPrediction",response_model=list[Prediction_out])
async def get_all_prediction(db:Session=Depends(get_db)):
    predictions = db.query(Prediction).all()
    if not predictions :
        return []
    return predictions


@app.get("/GetPredictionByDecision",response_model=list[Prediction_out])
async def get_prediction_by_decision(id_client:int,decision:EnumDecision,db:Session=Depends(get_db)):
    
    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le clien d'identifiant {id_client} n'existe pas")


    if decision == "all":
        predictions = db.query(Prediction).filter(Prediction.id_client == id_client).order_by(Prediction.time_stamp.desc()).all()
    else:
        predictions = db.query(Prediction).filter((Prediction.decision_finale == decision)).filter((Prediction.id_client == id_client)).order_by(Prediction.time_stamp.desc()).all()
    

    if not predictions:
        return []
    
    return predictions


@app.post("/Prediction",response_model=Prediction_out)
async def expertise_endpoint(
    id_client:int,
    photo_car: UploadFile = File(...), 
    photo_constat: UploadFile = File(...),
    db:Session=Depends(get_db)
):
    

    client = db.query(Client).filter(Client.id_client==id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {id_client} n'existe pas.")
    
    path_car = f"temp_{photo_car.filename}"
    path_constat = f"temp_{photo_constat.filename}"

    with open(path_car, "wb") as f:
        shutil.copyfileobj(photo_car.file, f)
    with open(path_constat, "wb") as f:
        shutil.copyfileobj(photo_constat.file, f)
    
    damage_list = objet_detection(path_car)
    constat_element = analyse_constat (path_constat)

    result = final_decision (damage_list=damage_list,constat_element=constat_element)

    os.remove(path_car)
    print(path_car,"A bien été supprimé!")
    os.remove(path_constat)
    print(path_constat,"A bien été deleted")
    time_stamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    prediction = Prediction(
        id_client = id_client,
        decodage_texte = result['decodage_texte'],
        exclusions_detectees = result['exclusions_detectees'],
        raison_exclusion = result['raison_exclusion'],
        details_degats = result ['details_degats'],
        decision_finale = result ['decision_finale'],
        time_stamp = datetime.now().strptime(time_stamp_str,"%Y-%m-%d %H:%M:%S")
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


@app.post("/AddClient",response_model=Client_out)
async def add_client(client:Client_In,db:Session=Depends(get_db)):
    client = Client(nom=client.nom)
    db.add(client)
    db.commit()
    db.refresh(client)

    return client


@app.delete("/DeleteClientByIdClient",response_model=Client_out)
async def delete_client_by_idClient(id_client:int,db:Session=Depends(get_db)):

    client = db.query(Client).filter(Client.id_client == id_client).first()

    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {id_client} que vous tentez de supprimer n'existe pas.")
    
    deleted = Client_out.model_validate(client).model_dump()

    db.query(Client).filter(Client.id_client == id_client).delete(synchronize_session=False)
    db.commit()

    return deleted


@app.delete("/DeletePredictionByIdPrediction",response_model=Prediction_out)
async def delete_prediction_by_idPrediction(id_prediction:int,db:Session=Depends(get_db)):

    prediction = db.query(Prediction).filter(Prediction.id_prediction == id_prediction).first()

    if not prediction:
        raise HTTPException(status_code=404,detail=f"La prédiction d'identifiant {id_prediction} que vous tentez de supprimer n'existe pas.")
    
    deleted = Prediction_out.model_validate(prediction).model_dump()

    db.query(Prediction).filter(Prediction.id_prediction == id_prediction).delete(synchronize_session=False)
    db.commit()

    return deleted


@app.delete("/DeletePredictionByIdClient",response_model=list[Prediction_out])
async def delete_prediction_by_idClient(id_client:int,db:Session=Depends(get_db)):

    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code= 404,detail=f"Le client d'identifiant {id_client} n'existe pas")

    predictions = db.query(Prediction).filter(Prediction.id_client == id_client).all()
    if not predictions :
        raise HTTPException(status_code= 404,detail=f"Le client d'identifiant {id_client} n'a fait aucune prédiction")
    
    deleted = [Prediction_out.model_validate(pred).model_dump() for pred in predictions]

    db.query(Prediction).filter(Prediction.id_client == id_client).delete(synchronize_session=False)
    db.commit()

    return deleted


