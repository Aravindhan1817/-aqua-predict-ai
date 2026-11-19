import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import OverviewPage from './pages/OverviewPage';
import PredictPage from './pages/PredictPage';
import PerformancePage from './pages/PerformancePage';
import HistoryPage from './pages/HistoryPage';
import StandardsPage from './pages/StandardsPage';
import { api } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(false);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    // Check backend health and fetch initial metrics
    const checkStatus = async () => {
      try {
        await api.checkHealth();
        setIsOnline(true);
      } catch (err) {
        setIsOnline(false);
      }
    };

    const loadMetrics = async () => {
      try {
        const data = await api.getModelPerformance();
        setMetrics(data);
      } catch (err) {
        console.warn('Backend metrics not yet reachable:', err.message);
      }
    };

    checkStatus();
    loadMetrics();

    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const bestModelName = metrics?.best_model || 'Random Forest';

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Sidebar 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        mobileOpen={mobileOpen}
        setMobileOpen={setMobileOpen}
        isOnline={isOnline}
      />

      {/* Main Content Area */}
      <div className="main-wrapper">
        <Header 
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          setMobileOpen={setMobileOpen}
          bestModel={bestModelName}
        />

        <main className="content-body">
          {activeTab === 'overview' && (
            <OverviewPage 
              setActiveTab={setActiveTab} 
              metrics={metrics}
            />
          )}

          {activeTab === 'predict' && (
            <PredictPage 
              onPredictionSuccess={() => {
                // optionally update state
              }}
            />
          )}

          {activeTab === 'performance' && (
            <PerformancePage 
              metrics={metrics}
            />
          )}

          {activeTab === 'history' && (
            <HistoryPage />
          )}

          {activeTab === 'standards' && (
            <StandardsPage />
          )}
        </main>
      </div>
    </div>
  );
}
