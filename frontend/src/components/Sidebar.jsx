import React from 'react';
import { 
  Home, 
  Droplets, 
  BarChart3, 
  History, 
  BookOpen, 
  ShieldCheck,
  X
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, mobileOpen, setMobileOpen, isOnline }) {
  const navItems = [
    { id: 'overview', label: 'Home / Overview', icon: Home },
    { id: 'predict', label: 'Water Prediction', icon: Droplets },
    { id: 'performance', label: 'Model Performance', icon: BarChart3 },
    { id: 'history', label: 'Prediction History', icon: History },
    { id: 'standards', label: 'Standards & Health', icon: BookOpen },
  ];

  const handleNavClick = (id) => {
    setActiveTab(id);
    if (setMobileOpen) setMobileOpen(false);
  };

  return (
    <aside className={`sidebar ${mobileOpen ? 'mobile-open' : ''}`}>
      <div className="sidebar-brand">
        <div className="brand-icon-wrapper">
          <Droplets size={24} />
        </div>
        <div style={{ flex: 1 }}>
          <h1 className="brand-title">AquaPredict AI</h1>
          <p className="brand-sub">Water Quality Intelligence</p>
        </div>
        {mobileOpen && (
          <button 
            className="mobile-menu-btn" 
            onClick={() => setMobileOpen(false)}
            style={{ display: 'block' }}
          >
            <X size={20} />
          </button>
        )}
      </div>

      <nav className="nav-list">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item-btn ${isActive ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
            >
              <Icon size={18} className="nav-icon" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="status-pill">
          <span className={`status-dot ${isOnline ? '' : 'offline'}`}></span>
          <span>{isOnline ? 'System Online (v2.0)' : 'Connecting API...'}</span>
        </div>
        <div style={{ marginTop: '8px', fontSize: '0.7rem', color: '#94a3b8' }}>
          Powered by Scikit-Learn & FastAPI
        </div>
      </div>
    </aside>
  );
}
