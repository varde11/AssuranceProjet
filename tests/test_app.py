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
from helpers import hash_password

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
        id_client="test1",
        nom="test1",
        password_hash=hash_password("password123")
    )
    
    db.add(fake_client)
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def reset_db():
    """Fixture qui réinitialise la base avant chaque test"""
    setup_database()
    yield


def login_and_get_token(id_client: str, password: str):
    """Helper pour se connecter et obtenir un token"""
    response = client.post("/login", json={"id_client": id_client, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login():
    """Test de la route login"""
    # Test login réussi
    token = login_and_get_token("test1", "password123")
    assert token is not None

    # Test login échoué
    response = client.post("/login", json={"id_client": "test1", "password": "wrong"})
    assert response.status_code == 401


def test_add_and_verify_clients():
    """Test ajout de client et vérification des clients existants"""
    load_rag_artificats()
    load_artificats_yolo()
    # Ajouter un nouveau client test2
    response = client.post("/AddClient", json={"id_client": "test2", "nom": "test2", "password": "password123"})
    assert response.status_code == 200
    added_client = response.json()
    assert added_client["id_client"] == "test2"
    assert added_client["nom"] == "test2"

    # Se connecter avec test1 pour accéder aux routes protégées
    token = login_and_get_token("test1", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Vérifier le client connecté (/Me)
    response = client.get("/Me", headers=headers)
    assert response.status_code == 200
    client_data = response.json()
    assert client_data["id_client"] == "test1"
    assert client_data["nom"] == "test1"

    # Supprimer le client test2 (nécessite peut-être auth, mais supposons que non)
    response = client.delete("/DeleteClientByIdClient?id_client=test2")
    assert response.status_code == 200

    # Vérifier que test2 n'existe plus (si route publique)
    # Note: ajuster selon les routes disponibles


def test_predictions_and_cleanup():
    """Test ajout de client, prédictions et suppression"""
    # Ajouter client test2
    response = client.post("/AddClient", json={"id_client": "test2", "nom": "test2", "password": "password123"})
    assert response.status_code == 200
    added_client = response.json()
    client_id = added_client["id_client"]  # "test2"

    # Se connecter avec test2
    token = login_and_get_token("test2", "password123")
    headers = {"Authorization": f"Bearer {token}"}

    # Ouvrir les fichiers pour la prédiction
    with open("app/model/dam2.jpg", "rb") as photo_car_file, \
         open("app/model/constat_aimable1.jpg", "rb") as photo_constat_file:
        
        # Faire la première prédiction
        files = {
            "photo_car": ("dam2.jpg", photo_car_file, "image/jpeg"),
            "photo_constat": ("constat_aimable1.jpg", photo_constat_file, "image/jpeg")
        }
        response = client.post("/Prediction", files=files, headers=headers)
        assert response.status_code == 200
        prediction1 = response.json()
        assert prediction1["id_prediction"] == 1
        assert prediction1["id_client"] == client_id

        # Faire la deuxième prédiction pour le même client
        photo_car_file.seek(0)  # Remettre au début
        photo_constat_file.seek(0)
        response = client.post("/Prediction", files=files, headers=headers)
        assert response.status_code == 200
        prediction2 = response.json()
        assert prediction2["id_prediction"] == 2
        assert prediction2["id_client"] == client_id

    # Supprimer la prédiction 1 (si route publique)
    response = client.delete("/DeletePredictionByIdPrediction?id_prediction=1")
    assert response.status_code == 200

    # Supprimer le client test2 (ce qui supprime aussi ses prédictions)
    response = client.delete(f"/DeleteClientByIdClient?id_client={client_id}")
    assert response.status_code == 200

    # Vérifier que la prédiction 2 n'existe plus
    response = client.get("/GetPredictionByIdPrediction?id_prediction=2")
    assert response.status_code == 404