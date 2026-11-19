import React from 'react';
import { Menu, Droplets, Activity } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, setMobileOpen, bestModel }) {
  const titles = {
    overview: 'System Dashboard & Architecture Overview',
    predict: 'AI Water Potability Assessment & Diagnosis',
    performance: 'Machine Learning Model Benchmarks & Evaluation',
    history: 'Prediction Audit Log & Historical Records',
    standards: 'WHO & EPA Drinking Water Quality Guidelines'
  };

  return (
    <header className="top-header">
      <div className="header-left">
        <button 
          className="mobile-menu-btn" 
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation menu"
        >
          <Menu size={24} />
        </button>
        <div>
          <h2 className="page-heading">{titles[activeTab] || 'Water Quality Prediction'}</h2>
        </div>
      </div>

      <div className="header-right">
        {bestModel && (
          <div className="badge badge-info" style={{ textTransform: 'none', padding: '6px 12px' }}>
            <Activity size={14} />
            <span>Active Model: <strong>{bestModel}</strong></span>
          </div>
        )}
        {activeTab !== 'predict' && (
          <button 
            className="btn btn-primary btn-sm"
            onClick={() => setActiveTab('predict')}
          >
            <Droplets size={14} />
            <span>New Prediction</span>
          </button>
        )}
      </div>
    </header>
  );
}
