import os
import time
import requests
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clients — Assurance", page_icon="👤", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 10

# -------------------- Helpers --------------------
def wait_for_api():
    with st.spinner("⏳ Connexion au backend…"):
        for _ in range(30):  # ~1 min
            try:
                r = requests.get(f"{API_URL}/health", timeout=3)
                if r.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(2)
    return False

def safe_get_json(url: str, params=None):
    r = requests.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def safe_post_json(url: str, payload: dict):
    r = requests.post(url, json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def safe_delete_json(url: str, params=None):
    r = requests.delete(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def decision_badge(decision: str) -> str:
    d = (decision or "").lower()
    if d in ["remboursé", "rembourse", "approved", "refunded"]:
        color = "#16a34a"
    elif d in ["non remboursé", "non rembourse", "rejected", "denied"]:
        color = "#dc2626"
    elif d in ["a examiner", "à examiner", "review", "to_review", "needs_review"]:
        color = "#f59e0b"
    else:
        color = "#2563eb"
    return f"<span style='background:{color};color:white;padding:4px 10px;border-radius:999px;font-size:13px;font-weight:600'>{decision}</span>"

def render_predictions_table(preds):
    if not preds:
        st.info("Aucune prédiction.")
        return
    df = pd.DataFrame(preds)

    # réordonner si possible
    cols_pref = [
        "time_stamp",
        "id_prediction",
        "id_client",
        "decision_finale",
        "details_degats",
        "exclusions_detectees",
        "raison_exclusion",
        "decodage_texte",
    ]
    cols = [c for c in cols_pref if c in df.columns] + [c for c in df.columns if c not in cols_pref]

    # petite mise en forme: décision badge
    if "decision_finale" in df.columns:
        df["_decision_badge"] = df["decision_finale"].astype(str).apply(lambda x: decision_badge(x))
        st.markdown(
            df[["_decision_badge"]].to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
        st.dataframe(df[cols], use_container_width=True)
    else:
        st.dataframe(df[cols], use_container_width=True)

# -------------------- Gate --------------------
ok = wait_for_api()
if not ok:
    st.error("❌ API indisponible. Vérifie que le backend tourne (et /health répond).")
    st.stop()

# -------------------- UI --------------------
st.title("👤 Clients")
st.caption("Gérer les clients et consulter leur historique de prédictions.")

# Reload clients
def load_clients():
    return safe_get_json(f"{API_URL}/GetAllClient")

# Session state
if "clients_cache" not in st.session_state:
    st.session_state.clients_cache = None

# Header actions
colA, colB = st.columns([0.8, 0.2])
with colA:
    st.subheader("Liste des clients")
with colB:
    if st.button("↻ Rafraîchir", use_container_width=True):
        st.session_state.clients_cache = None
        st.rerun()

# Fetch clients
try:
    if st.session_state.clients_cache is None:
        st.session_state.clients_cache = load_clients()
    clients = st.session_state.clients_cache
except Exception as e:
    st.error(f"Erreur chargement clients : {e}")
    st.stop()

dfc = pd.DataFrame(clients)
if dfc.empty:
    st.warning("Aucun client en base. Ajoute-en un ci-dessous.")
else:
    # Recherche simple
    q = st.text_input("🔎 Rechercher un client (nom ou id)", "")
    df_view = dfc.copy()
    if q.strip():
        qlow = q.lower().strip()
        df_view = df_view[
            df_view.apply(lambda r: qlow in str(r.get("nom", "")).lower() or qlow in str(r.get("id_client", "")).lower(), axis=1)
        ]

    st.dataframe(df_view, use_container_width=True)

st.divider()

# -------------------- Add client --------------------
st.subheader("➕ Ajouter un client")
with st.form("add_client_form", clear_on_submit=True):
    nom = st.text_input("Nom du client", placeholder="Ex: Dupont Jean")
    submitted = st.form_submit_button("Ajouter", type="primary")
    if submitted:
        if not nom.strip():
            st.error("Le nom ne peut pas être vide.")
        else:
            try:
                # Ton endpoint attend un Client_In (json) avec nom
                res = safe_post_json(f"{API_URL}/AddClient", {"nom": nom.strip()})
                st.success(f"Client ajouté ✅ (id={res.get('id_client')})")
                st.session_state.clients_cache = None
                st.rerun()
            except Exception as e:
                st.error(f"Erreur ajout client : {e}")

st.divider()

# -------------------- Client detail + actions --------------------
st.subheader("🧑‍💼 Détails & historique")

if dfc.empty:
    st.info("Ajoute un client pour consulter l’historique.")
    st.stop()

dfc["label_ui"] = dfc.apply(lambda r: f"{int(r['id_client'])} — {r.get('nom','(sans nom)')}", axis=1)
idx = st.selectbox("Choisir un client", options=list(range(len(dfc))), format_func=lambda i: dfc.iloc[i]["label_ui"])
id_client = int(dfc.iloc[idx]["id_client"])
nom_client = str(dfc.iloc[idx].get("nom", ""))

left, right = st.columns([0.55, 0.45], gap="large")

with left:
    with st.container(border=True):
        st.markdown(f"### Client #{id_client}")
        st.write(f"**Nom :** {nom_client}")

        # Delete client
        st.markdown("#### ❌ Supprimer ce client")
        st.caption("Attention : selon ta logique DB, supprimer le client peut échouer si des prédictions existent (contraintes FK).")
        confirm = st.checkbox("Je confirme vouloir supprimer ce client.")
        if st.button("Supprimer", disabled=not confirm, use_container_width=True):
            try:
                res = safe_delete_json(f"{API_URL}/DeleteClientByIdClient", params={"id_client": id_client})
                st.success(f"Client supprimé ✅ (id={res.get('id_client')})")
                st.session_state.clients_cache = None
                st.rerun()
            except requests.HTTPError as e:
                st.error("Suppression impossible (peut-être des prédictions liées).")
                st.write(getattr(e.response, "text", ""))
            except Exception as e:
                st.error(f"Erreur suppression : {e}")

with right:
    with st.container(border=True):
        st.markdown("### 📚 Historique des prédictions")
        # Filtres
        decision_filter = st.selectbox(
            "Filtrer par décision",
            ["all", "remboursé", "non remboursé", "a examiner"],  # prêt pour futur
            index=0
        )

        try:
            preds = safe_get_json(
                f"{API_URL}/GetPredictionByDecision",
                params={"id_client": id_client, "decision": decision_filter}
            )
        except Exception as e:
            st.error(f"Erreur chargement historique : {e}")
            preds = []

        if not preds:
            st.info("Aucune prédiction pour ce client (ou filtre trop restrictif).")
        else:
            render_predictions_table(preds)
