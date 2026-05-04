import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../api';
import styles from './Auth.module.css';


export default function Register() {
  const navigate = useNavigate();

  const [form, setForm]     = useState({ id_client: '', nom: '', password: '', confirm: '' });
  const [error, setError]   = useState('');
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }));
    setError('');
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const { id_client, nom, password, confirm } = form;

    if (!id_client.trim() || !nom.trim() || !password || !confirm) {
      setError('Veuillez remplir tous les champs.');
      return;
    }
    if (password !== confirm) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }
    if (password.length < 3) {
      setError('Le mot de passe doit faire au moins 3 caractères.');
      return;
    }

    setLoading(true);
    try {
      await register(id_client.trim(), nom.trim(), password);
      navigate('/login', { state: { registered: true } });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      {/* Left panel */}
      <div className={styles.panel}>



        <div className={styles.panelContent}>
          <div className={styles.logoMark}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M19 17H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11l5 5v5a2 2 0 0 1-2 2z"/>
              <circle cx="7" cy="19" r="2"/><circle cx="17" cy="19" r="2"/>
            </svg>
          </div>
          <h1 className={styles.panelTitle}>VARDE11</h1>
          <p className={styles.panelSub}>
            Rejoignez VARDE11 et bénéficiez d'une analyse de sinistre instantanée grâce à notre IA.
          </p>
          <ul className={styles.features}>
            <li><span className={styles.featureDot}/>Résultats en moins d'une minute</li>
            <li><span className={styles.featureDot}/>Historique complet de vos demandes</li>
            <li><span className={styles.featureDot}/>Sécurisé et confidentiel</li>
          </ul>

          <div className={styles.signature}>
            <span className={styles.signatureName}>VARDE11</span>
            <div className={styles.socialLinks}>
              <a href="https://github.com/varde11" target="_blank" rel="noopener noreferrer" className={styles.socialLink}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                GitHub
              </a>
              <a href="https://www.linkedin.com/in/vannel-evrard-feukou-noukatche90092" target="_blank" rel="noopener noreferrer" className={styles.socialLink}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
                LinkedIn
              </a>
            </div>
          </div>
        </div>




        <div className={styles.panelGrid} />
      </div>

      {/* Right form */}
      <div className={styles.formSide}>
        <div className={styles.formCard}>
          <div className={styles.formHeader}>
            <h2 className={styles.formTitle}>Créer un compte</h2>
            <p className={styles.formSub}>Remplissez les informations ci-dessous</p>
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label className={styles.label} htmlFor="id_client">Identifiant client</label>
              <input
                id="id_client"
                name="id_client"
                type="text"
                className={styles.input}
                placeholder="3 à 10 caractères"
                value={form.id_client}
                onChange={handleChange}
                autoFocus
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="nom">Nom complet</label>
              <input
                id="nom"
                name="nom"
                type="text"
                className={styles.input}
                placeholder="Jean Dupont"
                value={form.nom}
                onChange={handleChange}
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="password">Mot de passe</label>
              <input
                id="password"
                name="password"
                type="password"
                className={styles.input}
                placeholder="••••••••"
                value={form.password}
                onChange={handleChange}
              />
            </div>

            <div className={styles.field}>
              <label className={styles.label} htmlFor="confirm">Confirmer le mot de passe</label>
              <input
                id="confirm"
                name="confirm"
                type="password"
                className={styles.input}
                placeholder="••••••••"
                value={form.confirm}
                onChange={handleChange}
              />
            </div>

            {error && <div className={styles.errorBox}>{error}</div>}

            <button type="submit" className={styles.btnPrimary} disabled={loading}>
              {loading ? <span className="spinner" /> : null}
              {loading ? 'Création…' : 'Créer mon compte'}
            </button>
          </form>

          <p className={styles.switchLink}>
            Déjà un compte ? <Link to="/login">Se connecter</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
