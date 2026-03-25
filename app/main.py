from fastapi import FastAPI, UploadFile,File,Depends,HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from constat import analyse_constat
from yolo_detection import objet_detection,load_artificats_yolo
from rag import final_decision,load_rag_artificats

from schema import Prediction_out,Client_out,Client_In,EnumDecision,TokenOut,Client_Login
from db import get_db,engine
from sqlalchemy.orm import Session
from sqlalchemy import exists
from structure_table import Base,Client,Prediction
from datetime import datetime,timezone,timedelta
import shutil
import os

from helpers import verify_password,hash_password
from jose import jwt
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



app = FastAPI(title="API Assurance",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("AUTHORIZED_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


security = HTTPBearer()

def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_client = payload.get("sub")
        if not id_client:
            raise HTTPException(status_code=401, detail="Token invalide")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    client = db.query(Client).filter(Client.id_client == id_client).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")

    return client



@app.post("/login", response_model=TokenOut)
def login(client_data: Client_Login, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id_client == client_data.id_client).first()

    if not client or not verify_password(client_data.password, client.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides")

    token = create_access_token({"sub": client.id_client})

    return TokenOut(access_token=token)



@app.get("/health")
def health():
    return {"status": "okayy"}


@app.get("/Me")
def get_client_by_id_client(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} n'existe pas.")
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
async def get_prediction_by_idClient(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):

    client = db.query(Client).filter(Client.id_client == current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le clien d'identifiant {current_client.id_client} n'existe pas")

    predictions = db.query(Prediction).filter(Prediction.id_client==current_client.id_client).all()
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
async def get_prediction_by_decision(decision:EnumDecision,current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):
    
    client = db.query(Client).filter(Client.id_client == current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le clien d'identifiant {current_client.id_client} n'existe pas")


    if decision == "all":
        predictions = db.query(Prediction).filter(Prediction.id_client == current_client.id_client).order_by(Prediction.time_stamp.desc()).all()
    else:
        predictions = db.query(Prediction).filter((Prediction.decision_finale == decision)).filter((Prediction.id_client == current_client.id_client)).order_by(Prediction.time_stamp.desc()).all()
    

    if not predictions:
        return []
    
    return predictions


@app.post("/Prediction",response_model=Prediction_out)
async def expertise_endpoint(
    current_client:Client=Depends(get_current_client),
    photo_car: UploadFile = File(...), 
    photo_constat: UploadFile = File(...),
    db:Session=Depends(get_db)
):
    

    client = db.query(Client).filter(Client.id_client==current_client.id_client).first()
    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} n'existe pas.")
    
    path_car = f"/tmp/temp_{photo_car.filename}"
    path_constat = f"/tmp/temp_{photo_constat.filename}"

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
    

    prediction = Prediction(
        id_client = current_client.id_client,
        decodage_texte = result['decodage_texte'],
        exclusions_detectees = result['exclusions_detectees'],
        raison_exclusion = result['raison_exclusion'],
        details_degats = result ['details_degats'],
        decision_finale = result ['decision_finale'],
        montant_remboursement_total = result.get('montant_remboursement_total'),
        time_stamp = datetime.now().replace(microsecond=0)
    )

    db.add(prediction)
    current_client.total_estimation = current_client.total_estimation+1
    db.commit()
    db.refresh(prediction)
    db.refresh(current_client)

    return prediction



@app.post("/AddClient", response_model=Client_out)
def add_client(client: Client_In, db: Session = Depends(get_db)):
    if db.query(exists().where(Client.id_client == client.id_client)).scalar():
        raise HTTPException(
            status_code=422,
            detail=f"Il existe déjà un client avec l'id {client.id_client}"
        )

    new_client = Client(
        id_client=client.id_client,
        nom=client.nom,
        password_hash=hash_password(client.password),
        total_estimation=0
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return new_client



def _delete_predictions_for_client(id_client, db):
    db.query(Prediction).filter(Prediction.id_client == id_client).delete(synchronize_session=False)
    db.commit()

@app.delete("/DeleteClientByIdClient",response_model=Client_out)
async def delete_client_by_idClient(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):

    client = db.query(Client).filter(Client.id_client == current_client.id_client).first()

    if not client:
        raise HTTPException(status_code=404,detail=f"Le client d'identifiant {current_client.id_client} que vous tentez de supprimer n'existe pas.")
    
    deleted = Client_out.model_validate(client).model_dump()
    _delete_predictions_for_client(current_client.id_client, db)

    db.query(Client).filter(Client.id_client == current_client.id_client).delete(synchronize_session=False)
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
async def delete_prediction_by_idClient(current_client:Client=Depends(get_current_client),db:Session=Depends(get_db)):

    id_client= current_client.id_client
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


