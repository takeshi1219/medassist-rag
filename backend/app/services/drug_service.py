"""Drug Interaction Service - Business logic for drug interactions."""
from typing import List, Dict, Any, Optional
from itertools import combinations
from loguru import logger

from app.models.schemas import (
    DrugCheckResponse, DrugInteraction, Drug, InteractionSeverity
)


class DrugInteractionService:
    """
    Service for checking drug interactions and providing drug information.
    
    Uses a local database of common drug interactions for demonstration.
    In production, integrate with DrugBank API or similar service.
    """
    
    def __init__(self):
        """Initialize with demo drug interaction data."""
        self._interactions_db = self._load_demo_interactions()
        self._drugs_db = self._load_demo_drugs()
    
    async def check_interactions(self, drugs: List[str]) -> DrugCheckResponse:
        """
        Check for interactions between a list of drugs.
        
        Args:
            drugs: List of drug names to check
            
        Returns:
            DrugCheckResponse with interactions and warnings
        """
        interactions = []
        warnings = []
        has_severe = False
        has_contraindicated = False
        
        # Normalize drug names
        normalized_drugs = [d.lower().strip() for d in drugs]
        
        # Check all pairs
        for drug_a, drug_b in combinations(normalized_drugs, 2):
            interaction = self._find_interaction(drug_a, drug_b)
            if interaction:
                interactions.append(interaction)
                
                if interaction.severity == InteractionSeverity.SEVERE:
                    has_severe = True
                    warnings.append(
                        f"⚠️ SEVERE interaction between {drug_a} and {drug_b}: "
                        f"{interaction.description}"
                    )
                elif interaction.severity == InteractionSeverity.CONTRAINDICATED:
                    has_contraindicated = True
                    warnings.append(
                        f"🚫 CONTRAINDICATED: {drug_a} and {drug_b} should not be used together. "
                        f"{interaction.description}"
                    )
        
        # Get alternative suggestions for severe/contraindicated interactions
        alternatives = []
        if has_severe or has_contraindicated:
            for interaction in interactions:
                if interaction.severity in [InteractionSeverity.SEVERE, InteractionSeverity.CONTRAINDICATED]:
                    alts = await self.get_alternatives(interaction.drug_a)
                    alternatives.extend(alts[:2])  # Limit alternatives
        
        return DrugCheckResponse(
            interactions=interactions,
            alternatives=alternatives,
            warnings=warnings,
            checked_drugs=drugs,
            has_severe_interactions=has_severe,
            has_contraindications=has_contraindicated
        )
    
    def _find_interaction(self, drug_a: str, drug_b: str) -> Optional[DrugInteraction]:
        """Find interaction between two drugs in the database."""
        # Check both orderings
        key1 = f"{drug_a}:{drug_b}"
        key2 = f"{drug_b}:{drug_a}"
        
        interaction_data = self._interactions_db.get(key1) or self._interactions_db.get(key2)
        
        if interaction_data:
            return DrugInteraction(
                drug_a=drug_a.title(),
                drug_b=drug_b.title(),
                severity=InteractionSeverity(interaction_data["severity"]),
                description=interaction_data["description"],
                mechanism=interaction_data.get("mechanism"),
                management=interaction_data.get("management"),
                clinical_effects=interaction_data.get("clinical_effects", []),
                source=interaction_data.get("source", "MedAssist Drug Database")
            )
        
        return None
    
    async def search_drugs(self, query: str, limit: int = 10) -> List[Drug]:
        """Search drugs by name or class."""
        query_lower = query.lower()
        results = []
        
        for drug_name, drug_data in self._drugs_db.items():
            if query_lower in drug_name.lower():
                results.append(Drug(**drug_data))
            elif any(query_lower in brand.lower() for brand in drug_data.get("brand_names", [])):
                results.append(Drug(**drug_data))
            elif query_lower in drug_data.get("drug_class", "").lower():
                results.append(Drug(**drug_data))
                
            if len(results) >= limit:
                break
        
        return results
    
    async def get_drug_info(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a drug."""
        drug_lower = drug_name.lower()
        
        if drug_lower in self._drugs_db:
            drug_data = self._drugs_db[drug_lower]
            
            # Find all interactions for this drug
            interactions = []
            for key, interaction in self._interactions_db.items():
                drugs = key.split(":")
                if drug_lower in drugs:
                    other_drug = drugs[0] if drugs[1] == drug_lower else drugs[1]
                    interactions.append({
                        "drug": other_drug.title(),
                        "severity": interaction["severity"],
                        "description": interaction["description"]
                    })
            
            return {
                **drug_data,
                "known_interactions": interactions
            }
        
        return None
    
    async def get_alternatives(
        self,
        drug_name: str,
        reason: str = None
    ) -> List[Drug]:
        """Get alternative medications for a drug."""
        drug_lower = drug_name.lower()
        
        if drug_lower not in self._drugs_db:
            return []
        
        drug_class = self._drugs_db[drug_lower].get("drug_class", "")
        alternatives = []
        
        # Find drugs in the same class
        for name, data in self._drugs_db.items():
            if name != drug_lower and data.get("drug_class") == drug_class:
                alternatives.append(Drug(**data))
        
        return alternatives[:5]  # Limit to 5 alternatives
    
    def _load_demo_interactions(self) -> Dict[str, Dict]:
        """Load demo drug interaction data."""
        return {
            # ACE Inhibitors + Potassium-sparing diuretics
            "lisinopril:spironolactone": {
                "severity": "severe",
                "description": "Risk of hyperkalemia (elevated potassium levels)",
                "mechanism": "Both drugs increase potassium retention",
                "management": "Monitor potassium levels closely. Consider alternative diuretic.",
                "clinical_effects": ["Hyperkalemia", "Cardiac arrhythmias", "Muscle weakness"],
                "source": "UpToDate Drug Interactions"
            },
            # NSAIDs + Anticoagulants
            "ibuprofen:warfarin": {
                "severity": "severe",
                "description": "Increased risk of gastrointestinal bleeding",
                "mechanism": "NSAIDs inhibit platelet function and may cause GI ulceration",
                "management": "Avoid combination if possible. Use acetaminophen instead.",
                "clinical_effects": ["GI bleeding", "Prolonged INR", "Bruising"],
                "source": "Clinical Pharmacology Database"
            },
            # Metformin + Contrast dye
            "metformin:iodinated contrast": {
                "severity": "severe",
                "description": "Risk of lactic acidosis, especially in renal impairment",
                "mechanism": "Contrast can cause acute kidney injury, impairing metformin clearance",
                "management": "Hold metformin 48 hours before and after contrast. Check renal function.",
                "clinical_effects": ["Lactic acidosis", "Acute kidney injury"],
                "source": "ACR Manual on Contrast Media"
            },
            # MAOIs + SSRIs
            "phenelzine:sertraline": {
                "severity": "contraindicated",
                "description": "Risk of serotonin syndrome - potentially fatal",
                "mechanism": "Combined serotonergic effects lead to excessive serotonin",
                "management": "Do not combine. Allow 2-week washout between medications.",
                "clinical_effects": ["Serotonin syndrome", "Hyperthermia", "Seizures", "Death"],
                "source": "FDA Drug Safety Communication"
            },
            # Statins + Grapefruit
            "simvastatin:grapefruit": {
                "severity": "moderate",
                "description": "Increased statin levels, risk of myopathy",
                "mechanism": "Grapefruit inhibits CYP3A4, reducing statin metabolism",
                "management": "Avoid grapefruit or use statin not affected by CYP3A4",
                "clinical_effects": ["Myopathy", "Rhabdomyolysis", "Elevated CK"],
                "source": "FDA Drug Label"
            },
            # Fluoroquinolones + NSAIDs
            "ciprofloxacin:ibuprofen": {
                "severity": "moderate",
                "description": "Increased risk of CNS stimulation and seizures",
                "mechanism": "Combined inhibition of GABA receptors",
                "management": "Use with caution. Monitor for CNS symptoms.",
                "clinical_effects": ["Seizures", "Confusion", "Tremors"],
                "source": "Lexicomp Drug Interactions"
            },
            # Digoxin + Amiodarone
            "digoxin:amiodarone": {
                "severity": "severe",
                "description": "Increased digoxin levels, risk of toxicity",
                "mechanism": "Amiodarone inhibits P-glycoprotein and renal clearance",
                "management": "Reduce digoxin dose by 50%. Monitor levels closely.",
                "clinical_effects": ["Digoxin toxicity", "Arrhythmias", "Nausea", "Visual changes"],
                "source": "Clinical Pharmacology Database"
            },
            # Clopidogrel + PPIs
            "clopidogrel:omeprazole": {
                "severity": "moderate",
                "description": "Reduced clopidogrel efficacy",
                "mechanism": "Omeprazole inhibits CYP2C19, reducing active metabolite formation",
                "management": "Consider pantoprazole or H2 blocker instead",
                "clinical_effects": ["Reduced antiplatelet effect", "Increased cardiovascular events"],
                "source": "FDA Drug Safety Communication"
            },
            # Beta blockers + Calcium channel blockers (non-DHP)
            "metoprolol:verapamil": {
                "severity": "severe",
                "description": "Risk of severe bradycardia and heart block",
                "mechanism": "Combined negative chronotropic and dromotropic effects",
                "management": "Avoid combination or monitor closely with ECG",
                "clinical_effects": ["Bradycardia", "Heart block", "Hypotension", "Heart failure"],
                "source": "UpToDate Drug Interactions"
            },
            # Aspirin + Ibuprofen
            "aspirin:ibuprofen": {
                "severity": "moderate",
                "description": "Ibuprofen may reduce cardioprotective effect of aspirin",
                "mechanism": "Competitive binding to COX-1 active site",
                "management": "Take aspirin 30 min before ibuprofen, or use different NSAID timing",
                "clinical_effects": ["Reduced antiplatelet effect", "GI bleeding risk"],
                "source": "FDA Science Paper"
            }
        }
    
    def _load_demo_drugs(self) -> Dict[str, Dict]:
        """Load demo drug database."""
        return {
            "lisinopril": {
                "name": "Lisinopril",
                "generic_name": "Lisinopril",
                "brand_names": ["Prinivil", "Zestril"],
                "drug_class": "ACE Inhibitor",
                "description": "Angiotensin-converting enzyme (ACE) inhibitor for hypertension and heart failure"
            },
            "metformin": {
                "name": "Metformin",
                "generic_name": "Metformin Hydrochloride",
                "brand_names": ["Glucophage", "Fortamet", "Riomet"],
                "drug_class": "Biguanide",
                "description": "First-line treatment for type 2 diabetes mellitus"
            },
            "amlodipine": {
                "name": "Amlodipine",
                "generic_name": "Amlodipine Besylate",
                "brand_names": ["Norvasc"],
                "drug_class": "Calcium Channel Blocker (DHP)",
                "description": "Dihydropyridine calcium channel blocker for hypertension and angina"
            },
            "warfarin": {
                "name": "Warfarin",
                "generic_name": "Warfarin Sodium",
                "brand_names": ["Coumadin", "Jantoven"],
                "drug_class": "Anticoagulant",
                "description": "Vitamin K antagonist anticoagulant for preventing blood clots"
            },
            "omeprazole": {
                "name": "Omeprazole",
                "generic_name": "Omeprazole",
                "brand_names": ["Prilosec", "Losec"],
                "drug_class": "Proton Pump Inhibitor",
                "description": "PPI for GERD, peptic ulcers, and H. pylori eradication"
            },
            "sertraline": {
                "name": "Sertraline",
                "generic_name": "Sertraline Hydrochloride",
                "brand_names": ["Zoloft"],
                "drug_class": "SSRI",
                "description": "Selective serotonin reuptake inhibitor for depression and anxiety"
            },
            "metoprolol": {
                "name": "Metoprolol",
                "generic_name": "Metoprolol Succinate/Tartrate",
                "brand_names": ["Lopressor", "Toprol-XL"],
                "drug_class": "Beta Blocker",
                "description": "Beta-1 selective blocker for hypertension, angina, and heart failure"
            },
            "atorvastatin": {
                "name": "Atorvastatin",
                "generic_name": "Atorvastatin Calcium",
                "brand_names": ["Lipitor"],
                "drug_class": "Statin",
                "description": "HMG-CoA reductase inhibitor for hyperlipidemia"
            },
            "ibuprofen": {
                "name": "Ibuprofen",
                "generic_name": "Ibuprofen",
                "brand_names": ["Advil", "Motrin"],
                "drug_class": "NSAID",
                "description": "Non-steroidal anti-inflammatory drug for pain and inflammation"
            },
            "aspirin": {
                "name": "Aspirin",
                "generic_name": "Acetylsalicylic Acid",
                "brand_names": ["Bayer", "Ecotrin"],
                "drug_class": "NSAID/Antiplatelet",
                "description": "Analgesic, antipyretic, anti-inflammatory, and antiplatelet agent"
            },
            "losartan": {
                "name": "Losartan",
                "generic_name": "Losartan Potassium",
                "brand_names": ["Cozaar"],
                "drug_class": "ARB",
                "description": "Angiotensin II receptor blocker for hypertension"
            },
            "spironolactone": {
                "name": "Spironolactone",
                "generic_name": "Spironolactone",
                "brand_names": ["Aldactone"],
                "drug_class": "Potassium-Sparing Diuretic",
                "description": "Aldosterone antagonist for heart failure and hypertension"
            },
            "clopidogrel": {
                "name": "Clopidogrel",
                "generic_name": "Clopidogrel Bisulfate",
                "brand_names": ["Plavix"],
                "drug_class": "Antiplatelet",
                "description": "P2Y12 inhibitor for preventing cardiovascular events"
            },
            "pantoprazole": {
                "name": "Pantoprazole",
                "generic_name": "Pantoprazole Sodium",
                "brand_names": ["Protonix"],
                "drug_class": "Proton Pump Inhibitor",
                "description": "PPI with less CYP2C19 interaction than omeprazole"
            }
        }

