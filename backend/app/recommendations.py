"""
Water Quality Standards and Smart Treatment Recommendation Engine.
Based on WHO (World Health Organization) and EPA (US Environmental Protection Agency) standards.
"""

from typing import List, Dict, Tuple
from backend.app.schemas import ParameterEvaluation, Recommendation

# Reference standard ranges and guideline thresholds
STANDARDS = {
    "ph": {
        "display_name": "pH Level",
        "unit": "pH units",
        "safe_min": 6.5,
        "safe_max": 8.5,
        "critical_min": 5.5,
        "critical_max": 9.5,
        "standard_text": "6.5 - 8.5 (WHO / EPA standard)",
        "ideal": "7.0 - 7.5",
        "hazard_low": "Acidic water can corrode metal pipes, leaching lead and copper into drinking water.",
        "hazard_high": "Alkaline water leaves mineral deposits, tastes bitter, and reduces chlorination efficacy."
    },
    "hardness": {
        "display_name": "Hardness (CaCO3)",
        "unit": "mg/L",
        "safe_min": 60.0,
        "safe_max": 250.0,
        "critical_min": 30.0,
        "critical_max": 400.0,
        "standard_text": "60 - 250 mg/L",
        "ideal": "100 - 150 mg/L",
        "hazard_low": "Excessively soft water may dissolve plumbing materials and lacks essential minerals.",
        "hazard_high": "Excess hardness forms severe scaling in pipes, boilers, and appliances."
    },
    "solids": {
        "display_name": "Total Dissolved Solids (TDS)",
        "unit": "ppm (mg/L)",
        "safe_min": 50.0,
        "safe_max": 1000.0,
        "critical_min": 10.0,
        "critical_max": 50000.0, # Note: Kaggle dataset Solids range up to 60k
        "standard_text": "< 1000 ppm (Ideal < 500 ppm)",
        "ideal": "150 - 300 ppm",
        "hazard_low": "Flat taste due to absence of essential dissolved ions.",
        "hazard_high": "High dissolved mineral and salt concentrations causing salty taste and gastrointestinal irritation."
    },
    "chloramines": {
        "display_name": "Chloramines",
        "unit": "ppm (mg/L)",
        "safe_min": 0.5,
        "safe_max": 4.0,
        "critical_min": 0.0,
        "critical_max": 8.0,
        "standard_text": "< 4.0 ppm (WHO guideline)",
        "ideal": "1.0 - 2.5 ppm",
        "hazard_low": "Insufficient residual disinfectant allowing bacterial and biological regrowth.",
        "hazard_high": "Excess chloramines cause eye/nasal irritation, stomach discomfort, and distinct chemical odor."
    },
    "sulfate": {
        "display_name": "Sulfate",
        "unit": "mg/L",
        "safe_min": 0.0,
        "safe_max": 250.0,
        "critical_min": 0.0,
        "critical_max": 400.0,
        "standard_text": "< 250 mg/L (EPA secondary)",
        "ideal": "20 - 100 mg/L",
        "hazard_low": "No known health hazard at low concentrations.",
        "hazard_high": "High sulfate concentrations produce a bitter medicinal taste and induce laxative/dehydration effects."
    },
    "conductivity": {
        "display_name": "Electrical Conductivity",
        "unit": "μS/cm",
        "safe_min": 50.0,
        "safe_max": 600.0,
        "critical_min": 10.0,
        "critical_max": 1200.0,
        "standard_text": "< 600 μS/cm (Max 800 μS/cm)",
        "ideal": "200 - 400 μS/cm",
        "hazard_low": "Demineralized or distilled water signature.",
        "hazard_high": "Indicates high salinity or presence of conductive chemical contaminants."
    },
    "organic_carbon": {
        "display_name": "Total Organic Carbon (TOC)",
        "unit": "ppm (mg/L)",
        "safe_min": 0.0,
        "safe_max": 4.0,
        "critical_min": 0.0,
        "critical_max": 15.0,
        "standard_text": "< 4.0 ppm (EPA guideline)",
        "ideal": "< 2.0 ppm",
        "hazard_low": "Safe level indicating absence of organic decay.",
        "hazard_high": "Provides nutrients for bacterial proliferation and reacts with disinfectants to form carcinogens."
    },
    "trihalomethanes": {
        "display_name": "Trihalomethanes (THMs)",
        "unit": "μg/L (ppb)",
        "safe_min": 0.0,
        "safe_max": 80.0,
        "critical_min": 0.0,
        "critical_max": 100.0,
        "standard_text": "< 80 μg/L (EPA strict standard)",
        "ideal": "< 40 μg/L",
        "hazard_low": "Negligible risk of disinfection byproduct toxicity.",
        "hazard_high": "Dangerous carcinogenic disinfection byproducts linked to increased risk of cancer and liver damage."
    },
    "turbidity": {
        "display_name": "Turbidity",
        "unit": "NTU",
        "safe_min": 0.0,
        "safe_max": 5.0,
        "critical_min": 0.0,
        "critical_max": 7.0,
        "standard_text": "< 5.0 NTU (WHO standard, ideally < 1 NTU)",
        "ideal": "< 1.0 NTU",
        "hazard_low": "Clear, optically pure water.",
        "hazard_high": "Suspended colloidal matter harbors pathogens, protects viruses from disinfection, and indicates runoff."
    }
}

def evaluate_parameters(values: Dict[str, float]) -> List[ParameterEvaluation]:
    evaluations = []

    for key, spec in STANDARDS.items():
        val = values.get(key, 0.0)
        safe_min = spec["safe_min"]
        safe_max = spec["safe_max"]

        if safe_min <= val <= safe_max:
            status = "safe"
            description = f"Within normal WHO/EPA drinking guideline standards ({spec['ideal']} ideal)."
        elif (val < safe_min and val >= spec["critical_min"]) or (val > safe_max and val <= spec["critical_max"]):
            status = "warning"
            if val < safe_min:
                description = f"Slightly below recommended range. {spec['hazard_low']}"
            else:
                description = f"Elevated above recommended threshold. {spec['hazard_high']}"
        else:
            status = "danger"
            if val < safe_min:
                description = f"Critically low! {spec['hazard_low']}"
            else:
                description = f"Critically elevated! {spec['hazard_high']}"

        evaluations.append(ParameterEvaluation(
            parameter=key,
            display_name=spec["display_name"],
            value=round(val, 2),
            unit=spec["unit"],
            safe_range=spec["standard_text"],
            status=status,
            description=description
        ))

    return evaluations

def generate_recommendations(evaluations: List[ParameterEvaluation], is_safe: bool) -> List[Recommendation]:
    recs = []

    # Map status by parameter key
    eval_dict = {item.parameter: item for item in evaluations}

    # 1. Turbidity
    turb = eval_dict.get("turbidity")
    if turb and turb.status in ("warning", "danger"):
        recs.append(Recommendation(
            category="Physical Filtration",
            title="Sediment & Dual-Media Microfiltration",
            description=f"Turbidity is high ({turb.value} NTU). Install a 5-micron spun polypropylene sediment pre-filter followed by multi-media quartz filtration to remove suspended particulates and colloidal solids.",
            priority="high" if turb.status == "danger" else "medium"
        ))

    # 2. Total Dissolved Solids (Solids) & Conductivity
    solids = eval_dict.get("solids")
    if solids and solids.value > 1000.0:
        recs.append(Recommendation(
            category="Desalination & Demineralization",
            title="Reverse Osmosis (RO) Purification",
            description=f"Dissolved solids level ({solids.value} ppm) exceeds desirable limits. High-pressure RO membrane filtration is strongly advised to strip dissolved salts, heavy metals, and inorganic ions.",
            priority="high" if solids.value > 20000 else "medium"
        ))

    # 3. pH adjustment
    ph_eval = eval_dict.get("ph")
    if ph_eval and ph_eval.value < 6.5:
        recs.append(Recommendation(
            category="pH Balancing",
            title="Calcite / Corosex Neutralization Filter",
            description=f"Acidic pH ({ph_eval.value}) corrodes plumbing and leaches harmful metals. Pass water through a neutralizing calcite bed to raise pH to neutral range (7.0 - 7.5).",
            priority="high"
        ))
    elif ph_eval and ph_eval.value > 8.5:
        recs.append(Recommendation(
            category="pH Balancing",
            title="pH Correction / Acid Injection System",
            description=f"Alkaline pH ({ph_eval.value}) reduces disinfection efficiency and leaves mineral deposits. Treat with automated citric or food-grade neutralizing infusion.",
            priority="medium"
        ))

    # 4. Trihalomethanes & Organic Carbon
    thm = eval_dict.get("trihalomethanes")
    org_carb = eval_dict.get("organic_carbon")
    if (thm and thm.status in ("warning", "danger")) or (org_carb and org_carb.status in ("warning", "danger")):
        recs.append(Recommendation(
            category="Chemical & Organic Purification",
            title="Granular Activated Carbon (GAC) Filtration",
            description="Elevated organic compounds or carcinogenic Trihalomethanes detected. Employ coconut-shell Granular Activated Carbon (GAC) or catalytic carbon block filtration to adsorb toxic organics.",
            priority="high"
        ))

    # 5. Sulfate
    sulfate = eval_dict.get("sulfate")
    if sulfate and sulfate.status in ("warning", "danger"):
        recs.append(Recommendation(
            category="Anion Exchange",
            title="Specialized Anion Exchange Resin Treatment",
            description=f"Sulfate is elevated at {sulfate.value} mg/L, causing a bitter taste and laxative risk. Use strong-base anion exchange softening resin or specialized RO membranes.",
            priority="medium"
        ))

    # 6. Hardness
    hard = eval_dict.get("hardness")
    if hard and hard.value > 250:
        recs.append(Recommendation(
            category="Softening",
            title="Ion-Exchange Water Softener",
            description=f"Water hardness is {hard.value} mg/L (Hard to Very Hard). Utilize a sodium ion-exchange water softener to prevent boiler scaling and pipe encrustation.",
            priority="medium"
        ))

    # 7. Disinfection / Biological Safety
    if not is_safe:
        recs.append(Recommendation(
            category="Disinfection & Sterilization",
            title="UV Sterilization & Certified Laboratory Assay",
            description="AI model has flagged this sample as UNSAFE for direct consumption. Prior to drinking, execute UV-C radiation treatment (or rolling boil for 3+ minutes) and submit to an accredited EPA/ISO water testing laboratory for full microbial and heavy metal panel analysis.",
            priority="high"
        ))
    else:
        recs.append(Recommendation(
            category="Maintenance & Monitoring",
            title="Routine Periodic Quality Assurance",
            description="Water parameters meet safety criteria for drinking. Maintain annual periodic testing, sanitize storage tanks every 6 months, and replace existing sediment cartridges regularly.",
            priority="low"
        ))

    return recs
