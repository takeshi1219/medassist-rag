"""Medical Code Service - ICD-10, SNOMED-CT lookups and translation."""
from typing import List, Optional, Dict
from loguru import logger

from app.models.schemas import (
    ICD10Code, SNOMEDConcept, MedicalTermTranslation, Language
)


class MedicalCodeService:
    """
    Service for medical code lookups and term translation.
    
    Uses demo data for demonstration. In production, integrate with:
    - WHO ICD-10 API
    - NLM SNOMED-CT browser API
    - Medical translation services
    """
    
    def __init__(self):
        """Initialize with demo data."""
        self._icd10_db = self._load_demo_icd10()
        self._snomed_db = self._load_demo_snomed()
        self._translations_db = self._load_demo_translations()
    
    async def search_icd10(self, query: str, limit: int = 20) -> List[ICD10Code]:
        """Search ICD-10 codes by code or description."""
        query_lower = query.lower()
        results = []
        
        for code, data in self._icd10_db.items():
            # Match on code or description
            if (query_lower in code.lower() or 
                query_lower in data["description"].lower()):
                results.append(ICD10Code(
                    code=code,
                    **data
                ))
                
            if len(results) >= limit:
                break
        
        return results
    
    async def get_icd10_code(self, code: str) -> Optional[ICD10Code]:
        """Get a specific ICD-10 code."""
        code_upper = code.upper()
        
        if code_upper in self._icd10_db:
            return ICD10Code(
                code=code_upper,
                **self._icd10_db[code_upper]
            )
        
        return None
    
    async def search_snomed(self, query: str, limit: int = 20) -> List[SNOMEDConcept]:
        """Search SNOMED-CT concepts by ID or term."""
        query_lower = query.lower()
        results = []
        
        for concept_id, data in self._snomed_db.items():
            # Match on ID or term
            if (query_lower in concept_id or 
                query_lower in data["term"].lower() or
                any(query_lower in syn.lower() for syn in data.get("synonyms", []))):
                results.append(SNOMEDConcept(
                    concept_id=concept_id,
                    **data
                ))
                
            if len(results) >= limit:
                break
        
        return results
    
    async def get_snomed_concept(self, concept_id: str) -> Optional[SNOMEDConcept]:
        """Get a specific SNOMED-CT concept."""
        if concept_id in self._snomed_db:
            return SNOMEDConcept(
                concept_id=concept_id,
                **self._snomed_db[concept_id]
            )
        
        return None
    
    async def translate_term(
        self,
        term: str,
        from_language: Language,
        to_language: Language,
        include_explanation: bool = True
    ) -> MedicalTermTranslation:
        """Translate a medical term between languages."""
        term_lower = term.lower()
        
        # Look up in translation database
        translation_data = self._translations_db.get(term_lower, {})
        
        if from_language == Language.JAPANESE:
            # Japanese to English
            translated = translation_data.get("en", self._default_translate_ja_to_en(term))
        else:
            # English to Japanese
            translated = translation_data.get("ja", self._default_translate_en_to_ja(term))
        
        return MedicalTermTranslation(
            original_term=term,
            translated_term=translated,
            from_language=from_language,
            to_language=to_language,
            medical_context=translation_data.get("context"),
            icd10_codes=translation_data.get("icd10", []),
            layman_explanation=translation_data.get("explanation") if include_explanation else None
        )
    
    def _default_translate_ja_to_en(self, term: str) -> str:
        """Default translation for unknown Japanese terms."""
        # In production, use a translation API
        return f"[Translation needed: {term}]"
    
    def _default_translate_en_to_ja(self, term: str) -> str:
        """Default translation for unknown English terms."""
        return f"[翻訳が必要: {term}]"
    
    def _load_demo_icd10(self) -> Dict[str, Dict]:
        """Load demo ICD-10 codes."""
        return {
            # Circulatory System (I00-I99)
            "I10": {
                "description": "Essential (primary) hypertension",
                "category": "Diseases of the circulatory system",
                "subcategory": "Hypertensive diseases",
                "includes": ["High blood pressure", "Hypertension (arterial) (benign) (essential) (malignant)"],
                "excludes": ["Hypertension with heart involvement (I11)", "Hypertension with kidney involvement (I12)"]
            },
            "I11.9": {
                "description": "Hypertensive heart disease without heart failure",
                "category": "Diseases of the circulatory system",
                "subcategory": "Hypertensive diseases",
                "includes": ["Hypertensive heart disease NOS"],
                "excludes": []
            },
            "I21.0": {
                "description": "Acute transmural myocardial infarction of anterior wall",
                "category": "Diseases of the circulatory system",
                "subcategory": "Ischemic heart diseases",
                "includes": ["Anterior (wall) MI", "Anteroapical MI", "Anterolateral MI"],
                "excludes": ["Chronic MI (I25.2)"]
            },
            "I50.9": {
                "description": "Heart failure, unspecified",
                "category": "Diseases of the circulatory system",
                "subcategory": "Heart failure",
                "includes": ["Cardiac failure NOS", "Congestive heart failure NOS"],
                "excludes": []
            },
            # Endocrine (E00-E89)
            "E11.9": {
                "description": "Type 2 diabetes mellitus without complications",
                "category": "Endocrine, nutritional and metabolic diseases",
                "subcategory": "Diabetes mellitus",
                "includes": ["Adult-onset diabetes NOS", "Non-insulin-dependent diabetes"],
                "excludes": ["Type 1 diabetes (E10)"]
            },
            "E11.65": {
                "description": "Type 2 diabetes mellitus with hyperglycemia",
                "category": "Endocrine, nutritional and metabolic diseases",
                "subcategory": "Diabetes mellitus",
                "includes": [],
                "excludes": []
            },
            "E78.0": {
                "description": "Pure hypercholesterolemia",
                "category": "Endocrine, nutritional and metabolic diseases",
                "subcategory": "Disorders of lipoprotein metabolism",
                "includes": ["Familial hypercholesterolemia", "Fredrickson type IIa"],
                "excludes": []
            },
            # Respiratory (J00-J99)
            "J18.9": {
                "description": "Pneumonia, unspecified organism",
                "category": "Diseases of the respiratory system",
                "subcategory": "Pneumonia",
                "includes": ["Community-acquired pneumonia NOS"],
                "excludes": ["Aspiration pneumonia (J69)", "Pneumonia due to solids/liquids"]
            },
            "J44.1": {
                "description": "Chronic obstructive pulmonary disease with acute exacerbation",
                "category": "Diseases of the respiratory system",
                "subcategory": "Chronic lower respiratory diseases",
                "includes": ["COPD exacerbation"],
                "excludes": ["Chronic bronchitis with acute exacerbation"]
            },
            "J45.20": {
                "description": "Mild intermittent asthma, uncomplicated",
                "category": "Diseases of the respiratory system",
                "subcategory": "Asthma",
                "includes": [],
                "excludes": []
            },
            # Mental Health (F00-F99)
            "F32.1": {
                "description": "Major depressive disorder, single episode, moderate",
                "category": "Mental, Behavioral and Neurodevelopmental disorders",
                "subcategory": "Mood disorders",
                "includes": [],
                "excludes": ["Recurrent depressive disorder (F33)"]
            },
            "F41.1": {
                "description": "Generalized anxiety disorder",
                "category": "Mental, Behavioral and Neurodevelopmental disorders",
                "subcategory": "Anxiety disorders",
                "includes": ["Anxiety neurosis", "Anxiety state"],
                "excludes": ["Panic disorder (F41.0)"]
            },
            # Infectious (A00-B99)
            "A41.9": {
                "description": "Sepsis, unspecified organism",
                "category": "Certain infectious and parasitic diseases",
                "subcategory": "Sepsis",
                "includes": ["Septicemia NOS"],
                "excludes": ["Sepsis due to specific organism"]
            },
            "B34.9": {
                "description": "Viral infection, unspecified",
                "category": "Certain infectious and parasitic diseases",
                "subcategory": "Viral infection",
                "includes": ["Viral disease NOS"],
                "excludes": []
            },
            # Neoplasms (C00-D49)
            "C34.90": {
                "description": "Malignant neoplasm of unspecified part of unspecified bronchus or lung",
                "category": "Neoplasms",
                "subcategory": "Malignant neoplasms of respiratory organs",
                "includes": ["Lung cancer NOS"],
                "excludes": []
            },
            "C50.919": {
                "description": "Malignant neoplasm of unspecified site of unspecified female breast",
                "category": "Neoplasms",
                "subcategory": "Malignant neoplasms of breast",
                "includes": ["Breast cancer NOS"],
                "excludes": []
            }
        }
    
    def _load_demo_snomed(self) -> Dict[str, Dict]:
        """Load demo SNOMED-CT concepts."""
        return {
            "38341003": {
                "term": "Hypertensive disorder, systemic arterial",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Hypertension", "High blood pressure", "HTN"]
            },
            "44054006": {
                "term": "Type 2 diabetes mellitus",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Type II diabetes", "T2DM", "Adult-onset diabetes", "Non-insulin dependent diabetes"]
            },
            "22298006": {
                "term": "Myocardial infarction",
                "semantic_type": "Clinical Finding",
                "synonyms": ["MI", "Heart attack", "Acute MI", "AMI"]
            },
            "233604007": {
                "term": "Pneumonia",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Lung infection", "Pulmonary infection"]
            },
            "84114007": {
                "term": "Heart failure",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Cardiac failure", "CHF", "Congestive heart failure"]
            },
            "35489007": {
                "term": "Depressive disorder",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Depression", "Major depression", "Clinical depression"]
            },
            "197480006": {
                "term": "Anxiety disorder",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Anxiety", "Anxiety state", "GAD"]
            },
            "13645005": {
                "term": "Chronic obstructive pulmonary disease",
                "semantic_type": "Clinical Finding",
                "synonyms": ["COPD", "Chronic airflow obstruction", "Chronic obstructive lung disease"]
            },
            "195967001": {
                "term": "Asthma",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Bronchial asthma", "Asthmatic"]
            },
            "91302008": {
                "term": "Sepsis",
                "semantic_type": "Clinical Finding",
                "synonyms": ["Septicemia", "Blood poisoning", "Systemic infection"]
            }
        }
    
    def _load_demo_translations(self) -> Dict[str, Dict]:
        """Load demo medical term translations (Japanese-English)."""
        return {
            # Japanese terms (romanized keys for demo)
            "高血圧": {
                "en": "Hypertension",
                "ja": "高血圧 (こうけつあつ)",
                "context": "Cardiovascular condition",
                "icd10": ["I10", "I11.9"],
                "explanation": "A chronic medical condition where blood pressure in the arteries is persistently elevated, increasing the risk of heart disease and stroke."
            },
            "糖尿病": {
                "en": "Diabetes mellitus",
                "ja": "糖尿病 (とうにょうびょう)",
                "context": "Metabolic disorder",
                "icd10": ["E11.9"],
                "explanation": "A metabolic disease characterized by high blood sugar levels due to insufficient insulin production or cells not responding properly to insulin."
            },
            "肺炎": {
                "en": "Pneumonia",
                "ja": "肺炎 (はいえん)",
                "context": "Respiratory infection",
                "icd10": ["J18.9"],
                "explanation": "An infection that inflames the air sacs in one or both lungs, which may fill with fluid or pus."
            },
            "心筋梗塞": {
                "en": "Myocardial infarction",
                "ja": "心筋梗塞 (しんきんこうそく)",
                "context": "Cardiovascular emergency",
                "icd10": ["I21.0"],
                "explanation": "A heart attack - occurs when blood flow to part of the heart muscle is blocked, causing heart tissue damage."
            },
            "心不全": {
                "en": "Heart failure",
                "ja": "心不全 (しんふぜん)",
                "context": "Cardiovascular condition",
                "icd10": ["I50.9"],
                "explanation": "A condition where the heart cannot pump blood efficiently to meet the body's needs."
            },
            # English terms
            "hypertension": {
                "en": "Hypertension",
                "ja": "高血圧 (こうけつあつ)",
                "context": "Cardiovascular condition",
                "icd10": ["I10"],
                "explanation": "High blood pressure - a chronic condition where the force of blood against artery walls is too high."
            },
            "diabetes": {
                "en": "Diabetes mellitus",
                "ja": "糖尿病 (とうにょうびょう)",
                "context": "Metabolic disorder",
                "icd10": ["E11.9"],
                "explanation": "A group of metabolic diseases causing high blood sugar levels."
            },
            "pneumonia": {
                "en": "Pneumonia",
                "ja": "肺炎 (はいえん)",
                "context": "Respiratory infection",
                "icd10": ["J18.9"],
                "explanation": "Lung infection causing inflammation and fluid buildup in the air sacs."
            },
            "heart attack": {
                "en": "Myocardial infarction",
                "ja": "心筋梗塞 (しんきんこうそく)",
                "context": "Cardiovascular emergency",
                "icd10": ["I21.0"],
                "explanation": "Death of heart muscle tissue due to blocked blood flow."
            },
            "stroke": {
                "en": "Cerebrovascular accident",
                "ja": "脳卒中 (のうそっちゅう)",
                "context": "Neurological emergency",
                "icd10": ["I63.9"],
                "explanation": "Brain damage from interrupted blood supply, either from a blockage or bleeding."
            }
        }

