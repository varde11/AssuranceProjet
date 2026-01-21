from fastapi import FastAPI, UploadFile,File
from constat import analyse_constat
from yolo import objet_detection
from rag import final_decision
import shutil
import os

app = FastAPI(title="It's just a test")

@app.post("/TestUploadPhoto")
async def expertise_endpoint(
    photo_car: UploadFile = File(...), 
    photo_constat: UploadFile = File(...)
):
    
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

    return result