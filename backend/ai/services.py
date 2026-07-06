"""
AI services — Google Gemini API integration (google-genai >= 1.0 SDK).
Fetches real data context, queries Gemini with strict JSON constraints, and returns operational intelligence.
"""

import os
import json
import logging
import time
from google import genai
from google.genai import types
from config import get_settings

logger = logging.getLogger("citypilot.ai")


class AIService:
    """Core AI Service utilizing the Google Gemini API (new google-genai SDK)."""

    @staticmethod
    def _get_client():
        """Return a configured Gemini client if API key is present, else None."""
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to local analyzer.")
            return None
        try:
            return genai.Client(api_key=api_key)
        except Exception as e:
            logger.error(f"Error configuring Google Gemini client: {e}")
            return None

    @staticmethod
    def _generate(client, prompt: str, json_mode: bool = True) -> str | None:
        """Call Gemini with retry logic. Returns raw text or None on failure."""
        config = types.GenerateContentConfig(
            response_mime_type="application/json" if json_mode else "text/plain"
        )
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=config,
                )
                return response.text
            except Exception as e:
                logger.warning(f"Gemini generation attempt {attempt + 1} failed: {e}")
                time.sleep(1.5)
        return None

    @staticmethod
    def get_insights(db=None) -> list[str]:
        """Generate dynamic insights using Gemini, or a real database-driven fallback."""
        client = AIService._get_client()

        # Gather live context from database
        active_cnt = 0
        critical_cnt = 0
        weather_cond = "Clear"
        temp_c = 25.0
        rain_mm = 0.0
        top_ward = "Ward 2"

        if db:
            try:
                from repositories.complaint_repository import ComplaintRepository
                from repositories.weather_repository import WeatherRepository
                active_cnt = ComplaintRepository.get_active_count(db)
                critical_cnt = ComplaintRepository.get_critical_count(db)
                latest_w = WeatherRepository.get_latest(db)
                if latest_w:
                    weather_cond = latest_w.condition
                    temp_c = latest_w.temperature_c
                    rain_mm = latest_w.precipitation_mm
                wards = ComplaintRepository.get_affected_wards(db, limit=1)
                if wards:
                    top_ward = wards[0]
            except Exception as e:
                logger.error(f"Error gathering DB context for insights: {e}")

        if client:
            prompt = (
                "You are CityPilot AI, a smart city operations assistant. "
                "Generate exactly 3 concise, highly professional, and actionable operations insights "
                "or alerts for the city commissioner dashboard based on the following real-time city data:\n"
                f"- Active complaints: {active_cnt}\n"
                f"- Critical emergencies: {critical_cnt}\n"
                f"- Most affected area: {top_ward}\n"
                f"- Weather: {weather_cond}, {temp_c}°C, {rain_mm}mm rain\n\n"
                "Each insight must be a single sentence. "
                "Return the response as a JSON array of 3 strings."
            )
            raw = AIService._generate(client, prompt, json_mode=True)
            if raw:
                try:
                    data = json.loads(raw)
                    if isinstance(data, list) and len(data) >= 3:
                        return [str(item) for item in data[:3]]
                except Exception as e:
                    logger.warning(f"Failed to parse Gemini insights JSON: {e}")

        # Dynamic live fallback
        fallback_insights = []
        if critical_cnt > 0:
            fallback_insights.append(
                f"Immediate intervention required: {critical_cnt} critical emergencies active, "
                f"primarily concentrated in {top_ward}."
            )
        else:
            fallback_insights.append(
                "Operational status stable: 0 critical complaints currently open across all wards."
            )

        if rain_mm > 10.0:
            fallback_insights.append(
                f"Precipitation level at {rain_mm}mm increases waterlogging risks in "
                f"low-lying sectors of {top_ward}."
            )
        else:
            fallback_insights.append(
                f"Current weather condition is {weather_cond} at {temp_c}°C with no active storm warnings."
            )

        fallback_insights.append(
            f"Platform tracking {active_cnt} total active citizen complaints. "
            "Resource deployment is currently active."
        )
        return fallback_insights

    @staticmethod
    def analyze(context: dict) -> dict:
        """
        Analyse city data and return structured intelligence using the Gemini API.
        Includes retry logic and a real database-driven fallback.
        """
        query = context.get("query", "")
        affected_wards = context.get("affected_wards", ["Ward 2", "Ward 4"])
        total_active = context.get("total_active_complaints", 0)
        total_critical = context.get("total_critical", 0)
        weather = context.get("weather") or {}
        complaints = context.get("complaints", [])
        resources = context.get("resources", [])
        knowledge_docs_count = context.get("knowledge_documents_count", 0)
        retrieved_context = context.get("retrieved_context", "")
        severity_dist = context.get("severity_distribution", [])
        status_dist = context.get("status_distribution", [])
        historical_trend = context.get("complaint_trend_7_days", [])
        category_trend = context.get("category_trend_6_months", [])
        weekly_comp = context.get("weekly_comparison", [])
        predicted_hotspots_input = context.get("predicted_hotspots", [])

        # ── 1. Attempt Gemini Generation ─────────────────────────────
        client = AIService._get_client()
        if client:
            prompt = (
                f"You are CityPilot AI, an advanced urban operations intelligence system.\n"
                f"Analyze the following user query about city operations: '{query}'\n\n"
                f"Here is the structured real-time city data from PostgreSQL:\n"
                f"- Active complaints: {total_active} (Critical: {total_critical})\n"
                f"- Weather status: {json.dumps(weather)}\n"
                f"- Recent complaints sample: {json.dumps(complaints)}\n"
                f"- Severity distribution: {json.dumps(severity_dist)}\n"
                f"- Status distribution: {json.dumps(status_dist)}\n"
                f"- Historical complaint trends (last 7 days): {json.dumps(historical_trend)}\n"
                f"- Category trend (6 months): {json.dumps(category_trend)}\n"
                f"- Weekly comparison (this week vs last week): {json.dumps(weekly_comp)}\n"
                f"- Resource utilization metrics: {json.dumps(resources)}\n"
                f"- Most affected wards: {json.dumps(affected_wards)}\n"
                f"- Predicted hotspots (spatial calculation): {json.dumps(predicted_hotspots_input)}\n"
                f"- Uploaded knowledge documents count: {knowledge_docs_count}\n"
                f"- Retrieved relevant documents content (RAG): {retrieved_context}\n\n"
                f"Analyze this data and return a JSON object with the following fields:\n"
                f"- executive_summary (string): professional summary of current operational state.\n"
                f"- risk_score (integer 0-100): current operational/emergency risk score.\n"
                f"- confidence (integer 0-100): confidence percentage of this analysis.\n"
                f"- priority_level (string): LOW, MEDIUM, HIGH, or CRITICAL.\n"
                f"- recommendations (list of strings): 3-5 specific operational recommendations.\n"
                f"- predicted_hotspots (list): specific hotspot predictions with ward and reason.\n"
                f"- affected_wards (list of strings): wards impacted.\n"
                f"- required_resources (list of strings): resources needed to resolve current issues.\n"
                f"- estimated_resolution_time (string): estimated resolution time.\n"
                f"- sources (list of strings): list of source filenames from RAG context.\n\n"
                f"Return ONLY a valid JSON object matching the requested schema. No markdown wrapping."
            )

            raw = AIService._generate(client, prompt, json_mode=True)
            if raw:
                try:
                    res_dict = json.loads(raw)
                    required_keys = [
                        "executive_summary", "risk_score", "confidence", "priority_level",
                        "recommendations", "predicted_hotspots", "affected_wards",
                        "required_resources", "estimated_resolution_time", "sources"
                    ]
                    if all(k in res_dict for k in required_keys):
                        # Safely parse integer values
                        try:
                            res_dict["risk_score"] = int(res_dict.get("risk_score", 50))
                        except (ValueError, TypeError):
                            res_dict["risk_score"] = 50
                            
                        try:
                            res_dict["confidence"] = int(res_dict.get("confidence", 85))
                        except (ValueError, TypeError):
                            res_dict["confidence"] = 85
                            
                        res_dict["priority_level"] = str(res_dict.get("priority_level", "MEDIUM")).upper()
                        
                        # Helper to safely sanitize lists
                        def clean_list(val):
                            if isinstance(val, list):
                                return [str(x) for x in val if x is not None]
                            elif val:
                                return [str(val)]
                            return []

                        res_dict["recommendations"] = clean_list(res_dict.get("recommendations"))
                        
                        hotspots = res_dict.get("predicted_hotspots")
                        if isinstance(hotspots, list):
                            res_dict["predicted_hotspots"] = hotspots
                        elif hotspots:
                            res_dict["predicted_hotspots"] = [hotspots]
                        else:
                            res_dict["predicted_hotspots"] = []

                        res_dict["affected_wards"] = clean_list(res_dict.get("affected_wards"))
                        res_dict["required_resources"] = clean_list(res_dict.get("required_resources"))
                        res_dict["estimated_resolution_time"] = str(res_dict.get("estimated_resolution_time", ""))
                        res_dict["sources"] = clean_list(res_dict.get("sources"))

                        # Populate legacy fields for backward compatibility
                        res_dict["evidence"] = res_dict["recommendations"][:3]
                        res_dict["recommendation"] = res_dict["recommendations"][0] if res_dict["recommendations"] else ""
                        res_dict["affected_areas"] = res_dict["affected_wards"]
                        res_dict["priority"] = res_dict["priority_level"]
                        res_dict["resources_needed"] = res_dict["required_resources"]
                        res_dict["estimated_cost"] = "₹2,50,000"
                        res_dict["estimated_savings"] = "₹1.5 Cr in damages"
                        return res_dict
                except Exception as e:
                    logger.warning(f"Failed to parse Gemini analyze JSON: {e}")

        # ── 2. PostgreSQL-driven fallback ──────────────────────────
        risk_score = min(100, max(0, total_critical * 15 + total_active // 10))
        if risk_score >= 70:
            priority = "CRITICAL"
        elif risk_score >= 40:
            priority = "HIGH"
        else:
            priority = "MEDIUM"

        rec_list = [
            f"Address the {total_critical} active critical complaints in {', '.join(affected_wards[:2])} immediately.",
            "Deploy emergency water pumps to flood zones if precipitation continues.",
            "Alert municipal waste services to prioritize garbage build-ups in active complaints."
        ]

        hotspots_list = []
        for ph in predicted_hotspots_input[:3]:
            hotspots_list.append(
                f"{ph.get('ward', 'Unknown Ward')} (Risk Score: {ph.get('risk_score', 0)}% - {ph.get('reason', 'N/A')})"
            )
        if not hotspots_list:
            hotspots_list = [f"{w} (Elevated Risk)" for w in affected_wards[:2]]

        fallback_res = {
            "executive_summary": (
                f"Live PostgreSQL analysis for: '{query}'. Currently monitoring {total_active} active "
                f"complaints, with {total_critical} marked as critical. Wards with highest activity: "
                f"{', '.join(affected_wards)}. Weather: {weather.get('condition', 'N/A')} "
                f"at {weather.get('temperature_c', 'N/A')}°C. (Database fallback mode)."
            ),
            "risk_score": risk_score,
            "confidence": 75,
            "priority_level": priority,
            "recommendations": rec_list,
            "predicted_hotspots": hotspots_list,
            "affected_wards": affected_wards,
            "required_resources": [
                "2x Water Pumps for flood mitigation",
                "1x Emergency Response Unit",
                "3x Municipal Cleaning Crews"
            ],
            "estimated_resolution_time": "12 to 24 hours",
            "sources": context.get("sources", []),
            # Backward-compat fields
            "evidence": [
                f"Active complaints count: {total_active}",
                f"Critical severity complaints count: {total_critical}",
                f"Current weather precip: {weather.get('precipitation_mm', 0)}mm"
            ],
            "recommendation": rec_list[0],
            "affected_areas": affected_wards,
            "priority": priority,
            "resources_needed": ["2× Water Pumps", "1× Emergency Response Team"],
            "estimated_cost": "₹1,80,000",
            "estimated_savings": "₹85 L in damage control"
        }
        return fallback_res


class RAGService:
    """RAG service — placeholder for knowledge-base retrieval."""

    @staticmethod
    def process_query(query: str, documents: list | None = None) -> str:
        """Process a query against knowledge documents."""
        doc_count = len(documents) if documents else 0
        return (
            f"Based on {doc_count} uploaded documents and historical data, "
            f"this requires immediate attention."
        )


class PredictionService:
    """Prediction service — placeholder for ML-based risk prediction."""

    @staticmethod
    def get_risk_heatmap(ward_data: list[dict] | None = None) -> list[dict]:
        """Return risk heatmap data."""
        if ward_data:
            return ward_data
        return [
            {"ward": "Ward 1", "risk": "Green", "score": 20},
            {"ward": "Ward 2", "risk": "Red", "score": 85},
            {"ward": "Ward 3", "risk": "Orange", "score": 60},
            {"ward": "Ward 4", "risk": "Yellow", "score": 45},
        ]


class ReportService:
    """Report service — placeholder for report generation."""

    @staticmethod
    def generate_executive_summary(context: dict | None = None) -> str:
        """Generate an executive summary."""
        if context:
            active = context.get("total_active_complaints", 0)
            critical = context.get("total_critical", 0)
            return (
                f"City operations: {active} active complaints, "
                f"{critical} critical. Immediate attention required for critical areas."
            )
        return "City operations are running normally with localized issues requiring immediate attention."
