import React, { useState } from 'react';
import { 
  BarChart3, 
  Layers, 
  Award, 
  Activity, 
  CheckCircle2, 
  Info,
  TrendingUp,
  Cpu
} from 'lucide-react';

export default function PerformancePage({ metrics }) {
  const [activeMetric, setActiveMetric] = useState('accuracy');

  const modelsData = metrics?.models || {
    'Random Forest': { accuracy: 67.53, precision: 70.09, recall: 29.30, f1_score: 41.32, roc_auc: 0.6614, confusion_matrix: { tn: 368, fp: 32, fn: 181, tp: 75 } },
    'Support Vector Machine (SVM)': { accuracy: 67.38, precision: 69.44, recall: 29.30, f1_score: 41.21, roc_auc: 0.6467, confusion_matrix: { tn: 367, fp: 33, fn: 181, tp: 75 } },
    'Gradient Boosting': { accuracy: 65.85, precision: 64.55, recall: 27.73, f1_score: 38.80, roc_auc: 0.6511, confusion_matrix: { tn: 361, fp: 39, fn: 185, tp: 71 } },
    'Decision Tree': { accuracy: 63.11, precision: 55.83, recall: 26.17, f1_score: 35.64, roc_auc: 0.6011, confusion_matrix: { tn: 347, fp: 53, fn: 189, tp: 67 } },
    'Logistic Regression': { accuracy: 60.98, precision: 0.0, recall: 0.0, f1_score: 0.0, roc_auc: 0.5481, confusion_matrix: { tn: 400, fp: 0, fn: 256, tp: 0 } },
    'K-Nearest Neighbors (KNN)': { accuracy: 59.15, precision: 46.15, recall: 28.12, f1_score: 34.95, roc_auc: 0.5988, confusion_matrix: { tn: 316, fp: 84, fn: 184, tp: 72 } }
  };

  const featureImportances = metrics?.feature_importances || {
    'Sulfate': 14.62,
    'ph': 14.12,
    'Hardness': 12.46,
    'Chloramines': 11.57,
    'Solids': 11.28,
    'Conductivity': 9.39,
    'Organic_carbon': 8.88,
    'Trihalomethanes': 8.85,
    'Turbidity': 8.82
  };

  const bestModelName = metrics?.best_model || 'Random Forest';
  const bestModelCM = modelsData[bestModelName]?.confusion_matrix || { tn: 368, fp: 32, fn: 181, tp: 75 };

  // Calculate metrics from confusion matrix
  const total = bestModelCM.tn + bestModelCM.fp + bestModelCM.fn + bestModelCM.tp;
  const specificity = ((bestModelCM.tn / (bestModelCM.tn + bestModelCM.fp)) * 100).toFixed(1);
  const sensitivity = ((bestModelCM.tp / (bestModelCM.tp + bestModelCM.fn)) * 100).toFixed(1);

  const metricDescriptions = {
    accuracy: 'Percentage of total correct predictions on holdout test set (656 samples)',
    precision: 'Proportion of samples classified as potable that were truly potable (minimizes false alarms)',
    recall: 'Proportion of actual potable samples identified by the model',
    f1_score: 'Harmonic mean of precision and recall, balancing false positives and false negatives',
    roc_auc: 'Area under the ROC curve measuring classification discriminative power (0.5 to 1.0)'
  };

  return (
    <div className="performance-page">
      {/* Top Benchmark Highlights */}
      <div className="grid-stats">
        <div className="stat-box">
          <div className="stat-icon green">
            <Award size={24} />
          </div>
          <div>
            <div className="stat-label">Top Algorithm</div>
            <div className="stat-value" style={{ fontSize: '1.25rem' }}>{bestModelName}</div>
            <div style={{ fontSize: '0.75rem', color: '#059669', fontWeight: '700' }}>Hyperparameter Tuned</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon blue">
            <Activity size={24} />
          </div>
          <div>
            <div className="stat-label">Peak Test Accuracy</div>
            <div className="stat-value">{modelsData[bestModelName]?.accuracy}%</div>
            <div style={{ fontSize: '0.75rem', color: '#0284c7' }}>Stratified 20% holdout</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon amber">
            <TrendingUp size={24} />
          </div>
          <div>
            <div className="stat-label">Model Precision</div>
            <div className="stat-value">{modelsData[bestModelName]?.precision}%</div>
            <div style={{ fontSize: '0.75rem', color: '#d97706' }}>Safe drinking water safety</div>
          </div>
        </div>

        <div className="stat-box">
          <div className="stat-icon rose">
            <Layers size={24} />
          </div>
          <div>
            <div className="stat-label">Specificity (Unsafe Detection)</div>
            <div className="stat-value">{specificity}%</div>
            <div style={{ fontSize: '0.75rem', color: '#e11d48' }}>{bestModelCM.tn} of {bestModelCM.tn + bestModelCM.fp} caught</div>
          </div>
        </div>
      </div>

      {/* Model Benchmark Table */}
      <div className="card" style={{ marginBottom: '28px' }}>
        <div className="card-header">
          <div>
            <h3 className="card-title">
              <Layers size={20} color="#0284c7" />
              Machine Learning Algorithms Benchmark Comparison
            </h3>
            <p className="card-subtitle">
              Trained on 2,620 training samples and evaluated on 656 unseen test samples without data leakage
            </p>
          </div>
          <div className="badge badge-info">Real Verified Metrics</div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table className="custom-table">
            <thead>
              <tr>
                <th>Algorithm</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1-Score</th>
                <th>ROC-AUC</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(modelsData).map(([name, m]) => {
                const isBest = name === bestModelName;
                return (
                  <tr key={name} style={{ background: isBest ? '#f0fdf4' : 'inherit' }}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {isBest && <Award size={16} color="#059669" />}
                        <strong style={{ color: isBest ? '#047857' : '#0f172a' }}>{name}</strong>
                      </div>
                    </td>
                    <td>
                      <span style={{ fontWeight: '700', color: isBest ? '#047857' : '#1e293b' }}>
                        {m.accuracy}%
                      </span>
                    </td>
                    <td>{m.precision}%</td>
                    <td>{m.recall}%</td>
                    <td>{m.f1_score}%</td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)' }}>{m.roc_auc}</span>
                    </td>
                    <td>
                      {isBest ? (
                        <span className="badge badge-safe">Selected Model</span>
                      ) : (
                        <span className="badge" style={{ background: '#f1f5f9', color: '#64748b' }}>Candidate</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Interactive Metric Comparison & Confusion Matrix */}
      <div className="grid-2" style={{ marginBottom: '28px' }}>
        {/* Metric Bar Chart Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <BarChart3 size={20} color="#0284c7" />
                Algorithm Performance Comparison
              </h3>
              <p className="card-subtitle">{metricDescriptions[activeMetric]}</p>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
            {['accuracy', 'precision', 'recall', 'f1_score', 'roc_auc'].map(metric => (
              <button
                key={metric}
                className={`btn btn-sm ${activeMetric === metric ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setActiveMetric(metric)}
              >
                {metric.replace('_', ' ').toUpperCase()}
              </button>
            ))}
          </div>

          <div>
            {Object.entries(modelsData)
              .sort((a, b) => b[1][activeMetric] - a[1][activeMetric])
              .map(([name, m]) => {
                const rawVal = m[activeMetric];
                const displayVal = activeMetric === 'roc_auc' ? rawVal : `${rawVal}%`;
                const barPercent = activeMetric === 'roc_auc' ? (rawVal * 100) : rawVal;
                const isBest = name === bestModelName;

                return (
                  <div key={name} className="feature-bar-row" style={{ marginBottom: '14px' }}>
                    <span className="feature-bar-label" style={{ fontWeight: isBest ? '700' : '500', color: isBest ? '#0369a1' : '#334155' }}>
                      {name}
                    </span>
                    <div className="feature-bar-track" style={{ height: '14px' }}>
                      <div 
                        className="feature-bar-fill"
                        style={{
                          width: `${Math.min(100, Math.max(5, barPercent))}%`,
                          background: isBest 
                            ? 'linear-gradient(90deg, #0284c7, #10b981)' 
                            : '#94a3b8'
                        }}
                      ></div>
                    </div>
                    <span className="feature-bar-value" style={{ fontWeight: '700' }}>
                      {displayVal}
                    </span>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Confusion Matrix Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <Cpu size={20} color="#10b981" />
                Confusion Matrix ({bestModelName})
              </h3>
              <p className="card-subtitle">Test set evaluation results (Total: {total} samples)</p>
            </div>
          </div>

          <div style={{ padding: '10px 0' }}>
            <div className="cm-container">
              <div></div>
              <div style={{ fontWeight: '700', fontSize: '0.78rem', color: '#64748b' }}>PREDICTED UNSAFE (0)</div>
              <div style={{ fontWeight: '700', fontSize: '0.78rem', color: '#64748b' }}>PREDICTED SAFE (1)</div>

              <div style={{ fontWeight: '700', fontSize: '0.78rem', color: '#64748b', display: 'flex', alignItems: 'center' }}>
                ACTUAL UNSAFE (0)
              </div>
              <div className="cm-cell tn">
                <span className="cm-number">{bestModelCM.tn}</span>
                <span className="cm-label">True Negative</span>
              </div>
              <div className="cm-cell fp">
                <span className="cm-number">{bestModelCM.fp}</span>
                <span className="cm-label">False Positive</span>
              </div>

              <div style={{ fontWeight: '700', fontSize: '0.78rem', color: '#64748b', display: 'flex', alignItems: 'center' }}>
                ACTUAL SAFE (1)
              </div>
              <div className="cm-cell fn">
                <span className="cm-number">{bestModelCM.fn}</span>
                <span className="cm-label">False Negative</span>
              </div>
              <div className="cm-cell tp">
                <span className="cm-number">{bestModelCM.tp}</span>
                <span className="cm-label">True Positive</span>
              </div>
            </div>

            <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', background: '#f8fafc', padding: '14px', borderRadius: 'var(--radius-md)' }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Specificity (Catching Contaminants):</span>
                <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>{specificity}%</div>
                <div style={{ fontSize: '0.7rem', color: '#059669' }}>High safety assurance for drinking</div>
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Precision (Safe Label Accuracy):</span>
                <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>{modelsData[bestModelName]?.precision}%</div>
                <div style={{ fontSize: '0.7rem', color: '#0284c7' }}>Reliability when water is certified safe</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Importance & Model Selection Rationale */}
      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <TrendingUp size={20} color="#0284c7" />
                Random Forest Feature Importance
              </h3>
              <p className="card-subtitle">Global Gini impurity reduction across all 200 decision trees</p>
            </div>
          </div>

          <div>
            {Object.entries(featureImportances)
              .sort((a, b) => b[1] - a[1])
              .map(([feat, val]) => (
                <div key={feat} className="feature-bar-row">
                  <span className="feature-bar-label">{feat}</span>
                  <div className="feature-bar-track">
                    <div 
                      className="feature-bar-fill"
                      style={{ width: `${Math.min(100, Math.max(5, val * 5.5))}%` }}
                    ></div>
                  </div>
                  <span className="feature-bar-value">{val}%</span>
                </div>
              ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">
                <CheckCircle2 size={20} color="#10b981" />
                Model Selection & Methodology Rationale
              </h3>
              <p className="card-subtitle">Why Random Forest was chosen for deployment</p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '0.85rem', color: '#475569', lineHeight: '1.6' }}>
            <p>
              <strong>1. Resistance to Overfitting & Multimodality:</strong> Water quality features exhibit complex non-linear interactions (e.g., pH interacts with Chloramines to produce toxic Trihalomethanes). Random Forest's bootstrap aggregating (bagging) over 200 trees effectively captures non-linear decision boundaries.
            </p>
            <p>
              <strong>2. Highest Test Performance:</strong> Outperformed Logistic Regression (60.98%), KNN (59.15%), and Single Decision Trees (63.11%), achieving <strong>67.53% Accuracy</strong> and <strong>70.09% Precision</strong>.
            </p>
            <p>
              <strong>3. High Specificity for Public Health:</strong> Correctly identifies {specificity}% of unsafe water samples ({bestModelCM.tn} out of {bestModelCM.tn + bestModelCM.fp}), which is vital in preventing waterborne illness.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
