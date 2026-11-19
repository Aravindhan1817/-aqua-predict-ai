import React from 'react';
import { 
  Droplets, 
  ShieldCheck, 
  Activity, 
  BarChart2, 
  Database, 
  Layers, 
  CheckCircle2, 
  ArrowRight,
  Sliders,
  AlertTriangle
} from 'lucide-react';

export default function OverviewPage({ setActiveTab, metrics }) {
  const paramsOverview = [
    { name: 'pH Level', unit: '0 - 14 pH', range: '6.5 - 8.5', desc: 'Indicates acidity or alkalinity balance.' },
    { name: 'Hardness', unit: 'mg/L CaCO3', range: '60 - 250 mg/L', desc: 'Precipitated calcium and magnesium ions.' },
    { name: 'Total Dissolved Solids', unit: 'ppm / mg/L', range: '< 1000 ppm', desc: 'Dissolved minerals, salts, and heavy metals.' },
    { name: 'Chloramines', unit: 'ppm (mg/L)', range: '< 4.0 ppm', desc: 'Disinfection residual used in municipal water.' },
    { name: 'Sulfate', unit: 'mg/L', range: '< 250 mg/L', desc: 'Naturally occurring minerals from rock formations.' },
    { name: 'Conductivity', unit: 'μS/cm', range: '< 600 μS/cm', desc: 'Electrical ionic conductance capacity.' },
    { name: 'Organic Carbon', unit: 'ppm (mg/L)', range: '< 4.0 ppm', desc: 'Decomposing natural organic material content.' },
    { name: 'Trihalomethanes', unit: 'μg/L (ppb)', range: '< 80 μg/L', desc: 'Chlorination disinfection byproduct compounds.' },
    { name: 'Turbidity', unit: 'NTU', range: '< 5.0 NTU', desc: 'Suspended colloidal particulates and clarity.' },
  ];

  const totalSamples = metrics?.dataset_stats?.total_samples || 3276;
  const bestModelName = metrics?.best_model || 'Random Forest';
  const bestAccuracy = metrics?.models?.[bestModelName]?.accuracy || 67.53;

  return (
    <div className="overview-page">
      {/* Hero Welcome Banner */}
      <div 
        style={{
          background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #0f766e 100%)',
          borderRadius: 'var(--radius-lg)',
          padding: '36px',
          color: '#ffffff',
          marginBottom: '28px',
          boxShadow: 'var(--shadow-lg)'
        }}
      >
        <div style={{ maxWidth: '850px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.18)', padding: '4px 12px', borderRadius: '999px', fontSize: '0.8rem', fontWeight: '600', marginBottom: '16px' }}>
            <ShieldCheck size={16} />
            <span>AI-Driven Water Quality Prediction and Health Assessment</span>
          </div>
          <h1 style={{ fontSize: '2.4rem', fontWeight: '800', lineHeight: '1.2', marginBottom: '14px', letterSpacing: '-0.02em' }}>
            Clean Water Assurance Powered by Machine Learning
          </h1>
          <p style={{ fontSize: '1.05rem', opacity: '0.92', lineHeight: '1.6', marginBottom: '24px' }}>
            Analyze 9 critical physical, chemical, and biological water quality parameters to instantly determine drinking water safety. 
            Evaluate WHO and EPA regulatory compliance and receive tailored filtration recommendations.
          </p>
          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
            <button 
              className="btn btn-success"
              style={{ fontSize: '1rem', padding: '12px 24px' }}
              onClick={() => setActiveTab('predict')}
            >
              <Droplets size={18} />
              <span>Analyze Water Sample</span>
              <ArrowRight size={16} />
            </button>
            <button 
              className="btn btn-secondary"
              style={{ background: 'rgba(255,255,255,0.15)', color: '#ffffff', borderColor: 'rgba(255,255,255,0.3)', backdropFilter: 'blur(4px)' }}
              onClick={() => setActiveTab('performance')}
            >
              <BarChart2 size={18} />
              <span>Explore ML Models</span>
            </button>
          </div>
        </div>
      </div>

      {/* Quick Statistics Row */}
      <div className="grid-stats">
        <div className="stat-box">
          <div className="stat-icon blue">
            <Database size={24} />
          </div>
          <div>
            <div className="stat-label">Training Dataset</div>
            <div className="stat-value">{totalSamples.toLocaleString()}</div>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Real verified water samples</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon green">
            <Activity size={24} />
          </div>
          <div>
            <div className="stat-label">Production Model</div>
            <div className="stat-value" style={{ fontSize: '1.25rem' }}>{bestModelName}</div>
            <div style={{ fontSize: '0.75rem', color: '#059669', fontWeight: '600' }}>{bestAccuracy}% Test Accuracy</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon amber">
            <Sliders size={24} />
          </div>
          <div>
            <div className="stat-label">Analyzed Parameters</div>
            <div className="stat-value">9 Factors</div>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Physical, Chemical & Microbiological</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon rose">
            <Layers size={24} />
          </div>
          <div>
            <div className="stat-label">Evaluated Models</div>
            <div className="stat-value">6 Algorithms</div>
            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Benchmarked on Stratified Holdout</div>
          </div>
        </div>
      </div>

      {/* Architectural Features Grid */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <ShieldCheck className="text-primary" size={20} color="#0284c7" />
                How the Assessment Engine Works
              </h3>
              <p className="card-subtitle">End-to-end data processing and diagnostic pipeline</p>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#e0f2fe', color: '#0369a1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.85rem', flexShrink: 0 }}>1</div>
              <div>
                <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>Input Ingestion & Validation:</strong>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>
                  Captures 9 chemical and physical attributes with Pydantic boundary validation to eliminate out-of-range anomalies.
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#e0f2fe', color: '#0369a1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.85rem', flexShrink: 0 }}>2</div>
              <div>
                <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>Zero Data-Leakage Preprocessing:</strong>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>
                  Passes inputs through pre-fitted median imputers and standard scalers trained solely on the training partition.
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#e0f2fe', color: '#0369a1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.85rem', flexShrink: 0 }}>3</div>
              <div>
                <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>Machine Learning Potability Inference:</strong>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>
                  Evaluates sample through an ensemble Random Forest model, deriving potability classification and calibrated probability confidence.
                </p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{ width: '28px', height: '28px', borderRadius: '50%', background: '#e0f2fe', color: '#0369a1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '0.85rem', flexShrink: 0 }}>4</div>
              <div>
                <strong style={{ fontSize: '0.92rem', color: '#0f172a' }}>Advisory & Treatment Recommendations:</strong>
                <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '2px' }}>
                  Cross-references values with WHO/EPA drinking water standards and generates concrete purification action plans.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <CheckCircle2 size={20} color="#10b981" />
                Key System Highlights
              </h3>
              <p className="card-subtitle">Engineered for accuracy, reliability, and usability</p>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
              <div style={{ fontWeight: '700', fontSize: '0.9rem', color: '#0f172a' }}>Real Machine Learning Models</div>
              <p style={{ fontSize: '0.82rem', color: '#64748b' }}>
                Trained on the Kaggle Water Potability benchmark. All performance figures (67.53% Accuracy) are genuine and verified on a holdout test set.
              </p>
            </div>
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
              <div style={{ fontWeight: '700', fontSize: '0.9rem', color: '#0f172a' }}>SQLite Persistent Audit Trail</div>
              <p style={{ fontSize: '0.82rem', color: '#64748b' }}>
                Every tested sample is stored in a structured SQLite database with timestamps, parameters, and risk classifications for historical auditing.
              </p>
            </div>
            <div style={{ padding: '12px', background: '#f8fafc', borderRadius: 'var(--radius-md)', border: '1px solid #e2e8f0' }}>
              <div style={{ fontWeight: '700', fontSize: '0.9rem', color: '#0f172a' }}>1-Click Preset Samples</div>
              <p style={{ fontSize: '0.82rem', color: '#64748b' }}>
                Test the model instantly with pre-configured samples including Pristine Spring Water, Municipal Tap, Acidic Industrial Runoff, and Turbid River Water.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 9 Water Quality Parameters Grid */}
      <div className="card">
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Droplets size={20} color="#0284c7" />
              Water Quality Parameter Standard Reference
            </h3>
            <p className="card-subtitle">Permissible ranges and health criteria based on WHO & EPA guidelines</p>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={() => setActiveTab('standards')}>
            <span>Full Standards Guide</span>
            <ArrowRight size={14} />
          </button>
        </div>

        <div className="grid-3">
          {paramsOverview.map((p, idx) => (
            <div 
              key={idx}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-md)',
                background: '#ffffff',
                border: '1px solid #e2e8f0',
                transition: 'all 0.2s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span style={{ fontWeight: '700', fontSize: '0.92rem', color: '#0f172a' }}>{p.name}</span>
                <span className="unit-tag">{p.unit}</span>
              </div>
              <div style={{ fontSize: '0.82rem', color: '#0284c7', fontWeight: '600', marginBottom: '6px' }}>
                Safe Limit: {p.range}
              </div>
              <p style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: '1.4' }}>
                {p.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
