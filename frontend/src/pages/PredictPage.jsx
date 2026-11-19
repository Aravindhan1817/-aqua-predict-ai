import React, { useState, useEffect, useRef } from 'react';
import { 
  Droplets, 
  Send, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles, 
  Sliders, 
  FileCheck, 
  Info,
  ShieldCheck,
  ShieldAlert,
  ArrowRight,
  TrendingUp,
  Filter
} from 'lucide-react';
import { api } from '../services/api';

const DEFAULT_SAMPLE = {
  sample_name: 'Sample #1 - General Tap Water',
  ph: 7.2,
  hardness: 195.0,
  solids: 18500.0,
  chloramines: 6.8,
  sulfate: 335.0,
  conductivity: 420.0,
  organic_carbon: 12.5,
  trihalomethanes: 65.0,
  turbidity: 3.8
};

const PARAM_CONFIGS = [
  { key: 'ph', label: 'pH Level', unit: 'pH units', min: 0.0, max: 14.0, step: 0.1, standard: '6.5 - 8.5' },
  { key: 'hardness', label: 'Hardness', unit: 'mg/L CaCO3', min: 0.0, max: 450.0, step: 1.0, standard: '60 - 250 mg/L' },
  { key: 'solids', label: 'Total Dissolved Solids (TDS)', unit: 'ppm / mg/L', min: 0.0, max: 55000.0, step: 100.0, standard: '< 1000 ppm' },
  { key: 'chloramines', label: 'Chloramines', unit: 'ppm (mg/L)', min: 0.0, max: 15.0, step: 0.1, standard: '< 4.0 ppm' },
  { key: 'sulfate', label: 'Sulfate', unit: 'mg/L', min: 0.0, max: 550.0, step: 1.0, standard: '< 250 mg/L' },
  { key: 'conductivity', label: 'Conductivity', unit: 'μS/cm', min: 0.0, max: 1000.0, step: 5.0, standard: '< 600 μS/cm' },
  { key: 'organic_carbon', label: 'Total Organic Carbon', unit: 'ppm (mg/L)', min: 0.0, max: 30.0, step: 0.1, standard: '< 4.0 ppm' },
  { key: 'trihalomethanes', label: 'Trihalomethanes (THMs)', unit: 'μg/L (ppb)', min: 0.0, max: 130.0, step: 0.5, standard: '< 80 μg/L' },
  { key: 'turbidity', label: 'Turbidity', unit: 'NTU', min: 0.0, max: 10.0, step: 0.1, standard: '< 5.0 NTU' },
];

export default function PredictPage({ onPredictionSuccess }) {
  const [formData, setFormData] = useState(DEFAULT_SAMPLE);
  const [presets, setPresets] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const resultRef = useRef(null);

  useEffect(() => {
    // Load presets
    api.getPresets()
      .then(data => setPresets(data))
      .catch(() => {
        // Fallback preset samples if API is offline
        setPresets([
          { id: 'spring', name: 'Pristine Spring Water', parameters: { sample_name: 'Spring Water', ph: 7.2, hardness: 145.0, solids: 16200.0, chloramines: 5.5, sulfate: 310.0, conductivity: 395.0, organic_carbon: 11.2, trihalomethanes: 55.0, turbidity: 3.1 } },
          { id: 'runoff', name: 'Industrial Runoff Sample', parameters: { sample_name: 'Industrial Waste', ph: 3.9, hardness: 240.0, solids: 34000.0, chloramines: 9.2, sulfate: 460.0, conductivity: 680.0, organic_carbon: 21.5, trihalomethanes: 98.0, turbidity: 5.8 } }
        ]);
      });
  }, []);

  const handleInputChange = (key, value) => {
    const num = parseFloat(value);
    setFormData(prev => ({
      ...prev,
      [key]: isNaN(num) ? value : num
    }));
  };

  const loadPreset = (preset) => {
    setFormData({
      ...preset.parameters,
      sample_name: preset.name
    });
    setResult(null);
    setError(null);
  };

  const handleReset = () => {
    setFormData(DEFAULT_SAMPLE);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await api.predict(formData);
      setResult(response);
      if (onPredictionSuccess) onPredictionSuccess(response);
      // Scroll smoothly to results
      setTimeout(() => {
        resultRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err) {
      setError(err.message || 'Failed to complete prediction. Please verify the backend API.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="predict-page">
      {/* 1-Click Preset Samples */}
      <div className="presets-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#0369a1', fontWeight: '700', fontSize: '0.85rem' }}>
          <Sparkles size={16} />
          <span>Quick Preset Samples:</span>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {presets.map(p => (
            <button
              key={p.id}
              type="button"
              className="preset-chip"
              onClick={() => loadPreset(p)}
              title={p.description || p.name}
            >
              {p.name}
            </button>
          ))}
          <button
            type="button"
            className="preset-chip"
            style={{ borderColor: '#cbd5e1', color: '#64748b' }}
            onClick={handleReset}
          >
            Reset Default
          </button>
        </div>
      </div>

      {/* Input Form Card */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Sliders size={20} color="#0284c7" />
              Water Quality Sample Parameters
            </h3>
            <p className="card-subtitle">
              Adjust numerical sliders or enter exact laboratory measurements for all 9 factors
            </p>
          </div>
          <div className="badge badge-info">EPA / WHO Guideline Mode</div>
        </div>

        {error && (
          <div style={{ background: '#fff1f2', border: '1px solid #fecdd3', color: '#be123c', padding: '12px 16px', borderRadius: 'var(--radius-md)', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle size={18} />
            <span style={{ fontSize: '0.88rem', fontWeight: '600' }}>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group" style={{ marginBottom: '20px' }}>
            <label className="form-label">
              <span>Sample Name / Identifier</span>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Optional label for logging</span>
            </label>
            <input 
              type="text"
              className="form-input"
              value={formData.sample_name || ''}
              onChange={(e) => setFormData({ ...formData, sample_name: e.target.value })}
              placeholder="e.g. Municipal Tap #4, Well Water Sample, Filtered Output"
            />
          </div>

          <div className="grid-3">
            {PARAM_CONFIGS.map(cfg => {
              const val = formData[cfg.key] ?? 0;
              return (
                <div key={cfg.key} className="form-group" style={{ padding: '14px', background: '#f8fafc', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
                  <div className="form-label">
                    <span style={{ color: '#0f172a', fontWeight: '700' }}>{cfg.label}</span>
                    <span className="unit-tag">{cfg.unit}</span>
                  </div>

                  <div className="slider-container" style={{ margin: '8px 0' }}>
                    <input 
                      type="range"
                      className="range-slider"
                      min={cfg.min}
                      max={cfg.max}
                      step={cfg.step}
                      value={val}
                      onChange={(e) => handleInputChange(cfg.key, e.target.value)}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.72rem', color: '#64748b' }}>
                      Standard: <strong>{cfg.standard}</strong>
                    </span>
                    <input 
                      type="number"
                      className="form-input"
                      style={{ width: '105px', padding: '6px 10px', fontSize: '0.88rem', textAlign: 'right', fontWeight: '700' }}
                      min={cfg.min}
                      max={cfg.max}
                      step={cfg.step}
                      value={val}
                      onChange={(e) => handleInputChange(cfg.key, e.target.value)}
                      required
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={loading}
            >
              <RefreshCw size={16} />
              <span>Reset Values</span>
            </button>

            <button 
              type="submit" 
              className="btn btn-primary"
              style={{ minWidth: '180px' }}
              disabled={loading}
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="spin-icon" style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Evaluating...</span>
                </>
              ) : (
                <>
                  <Send size={16} />
                  <span>Predict Water Potability</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Prediction Result Section */}
      {result && (
        <div ref={resultRef} style={{ animation: 'fadeIn 0.4s ease-in-out' }}>
          {/* Main Potability Banner */}
          <div className={`result-banner ${result.prediction === 1 ? 'safe' : 'unsafe'}`}>
            <div className="banner-content">
              <div className="banner-icon-circle">
                {result.prediction === 1 ? (
                  <ShieldCheck size={36} color="#ffffff" />
                ) : (
                  <ShieldAlert size={36} color="#ffffff" />
                )}
              </div>
              <div>
                <div style={{ display: 'inline-block', padding: '3px 10px', background: 'rgba(255,255,255,0.2)', borderRadius: '999px', fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', marginBottom: '6px' }}>
                  AI Diagnostic Verdict
                </div>
                <h2 className="banner-status-title">
                  {result.prediction === 1 ? 'Water Sample is Potable (Safe to Drink)' : 'Water Sample is Non-Potable (Unsafe)'}
                </h2>
                <p className="banner-status-desc">
                  {result.prediction === 1 
                    ? `This sample satisfies microbiological, physical, and chemical thresholds under ${result.model_used}. Regular monitoring is recommended.`
                    : `Dangerous anomalies detected. Direct consumption without purification is hazardous to health. Review remediation protocols below.`
                  }
                </p>
                <div style={{ marginTop: '10px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <span className="badge" style={{ background: 'rgba(255,255,255,0.25)', color: '#ffffff' }}>
                    {result.risk_level}
                  </span>
                  <span style={{ fontSize: '0.8rem', opacity: '0.9' }}>
                    Model: <strong>{result.model_used}</strong>
                  </span>
                </div>
              </div>
            </div>

            <div className="banner-gauge">
              <div className="gauge-percentage">{result.probability}%</div>
              <div className="gauge-label">Potability Probability</div>
              <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.3)', borderRadius: '999px', margin: '8px 0', overflow: 'hidden' }}>
                <div style={{ width: `${result.probability}%`, height: '100%', background: '#ffffff', borderRadius: '999px' }}></div>
              </div>
              <div style={{ fontSize: '0.72rem', opacity: '0.9' }}>
                Confidence: {result.confidence}%
              </div>
            </div>
          </div>

          {/* Result Details Grid */}
          <div className="grid-2" style={{ marginBottom: '28px' }}>
            {/* Feature Contributions Chart */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">
                    <TrendingUp size={20} color="#0284c7" />
                    Important Contributing Features
                  </h3>
                  <p className="card-subtitle">Parameters that had the greatest influence on this specific prediction</p>
                </div>
              </div>

              <div>
                {Object.entries(result.feature_contributions || {})
                  .sort((a, b) => b[1] - a[1])
                  .map(([feat, val]) => (
                    <div key={feat} className="feature-bar-row">
                      <span className="feature-bar-label">{feat}</span>
                      <div className="feature-bar-track">
                        <div 
                          className="feature-bar-fill"
                          style={{ width: `${Math.min(100, Math.max(5, val * 3.5))}%` }}
                        ></div>
                      </div>
                      <span className="feature-bar-value">{val}%</span>
                    </div>
                  ))}
              </div>
            </div>

            {/* Smart Treatment Recommendations */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">
                    <Filter size={20} color="#10b981" />
                    Recommended Remediation Protocols
                  </h3>
                  <p className="card-subtitle">Engineered purification steps tailored to detected anomalies</p>
                </div>
              </div>

              <div>
                {result.recommendations && result.recommendations.length > 0 ? (
                  result.recommendations.map((rec, idx) => (
                    <div 
                      key={idx} 
                      className={`recommendation-item recommendation-badge-${rec.priority}`}
                    >
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                          <span style={{ fontWeight: '700', fontSize: '0.9rem', color: '#0f172a' }}>{rec.title}</span>
                          <span className={`badge badge-${rec.priority === 'high' ? 'danger' : rec.priority === 'medium' ? 'warning' : 'safe'}`}>
                            {rec.priority} Priority
                          </span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#0284c7', fontWeight: '600', marginBottom: '4px' }}>
                          Category: {rec.category}
                        </div>
                        <p style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.4' }}>
                          {rec.description}
                        </p>
                      </div>
                    </div>
                  ))
                ) : (
                  <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
                    No critical treatment interventions required. Sample meets target health criteria.
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Full Parameter Compliance Breakdown Table */}
          <div className="card">
            <div className="card-header">
              <div>
                <h3 className="card-title">
                  <FileCheck size={20} color="#0284c7" />
                  Parameter-by-Parameter Diagnostic Table
                </h3>
                <p className="card-subtitle">Comparison against WHO and EPA Drinking Water Standards</p>
              </div>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Parameter</th>
                    <th>Measured Value</th>
                    <th>Permissible Standard</th>
                    <th>Status</th>
                    <th>Health Impact / Diagnostic Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {result.parameter_evaluations?.map((p, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: '700' }}>{p.display_name}</td>
                      <td>
                        <strong style={{ fontFamily: 'var(--font-mono)' }}>{p.value}</strong>{' '}
                        <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{p.unit}</span>
                      </td>
                      <td style={{ color: '#0369a1', fontWeight: '500' }}>{p.safe_range}</td>
                      <td>
                        <span className={`badge badge-${p.status === 'safe' ? 'safe' : p.status === 'warning' ? 'warning' : 'danger'}`}>
                          {p.status}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.82rem', color: '#475569', maxWidth: '380px' }}>
                        {p.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
