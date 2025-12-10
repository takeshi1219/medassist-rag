#!/usr/bin/env python3
"""
MedAssist RAG - Vector Database Seeding Script

This script seeds the vector database with sample medical documents
for demonstration purposes.

Usage:
    python scripts/seed_vector_db.py
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Load .env file from backend folder
from dotenv import load_dotenv
env_path = backend_path / ".env"
load_dotenv(env_path)
print(f"Loaded environment from: {env_path}")

import asyncio
from typing import List, Dict
from loguru import logger

# Sample medical documents for seeding
SAMPLE_DOCUMENTS = [
    {
        "content": """Hypertension Management Guidelines (2024): First-line treatments for essential 
        hypertension include thiazide diuretics (e.g., hydrochlorothiazide, chlorthalidone), 
        ACE inhibitors (e.g., lisinopril, enalapril), ARBs (e.g., losartan, valsartan), and 
        calcium channel blockers (e.g., amlodipine, nifedipine). The target blood pressure for 
        most adults is <130/80 mmHg. Lifestyle modifications should be recommended for all patients 
        and include: DASH diet (Dietary Approaches to Stop Hypertension), sodium restriction to 
        <2.3g/day (ideally <1.5g/day), regular aerobic exercise (150 minutes/week of moderate 
        intensity), weight management (BMI <25), limiting alcohol intake, and smoking cessation.""",
        "metadata": {
            "title": "ACC/AHA Hypertension Guidelines 2024",
            "authors": ["American College of Cardiology", "American Heart Association"],
            "journal": "Journal of the American College of Cardiology",
            "year": 2024,
            "doi": "10.1016/j.jacc.2024.01.001",
            "source_type": "guideline"
        }
    },
    {
        "content": """Drug interactions with antihypertensive medications require careful monitoring. 
        NSAIDs (including ibuprofen, naproxen) can significantly reduce the effectiveness of 
        ACE inhibitors, ARBs, and diuretics by promoting sodium and water retention. Potassium-sparing 
        diuretics (spironolactone, eplerenone) combined with ACE inhibitors or ARBs substantially 
        increase the risk of hyperkalemia - serum potassium should be monitored regularly. 
        Grapefruit juice affects the metabolism of certain calcium channel blockers (felodipine, 
        nifedipine) by inhibiting CYP3A4, leading to increased drug levels and potential toxicity. 
        Beta-blockers combined with non-dihydropyridine calcium channel blockers (verapamil, diltiazem) 
        can cause severe bradycardia and heart block.""",
        "metadata": {
            "title": "Antihypertensive Drug Interactions: A Comprehensive Review",
            "authors": ["Smith J", "Johnson M", "Williams R"],
            "journal": "Clinical Pharmacology & Therapeutics",
            "year": 2023,
            "pmid": "34567890",
            "source_type": "paper"
        }
    },
    {
        "content": """Type 2 Diabetes Mellitus Treatment Algorithm (2024): Metformin remains the 
        preferred first-line pharmacologic therapy unless contraindicated (eGFR <30 mL/min/1.73m², 
        acute kidney injury, hepatic impairment, or metabolic acidosis risk). For patients with 
        established atherosclerotic cardiovascular disease (ASCVD), heart failure, or chronic kidney 
        disease, SGLT2 inhibitors (empagliflozin, dapagliflozin, canagliflozin) or GLP-1 receptor 
        agonists (semaglutide, dulaglutide, liraglutide) are recommended regardless of A1C level, 
        given their proven cardiovascular and renal benefits. Target A1C is <7% for most adults, 
        but should be individualized based on hypoglycemia risk, disease duration, life expectancy, 
        comorbidities, and patient preferences.""",
        "metadata": {
            "title": "Standards of Medical Care in Diabetes - 2024",
            "authors": ["American Diabetes Association"],
            "journal": "Diabetes Care",
            "year": 2024,
            "doi": "10.2337/dc24-S001",
            "source_type": "guideline"
        }
    },
    {
        "content": """Clinical presentation of acute myocardial infarction (AMI): Classic symptoms 
        include chest pain or pressure (described as squeezing, tightness, or heaviness), often 
        radiating to the left arm, jaw, neck, or back. Associated symptoms include dyspnea, 
        diaphoresis (sweating), nausea, vomiting, and lightheadedness. IMPORTANT: Atypical 
        presentations are more common in women, elderly patients (>75 years), and diabetic patients. 
        These patients may present with fatigue, generalized weakness, dyspnea without chest pain, 
        epigastric discomfort, or syncope. ECG changes (ST-elevation, ST-depression, T-wave inversions) 
        and cardiac troponin elevation confirm the diagnosis. Time to reperfusion is critical - 
        door-to-balloon time should be <90 minutes for STEMI.""",
        "metadata": {
            "title": "Acute Coronary Syndromes: Recognition and Management",
            "authors": ["Chen L", "Anderson K"],
            "journal": "New England Journal of Medicine",
            "year": 2023,
            "pmid": "36789012",
            "source_type": "paper"
        }
    },
    {
        "content": """Community-Acquired Pneumonia (CAP) Antibiotic Selection (IDSA/ATS 2023): 
        For outpatients without comorbidities or risk factors for resistant pathogens: 
        amoxicillin 1g TID or doxycycline 100mg BID or a macrolide (if local resistance <25%). 
        For outpatients with comorbidities (chronic heart, lung, liver, or kidney disease; 
        diabetes; alcoholism; malignancy; asplenia): combination therapy with amoxicillin-clavulanate 
        or cephalosporin PLUS macrolide or doxycycline; OR respiratory fluoroquinolone monotherapy 
        (moxifloxacin, levofloxacin). For inpatients (non-ICU): beta-lactam (ampicillin-sulbactam, 
        ceftriaxone, cefotaxime) PLUS macrolide or respiratory fluoroquinolone alone. 
        Duration: typically 5-7 days for uncomplicated CAP with clinical stability.""",
        "metadata": {
            "title": "IDSA/ATS Community-Acquired Pneumonia Guidelines 2023",
            "authors": ["Infectious Diseases Society of America"],
            "journal": "Clinical Infectious Diseases",
            "year": 2023,
            "doi": "10.1093/cid/ciad123",
            "source_type": "guideline"
        }
    },
    {
        "content": """Heart Failure with Reduced Ejection Fraction (HFrEF) Guideline-Directed Medical 
        Therapy (GDMT): Four pillars of therapy should be initiated and optimized in all eligible 
        patients: 1) ACEI/ARB/ARNI - ARNI (sacubitril/valsartan) is preferred over ACEI/ARB when 
        tolerated; 2) Beta-blockers - carvedilol, metoprolol succinate, or bisoprolol; 
        3) Mineralocorticoid receptor antagonists (MRA) - spironolactone or eplerenone; 
        4) SGLT2 inhibitors - dapagliflozin or empagliflozin (regardless of diabetes status). 
        Additional therapies include hydralazine/nitrates for African American patients, 
        ivabradine for symptomatic patients on maximally tolerated beta-blocker with HR ≥70 bpm, 
        and loop diuretics for volume management. Target doses should be achieved when tolerated.""",
        "metadata": {
            "title": "2023 AHA/ACC/HFSA Heart Failure Guidelines",
            "authors": ["American Heart Association", "American College of Cardiology"],
            "journal": "Circulation",
            "year": 2023,
            "doi": "10.1161/CIR.0000000000001063",
            "source_type": "guideline"
        }
    },
    {
        "content": """Warfarin Management and Drug Interactions: Warfarin has a narrow therapeutic 
        index requiring careful INR monitoring (target 2.0-3.0 for most indications, 2.5-3.5 for 
        mechanical heart valves). Drugs that INCREASE warfarin effect (bleeding risk): amiodarone, 
        fluconazole, metronidazole, TMP-SMX, fluoroquinolones, macrolides, statins, NSAIDs, 
        acetaminophen (high dose), SSRIs. Drugs that DECREASE warfarin effect: rifampin, 
        carbamazepine, phenytoin, barbiturates, St. John's Wort. Foods high in vitamin K 
        (green leafy vegetables) can decrease anticoagulation. Patients should maintain consistent 
        vitamin K intake rather than avoiding these foods. Bridging anticoagulation decisions 
        should be individualized based on thrombotic vs bleeding risk.""",
        "metadata": {
            "title": "Warfarin Drug Interactions and Management",
            "authors": ["Garcia D", "Crowther M"],
            "journal": "Chest",
            "year": 2023,
            "pmid": "35678901",
            "source_type": "paper"
        }
    },
    {
        "content": """Acute Kidney Injury (AKI) Management: AKI is defined as increase in serum 
        creatinine ≥0.3 mg/dL within 48 hours, or increase ≥1.5x baseline within 7 days, or 
        urine output <0.5 mL/kg/hr for 6 hours. KDIGO staging: Stage 1 (Cr 1.5-1.9x baseline), 
        Stage 2 (Cr 2.0-2.9x baseline), Stage 3 (Cr ≥3x baseline or Cr ≥4.0 mg/dL or RRT initiation). 
        Key management principles: 1) Identify and treat underlying cause (prerenal, intrinsic, 
        postrenal); 2) Discontinue nephrotoxic medications (NSAIDs, aminoglycosides, contrast agents, 
        ACE inhibitors in acute setting); 3) Optimize volume status; 4) Avoid hyperkalemia and 
        metabolic acidosis; 5) Adjust medication dosing for reduced GFR; 6) Consider nephrology 
        consultation for stage 2-3 AKI or unclear etiology.""",
        "metadata": {
            "title": "KDIGO Clinical Practice Guideline for Acute Kidney Injury",
            "authors": ["Kidney Disease: Improving Global Outcomes"],
            "journal": "Kidney International Supplements",
            "year": 2023,
            "doi": "10.1038/kisup.2023.1",
            "source_type": "guideline"
        }
    },
    {
        "content": """Sepsis Recognition and Initial Management (Surviving Sepsis Campaign 2023): 
        Sepsis is defined as life-threatening organ dysfunction caused by dysregulated host response 
        to infection. Use qSOFA for bedside screening (altered mental status, RR ≥22, SBP ≤100). 
        Hour-1 Bundle: 1) Measure lactate (remeasure if >2 mmol/L); 2) Obtain blood cultures before 
        antibiotics; 3) Administer broad-spectrum antibiotics; 4) Begin rapid fluid resuscitation 
        with 30 mL/kg crystalloid for hypotension or lactate ≥4 mmol/L; 5) Apply vasopressors 
        (norepinephrine first-line) if hypotensive during or after fluid resuscitation to maintain 
        MAP ≥65 mmHg. De-escalate antibiotics based on culture results and clinical improvement. 
        Corticosteroids (hydrocortisone 200mg/day) for refractory septic shock.""",
        "metadata": {
            "title": "Surviving Sepsis Campaign: International Guidelines 2023",
            "authors": ["Society of Critical Care Medicine"],
            "journal": "Critical Care Medicine",
            "year": 2023,
            "doi": "10.1097/CCM.0000000000005804",
            "source_type": "guideline"
        }
    },
    {
        "content": """Atrial Fibrillation Stroke Prevention: CHA2DS2-VASc score determines stroke 
        risk and anticoagulation need. Score components: Congestive heart failure (1), Hypertension 
        (1), Age ≥75 (2), Diabetes (1), Stroke/TIA/thromboembolism (2), Vascular disease (1), 
        Age 65-74 (1), Sex category female (1). Anticoagulation recommendations: Score 0 (men) or 
        1 (women) - no anticoagulation; Score 1 (men) - consider anticoagulation; Score ≥2 - 
        anticoagulation recommended. Direct oral anticoagulants (DOACs: apixaban, rivaroxaban, 
        dabigatran, edoxaban) are preferred over warfarin for non-valvular AF. Warfarin remains 
        indicated for mechanical heart valves and moderate-severe mitral stenosis. 
        HAS-BLED score assesses bleeding risk but should not preclude anticoagulation in 
        high-risk patients.""",
        "metadata": {
            "title": "2023 ACC/AHA Atrial Fibrillation Guidelines",
            "authors": ["American College of Cardiology"],
            "journal": "Journal of the American College of Cardiology",
            "year": 2023,
            "doi": "10.1016/j.jacc.2023.08.017",
            "source_type": "guideline"
        }
    }
]


async def seed_chroma():
    """Seed ChromaDB with sample documents."""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Connect to Chroma
        client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", "8001")),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name="medassist",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Check if already seeded
        existing = collection.count()
        if existing > 0:
            logger.info(f"Collection already has {existing} documents. Skipping seed.")
            return
        
        logger.info("Generating embeddings for sample documents...")
        
        # Generate embeddings using OpenAI
        from openai import OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        for i, doc in enumerate(SAMPLE_DOCUMENTS):
            # Get embedding
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=doc["content"]
            )
            embedding = response.data[0].embedding
            
            documents.append(doc["content"])
            embeddings.append(embedding)
            metadatas.append(doc["metadata"])
            ids.append(f"doc_{i}")
            
            logger.info(f"Processed document {i+1}/{len(SAMPLE_DOCUMENTS)}: {doc['metadata']['title'][:50]}...")
        
        # Add to collection
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Successfully seeded {len(documents)} documents to ChromaDB")
        
    except Exception as e:
        logger.error(f"Error seeding ChromaDB: {e}")
        raise


async def seed_pinecone():
    """Seed Pinecone with sample documents."""
    try:
        from pinecone import Pinecone
        from openai import OpenAI
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "medassist"))
        
        # Check existing vectors
        stats = index.describe_index_stats()
        if stats.total_vector_count > 0:
            logger.info(f"Index already has {stats.total_vector_count} vectors. Skipping seed.")
            return
        
        logger.info("Generating embeddings for sample documents...")
        
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        vectors = []
        for i, doc in enumerate(SAMPLE_DOCUMENTS):
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=doc["content"]
            )
            embedding = response.data[0].embedding
            
            vectors.append({
                "id": f"doc_{i}",
                "values": embedding,
                "metadata": {
                    **doc["metadata"],
                    "content": doc["content"]
                }
            })
            
            logger.info(f"Processed document {i+1}/{len(SAMPLE_DOCUMENTS)}")
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors)
        
        logger.info(f"Successfully seeded {len(vectors)} documents to Pinecone")
        
    except Exception as e:
        logger.error(f"Error seeding Pinecone: {e}")
        raise


async def main():
    """Main entry point."""
    logger.info("Starting vector database seeding...")
    
    use_chroma = os.getenv("USE_CHROMA", "true").lower() == "true"
    
    if use_chroma:
        await seed_chroma()
    else:
        await seed_pinecone()
    
    logger.info("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(main())

