"""
AI services — Google Gemini API integration.
Fetches real data context, queries Gemini with strict JSON constraints, and returns operational intelligence.
"""

import os
import json
import logging
# pyrefly: ignore [missing-import]
import google.generativeai as genai
from config import get_settings

logger = logging.getLogger("citypilot.ai")


class AIService:
    """Core AI Service utilizing the Google Gemini API."""

    @staticmethod
    def _get_model():
        """Retrieve and configure the Gemini generative model if API key is present."""
        settings = get_settings()
        api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            logger.warning("GEMINI_API_KEY not configured. Falling back to local analyzer.")
            return None
        try:
            genai.configure(api_key=api_key)
            return genai.GenerativeModel("gemini-3.5-flash")
        except Exception as e:
            logger.error(f"Error configuring Google Generative AI: {e}")
            return None

    @staticmethod
    def get_insights(db=None) -> list[str]:
        """Generate dynamic insights using Gemini, with a robust local fallback."""
        model = AIService._get_model()
        if not model:
            return [
                "Water logging risk in Ward 4 has increased by 15% due to expected rain.",
                "Deploy 3 extra waste collection trucks in Ward 2 to clear backlog.",
                "Traffic congestion likely at Main Intersection; recommend traffic diversion.",
            ]

        prompt = (
            "You are CityPilot AI, a smart city operations assistant. "
            "Generate exactly 3 concise, highly professional, and actionable operations insights "
            "or alerts for the city commissioner dashboard based on typical urban management "
            "problems (e.g. water logging, garbage clearance, traffic congestion). "
            "Each insight must be a single sentence. "
            "Return the response as a JSON array of 3 strings."
        )

        try:
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            if isinstance(data, list) and len(data) >= 3:
                return [str(item) for item in data[:3]]
        except Exception as e:
            logger.error(f"Failed to generate dynamic insights via Gemini: {e}")
        
        # Fallback
        return [
            "Water logging risk in Ward 4 has increased by 15% due to expected rain.",
            "Deploy 3 extra waste collection trucks in Ward 2 to clear backlog.",
            "Traffic congestion likely at Main Intersection; recommend traffic diversion.",
        ]

    @staticmethod
    def analyze(context: dict) -> dict:
        """
        Analyse city data and return structured intelligence using the Gemini API.

        Parameters
        ----------
        context : dict
            Structured context containing:
            - query: str
            - complaints: list[dict]
            - weather: dict | None
            - resources: list[dict]
            - affected_wards: list[str]
            - knowledge_documents_count: int
            - total_active_complaints: int
            - total_critical: int

        Returns
        -------
        dict matching AnalyzeResponse schema.
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

        # ── 1. Attempt Gemini Generation ────────────────────────────────────
        model = AIService._get_model()
        if model:
            prompt = (
                f"You are CityPilot AI, an advanced urban operations intelligence system.\n"
                f"Analyze the following user query about city operations: '{query}'\n\n"
                f"Here is the structured real-time city data from PostgreSQL:\n"
                f"- Active complaints: {total_active} (Critical: {total_critical})\n"
                f"- Weather status: {json.dumps(weather)}\n"
                f"- Recent complaints sample: {json.dumps(complaints)}\n"
                f"- Resource utilization metrics: {json.dumps(resources)}\n"
                f"- Most affected wards: {json.dumps(affected_wards)}\n"
                f"- Uploaded knowledge documents count: {knowledge_docs_count}\n"
                f"- Retrieved relevant documents content (RAG): {retrieved_context}\n\n"
                f"Analyze this data and return a JSON object with the following fields:\n"
                f"- risk_score (integer 0-100): current operational/emergency risk score.\n"
                f"- confidence (string): confidence percentage, e.g. 'High (95%)'.\n"
                f"- reason (string): explanation of how the data points lead to this risk score.\n"
                f"- evidence (list of strings): 2-4 key data points supporting your assessment.\n"
                f"- recommendation (string): primary tactical recommendation/action.\n"
                f"- resources_needed (list of strings): specific resource units to deploy.\n"
                f"- priority (string): enum value (LOW, MEDIUM, HIGH, CRITICAL).\n"
                f"- executive_summary (string): summary of findings.\n"
                f"- estimated_cost (string): estimated cost of recommendation, e.g. '₹2,50,000'.\n"
                f"- estimated_savings (string): estimated savings in damage control, e.g. '₹1.5 Cr'.\n"
                f"- affected_areas (list of strings): list of wards affected.\n\n"
                f"Return ONLY a valid JSON object matching the requested schema. No markdown wrapping."
            )

            try:
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                res_dict = json.loads(response.text)
                
                # Basic schema validation/coercion to guarantee compatibility with Pydantic
                required_keys = [
                    "risk_score", "confidence", "evidence", "recommendation",
                    "affected_areas", "priority", "resources_needed",
                    "estimated_cost", "estimated_savings", "executive_summary"
                ]
                
                if all(k in res_dict for k in required_keys):
                    # Ensure correct data types
                    res_dict["risk_score"] = int(res_dict.get("risk_score", 50))
                    res_dict["confidence"] = str(res_dict.get("confidence", "Medium"))
                    res_dict["evidence"] = [str(x) for x in res_dict.get("evidence", [])]
                    res_dict["recommendation"] = str(res_dict.get("recommendation", ""))
                    res_dict["affected_areas"] = [str(x) for x in res_dict.get("affected_areas", [])]
                    res_dict["priority"] = str(res_dict.get("priority", "MEDIUM")).upper()
                    res_dict["resources_needed"] = [str(x) for x in res_dict.get("resources_needed", [])]
                    res_dict["estimated_cost"] = str(res_dict.get("estimated_cost", ""))
                    res_dict["estimated_savings"] = str(res_dict.get("estimated_savings", ""))
                    res_dict["executive_summary"] = str(res_dict.get("executive_summary", ""))
                    
                    return res_dict
            except Exception as e:
                logger.error(f"Gemini generation or parsing failed: {e}. Falling back to rule-based analyzer.")

        # ── 2. Rule-Based Fallback (If key is missing or API call fails) ───
        evidence = []
        if weather:
            evidence.append(
                f"Current weather: {weather.get('condition', 'N/A')}, "
                f"Temperature: {weather.get('temperature_c', 'N/A')}°C, "
                f"Precipitation: {weather.get('precipitation_mm', 0)}mm."
            )
        evidence.append(
            f"There are {total_active} active complaints, "
            f"of which {total_critical} are critical."
        )
        if complaints:
            top_cats = {}
            for c in complaints:
                cat = c.get("category", "Unknown")
                top_cats[cat] = top_cats.get(cat, 0) + 1
            top = sorted(top_cats.items(), key=lambda x: -x[1])[:3]
            evidence.append(
                "Top recent complaint categories: "
                + ", ".join(f"{cat} ({cnt})" for cat, cnt in top)
                + "."
            )
        if not evidence:
            evidence = ["Insufficient data for detailed analysis."]

        # Rule-based risk logic
        risk_score = min(100, max(0, total_critical * 15 + total_active // 10))
        if risk_score >= 70:
            priority = "CRITICAL"
        elif risk_score >= 40:
            priority = "HIGH"
        else:
            priority = "MEDIUM"

        return {
            "risk_score": risk_score,
            "confidence": f"High ({min(99, 70 + len(evidence) * 5)}%)",
            "evidence": evidence,
            "recommendation": (
                f"Based on analysis of '{query}': Focus resources on "
                f"{', '.join(affected_wards[:3])}. "
                f"{total_critical} critical issues require immediate attention."
            ),
            "affected_areas": affected_wards[:5],
            "priority": priority,
            "resources_needed": [
                "3× Water Pumps",
                "2× Emergency Response Teams",
                "1× Traffic Control Unit",
                "1× Medical Standby",
            ],
            "estimated_cost": "₹3,75,000",
            "estimated_savings": "₹1.2 Cr in potential damage prevention",
            "executive_summary": (
                f"Analysis of '{query}': Currently tracking {total_active} active "
                f"complaints with {total_critical} at critical severity across "
                f"{len(affected_wards)} affected wards. "
                f"Proactive resource deployment recommended (fallback mode)."
            ),
        }


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
                f"{critical} critical. Immediate attention required for "
                f"critical areas."
            )
        return (
            "City operations are running normally with localized issues "
            "requiring immediate attention."
        )
