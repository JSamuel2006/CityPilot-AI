"""
Pydantic v2 schemas for request / response validation.
Every response schema matches its corresponding SQLAlchemy model exactly.
"""

from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

from database.models import (
    ComplaintCategory, Severity, ComplaintStatus,
    ResourceType, ResourceStatus,
)


# ═══════════════════════════════════════════════════════════════════
# API Envelope
# ═══════════════════════════════════════════════════════════════════

class APIResponse(BaseModel):
    """Standard JSON envelope for every endpoint."""
    success: bool = True
    message: str = ""
    data: Any = None
    timestamp: datetime = datetime.utcnow()
    execution_time_ms: float = 0.0


# ═══════════════════════════════════════════════════════════════════
# Complaint schemas
# ═══════════════════════════════════════════════════════════════════

class ComplaintBase(BaseModel):
    category: ComplaintCategory
    description: str
    ward: str
    severity: Severity
    lat: float
    lng: float


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintResponse(ComplaintBase):
    id: int
    status: ComplaintStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_department: Optional[str] = None
    resolution_hours: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════
# Weather schemas
# ═══════════════════════════════════════════════════════════════════

class WeatherResponse(BaseModel):
    id: int
    recorded_at: datetime
    temperature_c: float
    humidity_pct: float
    precipitation_mm: float
    wind_speed_kmh: float
    condition: str
    aqi: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════
# Resource schemas
# ═══════════════════════════════════════════════════════════════════

class ResourceResponse(BaseModel):
    id: int
    type: ResourceType
    name: str
    status: ResourceStatus
    ward: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    last_deployed: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════
# Department schemas
# ═══════════════════════════════════════════════════════════════════

class DepartmentResponse(BaseModel):
    id: int
    name: str
    head: Optional[str] = None
    contact_email: Optional[str] = None
    total_staff: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════
# Knowledge Document schemas
# ═══════════════════════════════════════════════════════════════════

class KnowledgeDocumentResponse(BaseModel):
    id: int
    original_filename: str
    stored_filename: str
    file_type: str
    file_size_bytes: Optional[int] = None
    file_path: Optional[str] = None
    upload_date: datetime
    status: str
    is_embedded: bool

    model_config = ConfigDict(from_attributes=True)


# ═══════════════════════════════════════════════════════════════════
# Analyze schemas
# ═══════════════════════════════════════════════════════════════════

class AnalyzeRequest(BaseModel):
    query: str


class AnalyzeResponse(BaseModel):
    risk_score: int
    confidence: str
    evidence: List[str]
    recommendation: str
    affected_areas: List[str]
    priority: str
    resources_needed: List[str]
    estimated_cost: str
    estimated_savings: str
    executive_summary: str
    sources: Optional[List[str]] = []



# ═══════════════════════════════════════════════════════════════════
# Report schemas
# ═══════════════════════════════════════════════════════════════════

class ReportRequest(BaseModel):
    type: str


# ═══════════════════════════════════════════════════════════════════
# Settings schemas
# ═══════════════════════════════════════════════════════════════════

class SystemStatusResponse(BaseModel):
    api_status: str
    database_type: str
    database_status: str
    database_version: str
    connection_pool_size: int
    ai_engine: str
    app_version: str
