const getBase = () =>
  (window.__ENV__ && window.__ENV__.API_URL) ||
  import.meta.env.VITE_API_URL ||
  'http://localhost:8000';

const authHeaders = (token) => ({
  Authorization: `Bearer ${token}`,
});

// ── Auth ──────────────────────────────────────────────────

export async function login(id_client, password) {
  const res = await fetch(`${getBase()}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_client, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Identifiants invalides');
  }
  return res.json(); // { access_token, token_type }
}

export async function register(id_client, nom, password) {
  const res = await fetch(`${getBase()}/AddClient`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id_client, nom, password }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erreur lors de la création du compte");
  }
  return res.json(); // Client_out
}

export async function getMe(token) {
  const res = await fetch(`${getBase()}/Me`, {
    headers: authHeaders(token),
  });
  if (!res.ok) throw new Error('Session expirée');
  return res.json();
}

// ── Predictions ───────────────────────────────────────────

export async function submitPrediction(token, photoCar, photoConstat) {
  const form = new FormData();
  form.append('photo_car', photoCar);
  form.append('photo_constat', photoConstat);

  const res = await fetch(`${getBase()}/Prediction`, {
    method: 'POST',
    headers: authHeaders(token),
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Erreur lors de l'analyse");
  }
  return res.json(); // Prediction_out
}

export async function getPredictions(token, decision = 'all') {
  const url = `${getBase()}/GetPredictionByDecision?decision=${encodeURIComponent(decision)}`;
  const res = await fetch(url, { headers: authHeaders(token) });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Erreur de récupération');
  }
  return res.json(); // list[Prediction_out]
}

export async function getPredictionById(token, id) {
  const res = await fetch(`${getBase()}/GetPredictionByIdPrediction?id_prediction=${id}`, {
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Prédiction introuvable');
  }
  return res.json(); // Prediction_out
}

export async function deletePrediction(token, id) {
  const res = await fetch(`${getBase()}/DeletePredictionByIdPrediction?id_prediction=${id}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Erreur de suppression');
  }
  return res.json();
}
