import React from 'react';
import { 
  BookOpen, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Info,
  Droplets,
  ExternalLink,
  Filter
} from 'lucide-react';

export default function StandardsPage() {
  const standardsData = [
    {
      param: 'pH Level',
      unit: 'pH units (0 - 14)',
      standard: '6.5 - 8.5 pH',
      ideal: '7.0 - 7.5 pH',
      agency: 'WHO / US EPA Secondary Drinking Water Standard',
      healthImpact: 'pH below 6.5 accelerates corrosion of metal water pipes, causing toxic lead and copper leaching into tap water. pH above 8.5 leaves encrusted mineral scaling, tastes bitter, and reduces chlorine disinfection efficacy.',
      remediation: 'Pass acidic water through neutralizing calcite or magnesium oxide beds. Treat high alkaline water with food-grade carbon dioxide or organic acid injection.'
    },
    {
      param: 'Hardness (CaCO3 Equivalent)',
      unit: 'mg/L (ppm)',
      standard: '60 - 250 mg/L',
      ideal: '100 - 150 mg/L',
      agency: 'WHO Guidelines for Drinking-water Quality',
      healthImpact: 'Water with hardness over 200 mg/L forms thick mineral scaling in pipes, domestic boilers, and water heaters. While not acutely toxic to healthy individuals, very hard water degrades lathering, dries skin, and impairs plumbing longevity.',
      remediation: 'Employ sodium or potassium ion-exchange resin water softeners, template-assisted crystallization, or reverse osmosis membranes.'
    },
    {
      param: 'Total Dissolved Solids (TDS / Solids)',
      unit: 'ppm (mg/L)',
      standard: '< 1000 ppm (EPA Secondary < 500 ppm)',
      ideal: '150 - 300 ppm',
      agency: 'WHO & US EPA National Secondary Drinking Water Regulations',
      healthImpact: 'High TDS indicates elevated dissolved mineral salts, carbonates, chlorides, and potential heavy metals. TDS above 1,000 ppm imparts unpalatable brackish taste and may induce gastrointestinal distress.',
      remediation: 'Multi-stage Reverse Osmosis (RO) filtration systems with thin-film composite (TFC) membranes or electrodialysis reversal.'
    },
    {
      param: 'Chloramines',
      unit: 'ppm (mg/L)',
      standard: '< 4.0 ppm',
      ideal: '1.0 - 2.5 ppm',
      agency: 'US EPA Maximum Residual Disinfectant Level (MRDL)',
      healthImpact: 'Chloramines are formed by reacting chlorine with ammonia to produce prolonged residual disinfection. Levels over 4 ppm cause respiratory irritation, mucosal irritation, and pronounced chlorine/chemical odor.',
      remediation: 'Catalytic granular activated carbon (GAC) filtration or ascorbic acid (Vitamin C) neutralizers designed specifically for chloramine reduction.'
    },
    {
      param: 'Sulfate (SO4)',
      unit: 'mg/L',
      standard: '< 250 mg/L',
      ideal: '20 - 100 mg/L',
      agency: 'US EPA Secondary Standard & WHO Guidelines',
      healthImpact: 'Sulfates occur naturally in mineral deposits. Concentrations exceeding 250 mg/L produce a bitter medicinal taste and induce laxative effects, diarrhea, and dehydration, especially in infants and non-acclimated individuals.',
      remediation: 'Anion-exchange softening resin, distillation, or high-pressure reverse osmosis.'
    },
    {
      param: 'Electrical Conductivity (EC)',
      unit: 'μS/cm',
      standard: '< 600 μS/cm (Max 800 μS/cm)',
      ideal: '200 - 400 μS/cm',
      agency: 'WHO Permissible Drinking Standards',
      healthImpact: 'Conductivity measures water’s ability to conduct electrical current, directly reflecting dissolved ion concentration. High EC indicates excessive salinity, agricultural nutrient runoff, or industrial chemical effluent.',
      remediation: 'Demineralization via deionization (DI) resin beds or Reverse Osmosis.'
    },
    {
      param: 'Total Organic Carbon (TOC)',
      unit: 'ppm (mg/L)',
      standard: '< 4.0 ppm (ideally < 2.0 ppm)',
      ideal: '< 1.5 ppm',
      agency: 'US EPA Disinfection Byproduct Rule (DBPR)',
      healthImpact: 'Organic carbon measures decaying plant and animal matter. While not directly toxic, organic compounds react with chlorine disinfectants to create carcinogenic disinfection byproducts (THMs and HAAs).',
      remediation: 'Activated carbon block filtration, ozone oxidation, coagulant flocculation, and UV-C destruction.'
    },
    {
      param: 'Trihalomethanes (THMs)',
      unit: 'μg/L (parts per billion - ppb)',
      standard: '< 80 μg/L (ppb)',
      ideal: '< 40 μg/L',
      agency: 'US EPA National Primary Drinking Water Regulations (MCL)',
      healthImpact: 'Formed when chlorine reacts with natural organic matter. Long-term exposure to trihalomethanes (such as chloroform) is clinically linked to increased risks of bladder cancer, liver dysfunction, and central nervous system complications.',
      remediation: 'Point-of-use Granular Activated Carbon (GAC) block filters or aerated packed-tower stripping.'
    },
    {
      param: 'Turbidity',
      unit: 'NTU (Nephelometric Turbidity Units)',
      standard: '< 5.0 NTU (Ideally < 1.0 NTU)',
      ideal: '< 0.5 NTU',
      agency: 'WHO Guidelines for Drinking-water Quality',
      healthImpact: 'Turbidity measures optical cloudiness caused by suspended clay, silt, and microorganisms. Colloidal particles shield pathogenic viruses and bacteria from chemical and UV disinfection, indicating contaminated surface runoff.',
      remediation: 'Multi-media dual sand/anthracite filters followed by 1-micron sediment cartridges and coagulation.'
    }
  ];

  return (
    <div className="standards-page">
      {/* Overview Banner */}
      <div 
        style={{
          background: 'linear-gradient(135deg, #0369a1 0%, #075985 100%)',
          borderRadius: 'var(--radius-lg)',
          padding: '32px',
          color: '#ffffff',
          marginBottom: '28px',
          boxShadow: 'var(--shadow-md)'
        }}
      >
        <div style={{ maxWidth: '800px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.2)', padding: '4px 12px', borderRadius: '999px', fontSize: '0.8rem', fontWeight: '700', marginBottom: '14px' }}>
            <BookOpen size={16} />
            <span>Regulatory Standards & Health Guidelines</span>
          </div>
          <h2 style={{ fontSize: '2rem', fontWeight: '800', lineHeight: '1.2', marginBottom: '12px' }}>
            Drinking Water Quality Standards Encyclopedia
          </h2>
          <p style={{ opacity: '0.9', fontSize: '0.98rem', lineHeight: '1.6' }}>
            Permissible thresholds, toxicological impacts, and engineering remediation standards established by the World Health Organization (WHO), US Environmental Protection Agency (EPA), and international health authorities.
          </p>
        </div>
      </div>

      {/* Encyclopedia Cards List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {standardsData.map((item, idx) => (
          <div key={idx} className="card">
            <div className="card-header" style={{ marginBottom: '16px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: '#0f172a' }}>
                    {item.param}
                  </h3>
                  <span className="unit-tag">{item.unit}</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: '#0284c7', fontWeight: '600', marginTop: '4px' }}>
                  Regulatory Authority: {item.agency}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase', fontWeight: '600' }}>Safe Limit</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: '800', color: '#059669' }}>{item.standard}</div>
                </div>
                <div style={{ textAlign: 'right', borderLeft: '1px solid #e2e8f0', paddingLeft: '12px' }}>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase', fontWeight: '600' }}>Ideal Level</div>
                  <div style={{ fontSize: '1.1rem', fontWeight: '800', color: '#0284c7' }}>{item.ideal}</div>
                </div>
              </div>
            </div>

            <div className="grid-2">
              <div style={{ padding: '14px', background: '#fff1f2', borderRadius: 'var(--radius-md)', border: '1px solid #ffe4e6' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#be123c', fontWeight: '700', fontSize: '0.85rem', marginBottom: '6px' }}>
                  <AlertTriangle size={16} />
                  <span>Clinical Health Hazards & Toxicity Risks:</span>
                </div>
                <p style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.5' }}>
                  {item.healthImpact}
                </p>
              </div>

              <div style={{ padding: '14px', background: '#f0fdf4', borderRadius: 'var(--radius-md)', border: '1px solid #dcfce7' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#047857', fontWeight: '700', fontSize: '0.85rem', marginBottom: '6px' }}>
                  <Filter size={16} />
                  <span>Remediation & Purification Protocols:</span>
                </div>
                <p style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.5' }}>
                  {item.remediation}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
