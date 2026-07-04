"""
Analyze service — retrieves real data from PostgreSQL and passes it to AIService.
"""

from sqlalchemy.orm import Session

from repositories.complaint_repository import ComplaintRepository
from repositories.weather_repository import WeatherRepository
from repositories.resource_repository import ResourceRepository
from repositories.knowledge_repository import KnowledgeRepository
from ai.services import AIService
from database.schemas import AnalyzeResponse


class AnalyzeService:
    """Builds context from live data and delegates to AIService."""

    @staticmethod
    def analyze_query(db: Session, query: str) -> AnalyzeResponse:
        # ── Gather real data ────────────────────────────────────────
        # Recent complaints
        recent_complaints = ComplaintRepository.get_recent(db, limit=20)
        complaint_summaries = [
            {
                "id": c.id,
                "category": c.category.value,
                "severity": c.severity.value,
                "status": c.status.value,
                "ward": c.ward,
                "description": c.description[:120],
            }
            for c in recent_complaints
        ]

        # Latest weather
        latest_weather = WeatherRepository.get_latest(db)
        weather_context = None
        if latest_weather:
            weather_context = {
                "temperature_c": latest_weather.temperature_c,
                "humidity_pct": latest_weather.humidity_pct,
                "precipitation_mm": latest_weather.precipitation_mm,
                "condition": latest_weather.condition,
                "aqi": latest_weather.aqi,
            }

        # Resource summary
        resource_util = ResourceRepository.get_utilization(db)

        # Affected wards
        affected_wards = ComplaintRepository.get_affected_wards(db, limit=5)

        # Knowledge documents count
        knowledge_count = KnowledgeRepository.get_count(db)

        # ── RAG Integration: Retrieve top 5 relevant chunks ─────────
        from services.rag_service import RAGService
        relevant_chunks = RAGService.retrieve_relevant_chunks(db, query, limit=5)
        
        # Format the retrieved context for the prompt
        retrieved_text = ""
        unique_sources = set()
        for idx, chunk in enumerate(relevant_chunks):
            retrieved_text += f"\n[Chunk {idx+1} from {chunk['source']}]: {chunk['content']}\n"
            unique_sources.add(chunk['source'])
            
        sources_list = sorted(list(unique_sources))

        # ── Build structured context ────────────────────────────────
        context = {
            "query": query,
            "complaints": complaint_summaries,
            "weather": weather_context,
            "resources": resource_util,
            "affected_wards": affected_wards,
            "knowledge_documents_count": knowledge_count,
            "total_active_complaints": ComplaintRepository.get_active_count(db),
            "total_critical": ComplaintRepository.get_critical_count(db),
            "retrieved_context": retrieved_text,
            "sources": sources_list,
        }

        # ── Pass to AI Service ──────────────────────────────────────
        result = AIService.analyze(context)

        # Inject sources and append to executive summary for UI rendering
        result["sources"] = sources_list
        if sources_list:
            sources_str = ", ".join(sources_list)
            result["executive_summary"] = (
                result.get("executive_summary", "") + 
                f" (Source documents analyzed: {sources_str})"
            )

        # ── Store Chat History ──────────────────────────────────────
        import json
        from database.models import ChatHistory
        try:
            chat_record = ChatHistory(
                query=query,
                response=json.dumps(result),
            )
            db.add(chat_record)
            db.commit()
        except Exception as e:
            db.rollback()
            # Suppress/log silently to not affect user request flow
            import logging
            logging.getLogger("citypilot.analyze").error(f"Failed to store chat history: {e}")

        return AnalyzeResponse(**result)
