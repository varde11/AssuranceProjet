import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getPredictionById, deletePrediction } from '../api';
import styles from './PredictionDetail.module.css';



function ConfirmModal({ onConfirm, onCancel, loading }) {
  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h3 className={styles.modalTitle}>Supprimer cette analyse ?</h3>
        <p className={styles.modalText}>
          Cette action est irréversible. L'analyse sera définitivement supprimée.
        </p>
        <div className={styles.modalActions}>
          <button className={styles.btnCancel} onClick={onCancel} disabled={loading}>
            Annuler
          </button>
          <button className={styles.btnDelete} onClick={onConfirm} disabled={loading}>
            {loading ? <span className="spinner" /> : null}
            {loading ? 'Suppression…' : 'Supprimer'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function PredictionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { token } = useAuth();

  const [pred,    setPred]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState('');
  const [showConfirm, setShowConfirm] = useState(false);
  const [deleting,    setDeleting]    = useState(false);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await getPredictionById(token, id);
        setPred(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, token]);

  async function handleDelete() {
    setDeleting(true);
    try {
      await deletePrediction(token, id);
      navigate('/historique');
    } catch (err) {
      setError(err.message);
      setShowConfirm(false);
    } finally {
      setDeleting(false);
    }
  }

  if (loading) {
    return (
      <div className={styles.page}>
        <div className={styles.loadingWrap}>
          <div className="spinner spinner--blue" style={{ width: 32, height: 32 }} />
          <p>Chargement de l'analyse…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.page}>
        <div className={styles.errorBox}>{error}</div>
        <button className={styles.btnBack} onClick={() => navigate('/historique')}>
          ← Retour à l'historique
        </button>
      </div>
    );
  }

  if (!pred) return null;

  const ok = pred.decision_finale === 'remboursé';
  const date = new Date(pred.time_stamp).toLocaleDateString('fr-FR', {
    weekday: 'long', day: '2-digit', month: 'long', year: 'numeric',
  });
  const time = new Date(pred.time_stamp).toLocaleTimeString('fr-FR', {
    hour: '2-digit', minute: '2-digit',
  });
  const hasExclusion = pred.exclusions_detectees === 'true' || pred.exclusions_detectees === 'True';
  const coveredCount = pred.details_degats.filter(d => d.couvert).length;

  return (
    <div className={styles.page}>
      {showConfirm && (
        <ConfirmModal
          onConfirm={handleDelete}
          onCancel={() => setShowConfirm(false)}
          loading={deleting}
        />
      )}

      {/* Breadcrumb */}
      <button className={styles.btnBack} onClick={() => navigate('/historique')}>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Retour à l'historique
      </button>

      {/* Hero header */}
      <div className={`${styles.hero} ${ok ? styles.heroOk : styles.heroKo}`}>
        <div className={styles.heroLeft}>
          <div className={styles.heroId}>Analyse #{pred.id_prediction}</div>
          <div className={styles.heroDate}>{date} à {time}</div>


          {/* <div className={styles.heroDate}>{fmt(pred.date_debut)} → {fmt(pred.date_fin)}</div> */}
          {pred.montant_remboursement_total && pred.montant_remboursement_total !== '0€' && (
            <div className={styles.heroMontant}>
              {pred.montant_remboursement_total}
              <span>remboursement estimé</span>
            </div>
          )}


          <div className={ok ? styles.heroDecisionOk : styles.heroDecisionKo}>
            {ok ? '✓ Dossier remboursé' : '✗ Dossier non remboursé'}
          </div>
        </div>



        <div className={styles.heroStats}>
          <div className={styles.stat}>
            <div className={styles.statNum}>{pred.details_degats.length}</div>
            <div className={styles.statLabel}>Dégâts détectés</div>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <div className={styles.statNum}>{coveredCount}</div>
            <div className={styles.statLabel}>Pièces couvertes</div>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.stat}>
            <div className={styles.statNum}>{hasExclusion ? '1' : '0'}</div>
            <div className={styles.statLabel}>Exclusion(s)</div>
          </div>
        </div>
      </div>



      {/* Content grid */}
      <div className={styles.content}>

        {/* Analysis text */}
        <section className={styles.card}>
          <h2 className={styles.cardTitle}>
            <span className={styles.cardTitleIcon}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </span>
            Analyse du sinistre
          </h2>
          <p className={styles.analysisText}>{pred.decodage_texte}</p>
        </section>

        {/* Exclusion */}
        {hasExclusion && (
          <section className={styles.exclusionCard}>
            <div className={styles.exclusionHeader}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              Exclusion de garantie détectée
            </div>
            <p className={styles.exclusionReason}>{pred.raison_exclusion}</p>
          </section>
        )}

        {/* Damage table */}
        <section className={styles.card}>
          <h2 className={styles.cardTitle}>
            <span className={styles.cardTitleIcon}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
              </svg>
            </span>
            Détail des dégâts
            <span className={styles.badge}>{pred.details_degats.length} éléments</span>
          </h2>

          <div className={styles.tableWrap}>




            <table className={styles.table}>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Pièce endommagée</th>
                  <th>Couverture assurance</th>
                  <th>Franchise applicable</th>
                  <th>Remboursement estimé</th>
                </tr>
              </thead>
              <tbody>
                {pred.details_degats.map((d, i) => (
                  <tr key={i}>
                    <td className={styles.tdIdx}>{i + 1}</td>
                    <td className={styles.tdPiece}>{d.piece}</td>
                    <td>
                      <span className={d.couvert === 'true' || d.couvert === true ? styles.coveredYes : styles.coveredNo}>
                        {d.couvert === 'true' || d.couvert === true ? '✓ Oui' : '✗ Non'}
                      </span>
                    </td>
                    <td>
                      {d.franchise && d.franchise !== 'N/A' ? (
                        <span className={styles.franchiseAmount}>{d.franchise}</span>
                      ) : (
                        <span className={styles.noFranchise}>—</span>
                      )}
                    </td>
                    <td className={styles.tdAmount}>
                      {d.montant_remboursement && d.montant_remboursement !== '0€'
                        ? <span className={styles.montantOk}>{d.montant_remboursement}</span>
                        : <span className={styles.noFranchise}>—</span>
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>




          </div>
        </section>

        {/* Delete action */}
        <div className={styles.dangerZone}>
          <div>
            <div className={styles.dangerTitle}>Zone de danger</div>
            <div className={styles.dangerSub}>La suppression de cette analyse est irréversible.</div>
          </div>
          <button className={styles.btnDeleteFinal} onClick={() => setShowConfirm(true)}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
            </svg>
            Supprimer cette analyse
          </button>
        </div>
      </div>
    </div>
  );
}

// heroDate