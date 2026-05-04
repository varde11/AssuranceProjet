import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import styles from './Layout.module.css';

const IconAnalyse = () => <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/></svg>;
const IconHistory = () => <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>;
const IconLogout  = () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>;
const IconMenu    = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>;
const IconClose   = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  function handleLogout() { logout(); navigate('/login'); }
  function handleNav() { setOpen(false); }

  const initials = user?.nom ? user.nom.slice(0, 2).toUpperCase() : '??';

  const navItems = [
    { to: '/nouvelle-analyse', icon: <IconAnalyse />, label: 'Nouvelle analyse', end: true },
    { to: '/historique',       icon: <IconHistory />, label: 'Historique',        end: false },
  ];

  const SidebarContent = () => (
    <>
      <div className={styles.brand}>
        <div className={styles.brandIcon}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 17H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11l5 5v5a2 2 0 0 1-2 2z"/>
            <circle cx="7" cy="19" r="2"/><circle cx="17" cy="19" r="2"/>
          </svg>
        </div>
        <div>
          <div className={styles.brandName}>VARDE11</div>
          <div className={styles.brandSub}>Assurance Auto</div>
        </div>
        <button className={styles.closeBtn} onClick={() => setOpen(false)}><IconClose /></button>
      </div>

      <nav className={styles.nav}>
        <p className={styles.navLabel}>Navigation</p>
        {navItems.map(({ to, icon, label, end }) => (
          <NavLink key={to} to={to} end={end} onClick={handleNav}
            className={({ isActive }) => `${styles.navItem} ${isActive ? styles.navItemActive : ''}`}>
            {icon}<span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className={styles.userBlock}>
        <div className={styles.userAvatar}>{initials}</div>
        <div className={styles.userInfo}>
          <div className={styles.userName}>{user?.nom || '…'}</div>
          <div className={styles.userId}>#{user?.id_client}</div>
        </div>
        <button className={styles.logoutBtn} onClick={handleLogout} title="Se déconnecter">
          <IconLogout />
        </button>
      </div>
    </>
  );

  return (
    <div className={styles.root}>
      {/* Desktop sidebar */}
      <aside className={styles.sidebar}>
        <SidebarContent />
      </aside>

      {/* Mobile overlay */}
      {open && <div className={styles.overlay} onClick={() => setOpen(false)} />}

      {/* Mobile drawer */}
      <aside className={`${styles.drawer} ${open ? styles.drawerOpen : ''}`}>
        <SidebarContent />
      </aside>

      <div className={styles.mainWrap}>
        {/* Mobile top bar */}
        <div className={styles.topBar}>
          <button className={styles.menuBtn} onClick={() => setOpen(true)}><IconMenu /></button>
          <div className={styles.topBarBrand}>
            <div className={styles.topBarIcon}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 17H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h11l5 5v5a2 2 0 0 1-2 2z"/>
                <circle cx="7" cy="19" r="2"/><circle cx="17" cy="19" r="2"/>
              </svg>
            </div>
            VARDE11
          </div>
          <div className={styles.topBarAvatar}>{initials}</div>
        </div>

        <main className={styles.main}><Outlet /></main>
      </div>
    </div>
  );
}