import os
import time
import requests
import streamlit as st
import pandas as pd

# --Config -
st.set_page_config(page_title="Assurance — Expertise", page_icon="🛡️", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")  
TIMEOUT = 10

#  Helpers -
def wait_for_api():
    """Bloque l'UI tant que l'API n'est pas prête"""
    with st.spinner("Démarrage du backend"):
        for _ in range(60): 
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


def decision_badge(decision: str) -> str:
    """Badge HTML couleur selon décision."""
    d = (decision or "").lower()

    # mapping FR + futur EN
    if d in ["remboursé", "rembourse", "approved", "refunded"]:
        color = "#16a34a"  # green
    elif d in ["non remboursé", "non rembourse", "rejected", "not_refunded", "denied"]:
        color = "#dc2626"  # red
    elif d in ["a examiner", "à examiner", "review", "to_review", "needs_review"]:
        color = "#f59e0b"  # orange
    else:
        color = "#2563eb"  # blue fallback

    return f"<span style='background:{color};color:white;padding:6px 12px;border-radius:999px;font-size:14px;font-weight:600'>{decision}</span>"


def render_result(pred: dict):
    st.markdown("### Résultat de l’expertise")

    decision = pred.get("decision_finale")
    st.markdown(decision_badge(str(decision)), unsafe_allow_html=True)

    decodage = pred.get("decodage_texte")
    if decodage:
        st.markdown("#### 🧾 Décodage / Explication")
        st.write(decodage)

   
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("#### 🚗 Détails des dégâts")
        details_degats = pred.get("details_degats")
        if isinstance(details_degats, (list, tuple)):
            st.write(details_degats)
        elif details_degats:
            st.write(details_degats)
        else:
            st.info("Aucun détail de dégâts fourni.")

    with col2:
        st.markdown("#### ⛔ Exclusions détectées")
        exclusions = pred.get("exclusions_detectees")
        if isinstance(exclusions, (list, tuple)):
            st.write(exclusions)
        elif exclusions:
            st.write(exclusions)
        else:
            st.info("Aucune exclusion détectée.")

        raison = pred.get("raison_exclusion")
        if raison:
            st.markdown("#### 🧠 Raison d’exclusion")
            st.write(raison)

    ts = pred.get("time_stamp")
    if ts:
        st.caption(f"Horodatage : {ts}")



ok = wait_for_api()
if not ok:
    st.error("❌ L’API n’est pas disponible. Vérifie que le backend tourne et que /health répond.")
    st.stop()

# -UI 
st.title("🛡️ Nouvelle expertise assurance")
st.caption("Uploader une photo du véhicule + une photo du constat, puis lancer l’analyse (YOLO + RAG).")

try:
    clients = safe_get_json(f"{API_URL}/GetAllClient")
except requests.HTTPError as e:
    st.error(f"Erreur API clients : {e}")
    st.stop()
except Exception as e:
    st.error(f"Impossible de contacter l’API : {e}")
    st.stop()

dfc = pd.DataFrame(clients)
if dfc.empty:
    st.warning("Aucun client en base. Ajoute un client via l’API (/AddClient).")
    st.stop()

# Session state
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("1) Paramètres")

    # Client dropdown
    dfc["label_ui"] = dfc.apply(lambda r: f"{int(r['id_client'])} — {r.get('nom','(sans nom)')}", axis=1)
    client_idx = st.selectbox("👤 Client", options=list(range(len(dfc))), format_func=lambda i: dfc.iloc[i]["label_ui"])
    id_client = int(dfc.iloc[client_idx]["id_client"])

    st.divider()
    st.subheader("2) Upload des documents")

    photo_car = st.file_uploader("📷 Photo véhicule (jpg/png)", type=["jpg", "jpeg", "png"])
    photo_constat = st.file_uploader("📄 Photo constat (jpg/png)", type=["jpg", "jpeg", "png"])

    # Previews
    prev1, prev2 = st.columns(2, gap="medium")
    with prev1:
        if photo_car is not None:
            st.image(photo_car, caption="Véhicule", use_container_width=True)
    with prev2:
        if photo_constat is not None:
            st.image(photo_constat, caption="Constat", use_container_width=True)

    st.divider()
    st.subheader("3) Lancer l’expertise")

    can_run = (photo_car is not None) and (photo_constat is not None) and (id_client >= 1)

    run_btn = st.button("🧠 Lancer l’expertise", type="primary", disabled=not can_run)

    if run_btn:
        with st.status("Analyse en cours…", expanded=True) as status:
            st.write("• Upload des fichiers")
            st.write("• Détection dégâts (YOLO)")
            st.write("• Analyse du constat")
            st.write("• Décision finale (RAG)")

            try:
                files = {
                    "photo_car": (photo_car.name, photo_car.getvalue(), photo_car.type or "image/jpeg"),
                    "photo_constat": (photo_constat.name, photo_constat.getvalue(), photo_constat.type or "image/jpeg"),
                }
                params = {"id_client": id_client}

                r = requests.post(f"{API_URL}/Prediction", params=params, files=files, timeout=120)
                r.raise_for_status()
                pred = r.json()

                st.session_state.last_prediction = pred
                status.update(label="✅ Expertise terminée", state="complete", expanded=False)
                st.success("Prédiction enregistrée en base ✅")

            except requests.HTTPError as e:
                status.update(label="❌ Erreur API", state="error", expanded=True)
                st.error(f"Erreur API : {e}")
                st.write(getattr(e.response, "text", ""))

            except Exception as e:
                status.update(label="❌ Erreur inattendue", state="error", expanded=True)
                st.error(f"Erreur : {e}")

with right:
    st.subheader("Résultat")
    if st.session_state.last_prediction is None:
        st.info("Lance une expertise pour voir le résultat ici.")
    else:
        render_result(st.session_state.last_prediction)

        st.divider()
        st.subheader("Actions")
        if st.button("🧾 Nouvelle expertise (reset)"):
            st.session_state.last_prediction = None
            st.rerun()

        #  historique client
        with st.expander("📚 Voir historique du client (dernier en haut)"):
            try:
                preds_client = safe_get_json(f"{API_URL}/GetPredictionByIdClient", params={"id_client": id_client})
                if preds_client:
                    dfp = pd.DataFrame(preds_client)
                    st.dataframe(dfp, use_container_width=True)
                else:
                    st.info("Aucune prédiction pour ce client.")
            except Exception as e:
                st.error(f"Impossible de charger l’historique : {e}")
