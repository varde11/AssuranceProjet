import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app 
from db import get_db
from structure_table import Client, Base
from yolo_detection import load_artificats_yolo
from rag import load_rag_artificats

SQLALCHEMY_DATABASE_URL = "sqlite:///./dummy.db" 


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Nécessaire pour SQLite
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)


def setup_database():
    """Cette fonction réinitialise la base et crée un client test"""
    # Réinitialiser complètement la base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    fake_client = Client(
    
        nom="test1"
    )
    
    db.add(fake_client)
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def reset_db():
    """Fixture qui réinitialise la base avant chaque test"""
    setup_database()
    yield


def test_add_and_verify_clients():
    """Test ajout de client et vérification des clients existants"""
    load_rag_artificats()
    load_artificats_yolo()
    # Ajouter un nouveau client test2
    response = client.post("/AddClient", json={"nom": "test2"})
    assert response.status_code == 200
    added_client = response.json()
    assert added_client["nom"] == "test2"
    # L'id_client devrait être 2 puisque test1 est déjà ajouté dans setup

    # Vérifier les deux clients dans une boucle
    for i in range(1, 3):
        response = client.get(f"/GetClientById?id_client={i}")
        assert response.status_code == 200
        client_data = response.json()
        assert client_data["id_client"] == i
        assert client_data["nom"] == f"test{i}"

    # Supprimer le client test2
    response = client.delete(f"/DeleteClientByIdClient?id_client=2")
    assert response.status_code == 200

    # Vérifier que test2 n'existe plus
    response = client.get("/GetClientById?id_client=2")
    assert response.status_code == 404


def test_predictions_and_cleanup():
    """Test ajout de client, prédictions et suppression"""
    # Ajouter client test2
    response = client.post("/AddClient", json={"nom": "test2"})
    assert response.status_code == 200
    added_client = response.json()
    client_id = added_client["id_client"]  # Devrait être 2

    # Ouvrir les fichiers pour la prédiction
    with open("app/model/dam2.jpg", "rb") as photo_car_file, \
         open("app/model/constat_aimable1.jpg", "rb") as photo_constat_file:
        
        # Faire la première prédiction
        files = {
            "photo_car": ("dam2.jpg", photo_car_file, "image/jpeg"),
            "photo_constat": ("constat_aimable1.jpg", photo_constat_file, "image/jpeg")
        }
        response = client.post("/Prediction", files=files, params={"id_client": client_id})
        assert response.status_code == 200
        prediction1 = response.json()
        assert prediction1["id_prediction"] == 1
        assert prediction1["id_client"] == client_id

        # Faire la deuxième prédiction pour le même client
        photo_car_file.seek(0)  # Remettre au début
        photo_constat_file.seek(0)
        response = client.post("/Prediction", files=files, params={"id_client": client_id})
        assert response.status_code == 200
        prediction2 = response.json()
        assert prediction2["id_prediction"] == 2
        assert prediction2["id_client"] == client_id

    # Supprimer la prédiction 1
    response = client.delete("/DeletePredictionByIdPrediction?id_prediction=1")
    assert response.status_code == 200

    # Supprimer le client test2 (ce qui supprime aussi ses prédictions)
    response = client.delete(f"/DeleteClientByIdClient?id_client={client_id}")
    assert response.status_code == 200

    # Vérifier que la prédiction 2 n'existe plus
    response = client.get("/GetPredictionByIdPrediction?id_prediction=2")
    assert response.status_code == 404