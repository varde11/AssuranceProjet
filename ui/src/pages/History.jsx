import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getPredictions } from '../api';
import styles from './History.module.css';




const FILTERS = [
  { key: 'all',          label: 'Toutes' },
  { key: 'remboursé',    label: 'Remboursées' },
  { key: 'non remboursé',label: 'Non remboursées' },
];

function PredictionCard({ pred, onClick }) {
  const ok = pred.decision_finale === 'remboursé';
  const date = new Date(pred.time_stamp).toLocaleDateString('fr-FR', {
    day: '2-digit', month: 'short', year: 'numeric',
  });
  const time = new Date(pred.time_stamp).toLocaleTimeString('fr-FR', {
    hour: '2-digit', minute: '2-digit',
  });
  const nbDegats = Array.isArray(pred.details_degats) ? pred.details_degats.length : 0;

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.cardTop}>
        <div className={styles.cardId}>
          <span className={styles.cardIdLabel}>Analyse</span>
          <span className={styles.cardIdNum}>#{pred.id_prediction}</span>
        </div>
        <span className={ok ? styles.badgeOk : styles.badgeKo}>
          {ok ? '✓ Remboursé' : '✗ Non remboursé'}
        </span>
      </div>

      <p className={styles.cardAnalysis} title={pred.decodage_texte}>
        {pred.decodage_texte.length > 120
          ? pred.decodage_texte.slice(0, 120) + '…'
          : pred.decodage_texte}
      </p>

      <div className={styles.cardFooter}>
        <div className={styles.cardMeta}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          {date} à {time}
        </div>
        <div className={styles.cardDegats}>
          {nbDegats} dégât{nbDegats > 1 ? 's' : ''}
        </div>
        <div className={styles.cardArrow}>
          Voir le détail →
        </div>
      </div>
    </div>
  );
}

export default function History() {
  const { token } = useAuth();
  const navigate = useNavigate();
  const [filter, setFilter]   = useState('all');
  const [data,   setData]     = useState([]);
  const [loading, setLoading] = useState(true);
  const [error,  setError]    = useState('');

  const fetchData = useCallback(async (f) => {
    setLoading(true);
    setError('');
    try {
      const res = await getPredictions(token, f);
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchData(filter); }, [filter, fetchData]);

  function handleFilterChange(key) {
    setFilter(key);
  }

  const counts = {
    all: data.length,
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Historique</h1>
          <p className={styles.subtitle}>Retrouvez toutes vos demandes d'analyse</p>
        </div>
        <button className={styles.btnRefresh} onClick={() => fetchData(filter)} disabled={loading}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
          </svg>
          Actualiser
        </button>
      </div>

      {/* Tabs */}
      <div className={styles.tabs}>
        {FILTERS.map(f => (
          <button
            key={f.key}
            className={`${styles.tab} ${filter === f.key ? styles.tabActive : ''}`}
            onClick={() => handleFilterChange(f.key)}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {loading && (
        <div className={styles.loadingState}>
          {[1,2,3].map(i => (
            <div key={i} className={`${styles.cardSkeleton} skeleton`} />
          ))}
        </div>
      )}

      {!loading && error && (
        <div className={styles.errorBox}>{error}</div>
      )}

      {!loading && !error && data.length === 0 && (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
          </div>
          <p className={styles.emptyTitle}>Aucune analyse trouvée</p>
          <p className={styles.emptySub}>
            {filter === 'all'
              ? "Vous n'avez pas encore effectué d'analyse."
              : `Aucune analyse de type "${filter}" dans votre historique.`}
          </p>
        </div>
      )}

      {!loading && !error && data.length > 0 && (
        <div className={styles.grid}>
          {data.map(pred => (
            <PredictionCard
              key={pred.id_prediction}
              pred={pred}
              onClick={() => navigate(`/analyse/${pred.id_prediction}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
