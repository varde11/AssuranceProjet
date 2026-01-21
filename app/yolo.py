from ultralytics import YOLO
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
yolo_path = os.path.join(BASE_DIR,"model","best.pt")



model = None

def load_artificats_yolo():
    global model 
    if model is None:
        model = YOLO(yolo_path)


def objet_detection(image_path):

    load_artificats_yolo()

    damage = []
    results = model(image_path,conf=0.1, iou=0.5)
    #result.show()
    
    for result in results:
        boxes = result.boxes  
        for box in boxes:
            class_id = int(box.cls[0]) 
            conf = float(box.conf[0])  
            name = model.names[class_id]

            if conf > 0.1:
                #print(f"Dégât détecté : {name} avec {conf:.2f} de confiance")
                #dico={"damage":name}
                damage.append(name)

    
    #print(damage)
    return damage


# image_path = os.path.join(BASE_DIR,"model","dam5.jpg")
# res=objet_detection(image_path)
# print("damage reçu from yolo:",res)
