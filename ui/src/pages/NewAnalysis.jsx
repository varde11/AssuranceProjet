import { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { submitPrediction } from '../api';
import styles from './NewAnalysis.module.css';

function UploadZone({ label, icon, file, onFile, accept, hint }) {
  const inputRef = useRef();
  const [dragging, setDragging] = useState(false);

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  }

  return (
    <div
      className={`${styles.uploadZone} ${dragging ? styles.dragging : ''} ${file ? styles.hasFile : ''}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={(e) => e.target.files[0] && onFile(e.target.files[0])}
      />

      {file ? (
        <>
          <div className={styles.uploadIconOk}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
          <div className={styles.uploadFileName}>{file.name}</div>
          <div className={styles.uploadHint}>Cliquer pour changer</div>
        </>
      ) : (
        <>
          <div className={styles.uploadIconWrap}>{icon}</div>
          <div className={styles.uploadLabel}>{label}</div>
          <div className={styles.uploadHint}>{hint}</div>
        </>
      )}
    </div>
  );
}

function DecisionBadge({ decision }) {
  const ok = decision === 'remboursé';
  return (
    <span className={ok ? styles.badgeOk : styles.badgeKo}>
      {ok ? '✓ Remboursé' : '✗ Non remboursé'}
    </span>
  );
}

function ResultCard({ result }) {
  const covered   = result.details_degats.filter(d => d.couvert).length;
  const total     = result.details_degats.length;

  return (
    <div className={`${styles.resultCard} fade-in`}>
      <div className={styles.resultHeader}>
        <div>
          <h3 className={styles.resultTitle}>Résultat de l'analyse</h3>
          <p className={styles.resultMeta}>#{result.id_prediction} · {new Date(result.time_stamp).toLocaleString('fr-FR')}</p>
        </div>
        <DecisionBadge decision={result.decision_finale} />
      </div>

      {/* Analyse */}
      <section className={styles.section}>
        <h4 className={styles.sectionTitle}>Analyse du sinistre</h4>
        <p className={styles.decodage}>{result.decodage_texte}</p>
      </section>

      {/* Exclusions */}
      {result.exclusions_detectees === 'true' || result.exclusions_detectees === 'True' ? (
        <div className={styles.exclusionAlert}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <triangle points="12 2 22 22 2 22"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          </svg>
          <strong>Exclusion détectée :</strong> {result.raison_exclusion}
        </div>
      ) : null}

      {/* Damages table */}
      <section className={styles.section}>
        <h4 className={styles.sectionTitle}>
          Détail des dégâts
          <span className={styles.damageCount}>{covered}/{total} pièces couvertes</span>
        </h4>
        <div className={styles.tableWrap}>

          <table className={styles.table}>
            <thead>
              <tr>
                <th>Pièce</th>
                <th>Couverture</th>
                <th>Franchise</th>
                <th>Remboursement</th>
              </tr>
            </thead>
            <tbody>
              {result.details_degats.map((d, i) => (
                <tr key={i}>
                  <td>{d.piece}</td>
                  <td>
                    <span className={d.couvert === 'true' || d.couvert === true ? styles.coveredYes : styles.coveredNo}>
                      {d.couvert === 'true' || d.couvert === true ? 'Oui' : 'Non'}
                    </span>
                  </td>
                  <td className={styles.franchise}>
                    {d.franchise && d.franchise !== 'N/A' ? d.franchise : '—'}
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--success-text)' }}>
                    {d.montant_remboursement && d.montant_remboursement !== '0€'
                      ? d.montant_remboursement
                      : '—'}
                  </td>
                </tr>
              ))}
              <tr className={styles.totalRow}>
                <td colSpan={3}>Total estimé remboursement</td>
                <td className={styles.tdAmount}>
                  {result.montant_remboursement_total || '—'}
                </td>
              </tr>
            </tbody>
          </table>







        </div>
      </section>
    </div>
  );
}

export default function NewAnalysis() {
  const { token } = useAuth();
  const [photoCar,     setPhotoCar]     = useState(null);
  const [photoConstat, setPhotoConstat] = useState(null);
  const [loading,  setLoading]   = useState(false);
  const [result,   setResult]    = useState(null);
  const [error,    setError]     = useState('');
  const [step,     setStep]      = useState('idle'); // idle | analysing | done

  const steps = [
    "Chargement des modèles…",
    "Analyse des dégâts par vision IA…",
    "Lecture du constat amiable…",
    "Application des règles d'assurance…",
    "Génération de la décision…",
  ];
  const [stepIdx, setStepIdx] = useState(0);

  async function handleSubmit() {
    if (!photoCar || !photoConstat) {
      setError('Veuillez fournir les deux photos.');
      return;
    }
    setError('');
    setResult(null);
    setLoading(true);
    setStep('analysing');
    setStepIdx(0);

    // Fake step progression (backend can take 30-60s)
    const interval = setInterval(() => {
      setStepIdx(i => Math.min(i + 1, steps.length - 1));
    }, 8000);

    try {
      const res = await submitPrediction(token, photoCar, photoConstat);
      clearInterval(interval);
      setResult(res);
      setStep('done');
    } catch (err) {
      clearInterval(interval);
      setError(err.message);
      setStep('idle');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setPhotoCar(null);
    setPhotoConstat(null);
    setResult(null);
    setError('');
    setStep('idle');
    setStepIdx(0);
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Nouvelle analyse</h1>
          <p className={styles.subtitle}>Soumettez les photos du sinistre pour obtenir une décision d'indemnisation</p>
        </div>
        {step === 'done' && (
          <button className={styles.btnReset} onClick={reset}>
            Nouvelle analyse
          </button>
        )}
      </div>

      {step !== 'done' && (
        <div className={styles.uploadSection}>


                    {/* Sample downloads */}
          <div className={styles.sampleBanner}>
            <div className={styles.sampleText}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              Pas de photos sous la main ? Téléchargez nos fichiers de test pour essayer l'application.
            </div>
            <div className={styles.sampleLinks}>
              <a href="/samples/vehicule.jpg" download className={styles.sampleBtn}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Véhicule test
              </a>
              <a href="/samples/constat.png" download className={styles.sampleBtn}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Constat test
              </a>
            </div>
          </div>


          <div className={styles.uploadGrid}>
            <UploadZone
              label="Photo du véhicule"
              hint="Glisser-déposer ou cliquer · JPG, PNG, JPEG"
              accept="image/*"
              file={photoCar}
              onFile={setPhotoCar}
              icon={
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              }
            />
            <UploadZone
              label="Photo du constat amiable"
              hint="Glisser-déposer ou cliquer · JPG, PNG, JPEG"
              accept="image/*"
              file={photoConstat}
              onFile={setPhotoConstat}
              icon={
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                  <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>
                </svg>
              }
            />
          </div>

          {error && <div className={styles.errorBox}>{error}</div>}

          {!loading ? (
            <button
              className={styles.btnAnalyse}
              onClick={handleSubmit}
              disabled={!photoCar || !photoConstat}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              Lancer l'analyse
            </button>
          ) : (
            <div className={styles.loadingCard}>
              <div className={styles.loadingRing}>
                <div className={styles.loadingSpinner} />
              </div>
              <div>
                <p className={styles.loadingTitle}>Analyse en cours…</p>
                <p className={styles.loadingStep}>{steps[stepIdx]}</p>
                <p className={styles.loadingNote}>Cette opération peut prendre jusqu'à 60 secondes</p>
              </div>
            </div>
          )}
        </div>
      )}

      {result && <ResultCard result={result} />}
    </div>
  );
}
