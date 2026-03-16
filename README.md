# AssuranceProjet

Projet FastAPI + Streamlit pour la gestion de clients et prédictions d'expertise d'assurance.

## 🚀 Aperçu

Ce projet contient :
- **API FastAPI** (`app/`) exposant des routes pour gérer des clients et des prédictions.
- **Interface Streamlit** (`ui/`) pour interagir avec l'API.
- **Base de données** PostgreSQL via Docker Compose (ou SQLite pour les tests).
- **Machine Learning / vision** : utilisation de modèles YOLO & un système RAG pour analyser des images et générer des prédictions.

---

## 🧩 Architecture

- `app/` : backend FastAPI
  - `main.py` : points d'entrée de l'API
  - `schema.py` : schémas Pydantic
  - `structure_table.py` : définition SQLAlchemy (Client / Prediction)
  - `db.py` : configuration de la DB + session
  - `yolo_detection.py` / `rag.py` / `constat.py` : logique ML et inference
  - `model/` : modèles et images de test (`best.pt`, `dam2.jpg`, `constat_aimable1.jpg`, ...)

- `ui/` : interface Streamlit

- `tests/` : tests pytest

- `docker-compose.yml` : orchestration service (API, UI, Postgres)

---

## ⚙️ Prérequis

- Docker + Docker Compose (recommandé)
- Python 3.11 (pour exécution locale sans Docker)

---

## ✅ Exécution (Docker)

1. Copier les variables d'environnement (exemple) :

```bash
cp .env.example .env
```

2. Construire et démarrer les services :

```bash
docker compose up --build
```

3. Accéder à :
- API FastAPI : http://localhost:8000
- UI Streamlit : http://localhost:8501

---

## 🧪 Exécution des tests (locale)

1. Activer l'environnement virtuel (si présent) :

```powershell
assuranceVenv\Scripts\Activate.ps1
```

2. Installer les dépendances (si nécessaire) :

```bash
pip install -r app/requirements.txt
```

3. Lancer les tests :

```bash
pytest tests/
```

> Les tests utilisent une base SQLite (fichier `dummy.db`) et réinitialisent la base avant chaque test.

---

## 🧠 API Principales

### Clients

- `POST /AddClient` : ajoute un client
- `GET /GetClientById?id_client=<id>` : récupère un client
- `GET /GetAllClient` : récupère tous les clients
- `DELETE /DeleteClientByIdClient?id_client=<id>` : supprime un client (et ses prédictions)

### Prédictions

- `POST /Prediction` (multipart/form-data)
  - `id_client` (query param)
  - `photo_car` (file)
  - `photo_constat` (file)

- `GET /GetPredictionByIdPrediction?id_prediction=<id>`
- `GET /GetPredictionByIdClient?id_client=<id>`
- `DELETE /DeletePredictionByIdPrediction?id_prediction=<id>`

---

## 🧩 Configuration

### Variables d'environnement attendues (Docker)

- `DATABASE_URL` : URL de connexion PostgreSQL
- `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` (dans `docker-compose.yml`)
- `myfirstApiKey` / `API_URL` : pour les appels externes (Groq / LangChain)

---

## 🛠️ Notes d'implémentation

- La base de données en runtime est PostgreSQL (via `db/`), mais les tests utilisent SQLite.
- Le module `yolo_detection` charge un modèle YOLO et doit pouvoir accéder à `app/model/best.pt`.
- Le module `rag.py` dépend de clés API externes (Groq / LangChain).

---

