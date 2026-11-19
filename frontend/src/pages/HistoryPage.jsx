import React, { useState, useEffect } from 'react';
import { 
  History, 
  Trash2, 
  Download, 
  Search, 
  Eye, 
  ShieldCheck, 
  ShieldAlert, 
  RefreshCw,
  X,
  Calendar,
  AlertTriangle
} from 'lucide-react';
import { api } from '../services/api';

export default function HistoryPage() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [selectedItem, setSelectedItem] = useState(null);
  const [actionMsg, setActionMsg] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const data = await api.getHistory(200);
      setHistory(data);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleDeleteItem = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm(`Delete prediction record #${id}?`)) return;
    try {
      await api.deleteHistoryItem(id);
      setHistory(prev => prev.filter(item => item.id !== id));
      setActionMsg(`Record #${id} successfully deleted.`);
      setTimeout(() => setActionMsg(null), 3000);
      if (selectedItem?.id === id) setSelectedItem(null);
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to delete ALL prediction records? This cannot be undone.')) return;
    try {
      await api.clearAllHistory();
      setHistory([]);
      setActionMsg('All prediction history cleared.');
      setTimeout(() => setActionMsg(null), 3000);
    } catch (err) {
      alert(`Clear failed: ${err.message}`);
    }
  };

  const exportCSV = () => {
    if (history.length === 0) return alert('No history data to export.');
    const headers = [
      'ID', 'Sample Name', 'Timestamp', 'pH', 'Hardness', 'Solids_TDS', 
      'Chloramines', 'Sulfate', 'Conductivity', 'Organic_Carbon', 
      'Trihalomethanes', 'Turbidity', 'Prediction', 'Status', 'Probability', 'Risk_Level'
    ];
    const rows = history.map(item => [
      item.id,
      `"${item.sample_name || 'Water Sample'}"`,
      `"${item.created_at}"`,
      item.ph,
      item.hardness,
      item.solids,
      item.chloramines,
      item.sulfate,
      item.conductivity,
      item.organic_carbon,
      item.trihalomethanes,
      item.turbidity,
      item.prediction,
      item.potability_label,
      item.probability,
      `"${item.risk_level}"`
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `water_prediction_audit_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredHistory = history
    .filter(item => {
      const q = search.toLowerCase();
      const matchesSearch = (
        item.sample_name?.toLowerCase().includes(q) ||
        item.potability_label?.toLowerCase().includes(q) ||
        item.risk_level?.toLowerCase().includes(q) ||
        item.created_at?.toLowerCase().includes(q)
      );
      if (!matchesSearch) return false;
      if (filterStatus === 'safe') return item.prediction === 1;
      if (filterStatus === 'unsafe') return item.prediction === 0;
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'newest') return b.id - a.id;
      if (sortBy === 'oldest') return a.id - b.id;
      if (sortBy === 'highest_prob') return b.probability - a.probability;
      if (sortBy === 'lowest_prob') return a.probability - b.probability;
      if (sortBy === 'status') return b.prediction - a.prediction;
      return 0;
    });

  return (
    <div className="history-page">
      {/* Action Notification */}
      {actionMsg && (
        <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', color: '#047857', padding: '12px 16px', borderRadius: 'var(--radius-md)', marginBottom: '16px', fontSize: '0.88rem', fontWeight: '600' }}>
          {actionMsg}
        </div>
      )}

      {/* Main Table Card */}
      <div className="card">
        <div className="card-header" style={{ flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <h3 className="card-title">
              <History size={20} color="#0284c7" />
              Water Quality Prediction Audit Log
            </h3>
            <p className="card-subtitle">
              Persistent SQLite storage of all assessed samples ({history.length} records)
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={fetchHistory}
              title="Refresh history"
            >
              <RefreshCw size={14} className={loading ? 'spin-icon' : ''} />
              <span>Refresh</span>
            </button>

            <button 
              className="btn btn-secondary btn-sm"
              onClick={exportCSV}
              disabled={history.length === 0}
            >
              <Download size={14} />
              <span>Export CSV</span>
            </button>

            <button 
              className="btn btn-danger btn-sm"
              onClick={handleClearAll}
              disabled={history.length === 0}
            >
              <Trash2 size={14} />
              <span>Clear Log</span>
            </button>
          </div>
        </div>

        {/* Search, Filter, and Sort Toolbar */}
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', marginBottom: '20px', alignItems: 'center' }}>
          <div style={{ flex: '1', minWidth: '240px', position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
            <input 
              type="text"
              className="form-input"
              style={{ paddingLeft: '38px' }}
              placeholder="Search by sample name, status, risk, or timestamp..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: '600' }}>Filter:</span>
            <button
              className={`btn btn-sm ${filterStatus === 'all' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('all')}
            >
              All
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'safe' ? 'btn-success' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('safe')}
            >
              Safe Only
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'unsafe' ? 'btn-danger' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('unsafe')}
            >
              Unsafe Only
            </button>
          </div>

          <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
            <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: '600' }}>Sort By:</span>
            <select
              className="form-input"
              style={{ width: 'auto', padding: '6px 12px', fontSize: '0.82rem' }}
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="highest_prob">Highest Probability</option>
              <option value="lowest_prob">Lowest Probability</option>
              <option value="status">Potability Status</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '48px', textAlign: 'center', color: '#64748b' }}>
            <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite', margin: '0 auto 12px' }} />
            <p>Loading prediction audit logs...</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div style={{ padding: '48px', textAlign: 'center', color: '#64748b', background: '#f8fafc', borderRadius: 'var(--radius-md)' }}>
            <History size={36} color="#cbd5e1" style={{ margin: '0 auto 12px' }} />
            <p style={{ fontWeight: '600', color: '#334155' }}>No prediction records found</p>
            <p style={{ fontSize: '0.82rem', marginTop: '4px' }}>
              Run your first water quality assessment on the "Water Prediction" tab to populate this log.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="custom-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Sample Name</th>
                  <th>Timestamp</th>
                  <th>pH</th>
                  <th>Solids (TDS)</th>
                  <th>Turbidity</th>
                  <th>Potability</th>
                  <th>Probability</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map(item => (
                  <tr 
                    key={item.id} 
                    style={{ cursor: 'pointer' }}
                    onClick={() => setSelectedItem(item)}
                  >
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '600' }}>#{item.id}</td>
                    <td style={{ fontWeight: '700', color: '#0f172a' }}>{item.sample_name || 'Water Sample'}</td>
                    <td style={{ fontSize: '0.8rem', color: '#64748b', whiteSpace: 'nowrap' }}>
                      {item.created_at}
                    </td>
                    <td>{item.ph.toFixed(1)}</td>
                    <td>{item.solids.toFixed(0)} <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>ppm</span></td>
                    <td>{item.turbidity.toFixed(1)} <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>NTU</span></td>
                    <td>
                      <span className={`badge ${item.prediction === 1 ? 'badge-safe' : 'badge-danger'}`}>
                        {item.prediction === 1 ? 'Safe' : 'Unsafe'}
                      </span>
                    </td>
                    <td>
                      <span style={{ fontWeight: '700', color: item.prediction === 1 ? '#059669' : '#e11d48' }}>
                        {item.probability.toFixed(1)}%
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <button 
                          className="btn btn-secondary btn-sm"
                          style={{ padding: '4px 8px' }}
                          onClick={(e) => { e.stopPropagation(); setSelectedItem(item); }}
                          title="View Full Parameters"
                        >
                          <Eye size={14} />
                        </button>
                        <button 
                          className="btn btn-danger btn-sm"
                          style={{ padding: '4px 8px' }}
                          onClick={(e) => handleDeleteItem(item.id, e)}
                          title="Delete Record"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Inspection Modal */}
      {selectedItem && (
        <div className="modal-overlay" onClick={() => setSelectedItem(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: '800', color: '#0f172a' }}>
                  Sample Assessment #{selectedItem.id}
                </h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b' }}>
                  {selectedItem.sample_name} • Recorded on {selectedItem.created_at}
                </p>
              </div>
              <button 
                onClick={() => setSelectedItem(null)}
                style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#64748b' }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              <div 
                style={{
                  padding: '16px',
                  borderRadius: 'var(--radius-md)',
                  background: selectedItem.prediction === 1 ? '#ecfdf5' : '#fff1f2',
                  border: `1px solid ${selectedItem.prediction === 1 ? '#a7f3d0' : '#fecdd3'}`,
                  marginBottom: '20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {selectedItem.prediction === 1 ? (
                    <ShieldCheck size={28} color="#059669" />
                  ) : (
                    <ShieldAlert size={28} color="#e11d48" />
                  )}
                  <div>
                    <div style={{ fontWeight: '800', fontSize: '1.05rem', color: selectedItem.prediction === 1 ? '#047857' : '#be123c' }}>
                      {selectedItem.potability_label === 'Safe' ? 'Potable (Safe for Consumption)' : 'Non-Potable (Unsafe)'}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#475569' }}>
                      {selectedItem.risk_level} • Model: {selectedItem.model_used || 'Random Forest'}
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: '800', color: selectedItem.prediction === 1 ? '#059669' : '#e11d48' }}>
                    {selectedItem.probability}%
                  </div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase' }}>Probability</div>
                </div>
              </div>

              <h4 style={{ fontSize: '0.9rem', fontWeight: '700', marginBottom: '12px', color: '#0f172a' }}>
                Measured Water Quality Attributes
              </h4>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>pH Level:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.ph.toFixed(2)} pH</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Hardness:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.hardness.toFixed(1)} mg/L</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Solids (TDS):</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.solids.toFixed(1)} ppm</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Chloramines:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.chloramines.toFixed(2)} ppm</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Sulfate:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.sulfate.toFixed(1)} mg/L</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Conductivity:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.conductivity.toFixed(1)} μS/cm</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Organic Carbon:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.organic_carbon.toFixed(2)} ppm</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Trihalomethanes:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.trihalomethanes.toFixed(1)} μg/L</div>
                </div>
                <div style={{ padding: '10px 14px', background: '#f8fafc', borderRadius: 'var(--radius-sm)', border: '1px solid #e2e8f0', gridColumn: 'span 2' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Turbidity:</span>
                  <div style={{ fontWeight: '700', color: '#0f172a' }}>{selectedItem.turbidity.toFixed(2)} NTU</div>
                </div>
              </div>

              <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button 
                  className="btn btn-danger btn-sm"
                  onClick={(e) => handleDeleteItem(selectedItem.id, e)}
                >
                  <Trash2 size={14} />
                  <span>Delete Record</span>
                </button>
                <button 
                  className="btn btn-secondary btn-sm"
                  onClick={() => setSelectedItem(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
