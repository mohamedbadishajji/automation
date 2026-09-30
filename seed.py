from datetime import datetime, timezone, timedelta
from app.core.database import SessionLocal, engine, Base
from app.models.tender import Tender, TenderStatus
from app.models.research import ProspectResearch
from app.models.asset import InternalAsset, AssetType, TenderAssetMatch
from app.models.proposal import Proposal


def seed_database():
    db = SessionLocal()
    try:
        print("Reinitialisation des tables...")
        # Optionnel : Recree les tables proprement pour le seed
        Base.metadata.create_all(bind=engine)

        # Verification si des donnees existent deja
        if db.query(Tender).first():
            print("La base de donnees contient deja des donnees. Seed annule.")
            return

        print("Insertion des actifs internes d'OliveSoft (CVs & Projets)...")

        # 1. Ajout des CVs et Projets Références (Internal Assets)
        asset_cv1 = InternalAsset(
            title="CV - Aymen Kassab (Lead AI & Data Engineer)",
            asset_type=AssetType.CV,
            description="Expert en architectures RAG, orchestrations agentiques n8n, LLMs (OpenAI/Ollama) et backend FastAPI avec 6 ans d'experience.",
            qdrant_point_id="qdrant-uuid-cv-001",
            metadata_json={"skills": ["Python", "FastAPI", "RAG", "n8n", "Qdrant", "PostgreSQL"],
                           "seniority": "Senior"},
            file_url="https://storage.olivesoft.tn/cvs/aymen_kassab.pdf"
        )

        asset_cv2 = InternalAsset(
            title="CV - Sarra Ben Ali (Senior Fullstack Developer)",
            asset_type=AssetType.CV,
            description="Developpeuse Fullstack specialisee en interfaces React/Next.js, Tailwind CSS et integration d'APIs REST complexes.",
            qdrant_point_id="qdrant-uuid-cv-002",
            metadata_json={"skills": ["React", "Next.js", "TypeScript", "Tailwind CSS", "REST API"],
                           "seniority": "Senior"},
            file_url="https://storage.olivesoft.tn/cvs/sarra_ben_ali.pdf"
        )

        asset_project1 = InternalAsset(
            title="Projet Reference - Plateforme IA FinTech Banque Nationale",
            asset_type=AssetType.PAST_PROJECT,
            description="Conception et deploiement d'un systeme d'analyse automatisée de documents financiers et generation de rapports via LLM pour une grande banque.",
            qdrant_point_id="qdrant-uuid-proj-001",
            metadata_json={"client_sector": "Banking", "tech_stack": ["Python", "LangChain", "PostgreSQL", "React"],
                           "duration_months": 8},
            file_url="https://storage.olivesoft.tn/projects/fintech_case_study.pdf"
        )

        db.add_all([asset_cv1, asset_cv2, asset_project1])
        db.commit()
        db.refresh(asset_cv1)
        db.refresh(asset_cv2)
        db.refresh(asset_project1)

        print("Insertion des appels d'offres (Tenders)...")

        # 2. Ajout d'un Appel d'Offres (Tender 1 - Complet avec recherche & proposal)
        tender1 = Tender(
            title="Appel d'Offres - Automation de l'Intelligence Financiere & Generation de Rapports",
            organization_name="ATB Bank Group",
            source_url="https://marchespublics.tn/tenders/2026-atb-ai-042",
            raw_description="Le groupe souhaite se doter d'une solution d'IA capable de crawler les marches publics, d'effectuer une recherche d'intelligence sur les prospects et d'automatiser la redaction des propositions commerciales personnalisees sous format presentation.",
            status=TenderStatus.PROPOSAL_READY,
            is_partial=False,
            deadline=datetime.now(timezone.utc) + timedelta(days=21)
        )

        # Tender 2 (En cours de recherche)
        tender2 = Tender(
            title="Mise en place d'un Portail Cloud & Chatbot RAG RH",
            organization_name="Ministere des Technologies",
            source_url="https://marchespublics.tn/tenders/2026-min-tech-018",
            raw_description="Deploiement d'une solution RAG interne pour interroger la base documentaire RH et les CVs des collaborateurs.",
            status=TenderStatus.RESEARCHING,
            is_partial=False,
            deadline=datetime.now(timezone.utc) + timedelta(days=14)
        )

        db.add_all([tender1, tender2])
        db.commit()
        db.refresh(tender1)
        db.refresh(tender2)

        print("Insertion de la recherche prospect agentique (n8n)...")

        # 3. Prospect Research pour Tender 1
        research1 = ProspectResearch(
            tender_id=tender1.id,
            sector="Services Financiers & Banque",
            estimated_revenue="120M - 150M TND",
            key_partners=["Microsoft Azure", "SWIFT", "Oracle"],
            domain_requirements=["Conformite BCT", "Securite ISO 27001", "Support Multi-agent"],
            competitor_insights={
                "main_competitors": ["Fintech Softs", "Global IT Consulting"],
                "our_advantage": "Expertise prouvée en orchestration n8n et deploiement RAG sur mesure"
            },
            estimated_budget_range="180K - 250K TND",
            raw_research_notes="Prospect a fort potentiel. Transition numerique prioritaire pour Q4 2026."
        )
        db.add(research1)

        print("Liaison des matchs RAG (Qdrant)...")

        # 4. RAG Asset Matches pour Tender 1
        match1 = TenderAssetMatch(
            tender_id=tender1.id,
            asset_id=asset_cv1.id,
            relevance_score=0.94,
            match_reason="Profil parfait pour le pilotage de l'architecture IA RAG et les flux n8n."
        )
        match2 = TenderAssetMatch(
            tender_id=tender1.id,
            asset_id=asset_project1.id,
            relevance_score=0.89,
            match_reason="Projet similairement realise dans le secteur bancaire avec des exigences de securite identiques."
        )
        db.add_all([match1, match2])

        print("Insertion de la proposition commerciale generee...")

        # 5. Generated Proposal pour Tender 1
        proposal1 = Proposal(
            tender_id=tender1.id,
            version=1,
            content_json={
                "slides": [
                    {
                        "slide_number": 1,
                        "title": "Proposition Commerciale : Solution IA d'Intelligence RFP",
                        "subtitle": "Preparee par OliveSoft pour ATB Bank Group",
                        "type": "COVER"
                    },
                    {
                        "slide_number": 2,
                        "title": "Comprehension du Besoins & Enjeux",
                        "bullet_points": [
                            "Automatisations des processus de recherche de prospects",
                            "Extraction intelligente d'actifs via RAG hybride",
                            "Generation automatisee de deks de presentation au format OliveSoft"
                        ],
                        "type": "CONTENT"
                    },
                    {
                        "slide_number": 3,
                        "title": "Equipe Mobilisee & References OliveSoft",
                        "assigned_experts": ["Aymen Kassab (Lead AI)", "Sarra Ben Ali (Senior Fullstack)"],
                        "past_reference": "Projet Plateforme IA FinTech Banque Nationale",
                        "type": "TEAM_AND_REFS"
                    }
                ]
            },
            coverage_score_matrix={
                "technical_coverage": "95%",
                "functional_coverage": "90%",
                "compliance_score": "100%"
            },
            file_path_pptx="exports/proposals/ATB_Proposal_v1.pptx",
            file_path_pdf="exports/proposals/ATB_Proposal_v1.pdf"
        )
        db.add(proposal1)

        db.commit()
        print("Seed termine avec succes ! La base de donnees est prête pour la demo.")

    except Exception as e:
        print(f"Erreur durant le seed : {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()