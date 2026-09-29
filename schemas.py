from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Facility Schemas
class FacilityBase(BaseModel):
    id: str
    name: str
    type: str # classroom, computer_lab, science_lab, seminar_hall, auditorium, meeting_room, sports_facility
    building: str
    floor: int
    capacity: int
    status: str = "available" # available, occupied, maintenance, disabled
    utilization_rate: float = 0.0
    quality_rating: float = 4.5
    is_accessible: bool = True
    op_start_time: str = "08:00"
    op_end_time: str = "22:00"
    equipment: List[str] = []

class FacilityCreate(FacilityBase):
    pass

class FacilityUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    quality_rating: Optional[float] = None
    is_accessible: Optional[bool] = None
    equipment: Optional[List[str]] = None

# Allocation Request Schemas
class ParseRequest(BaseModel):
    prompt: str

class ExtractedRequirements(BaseModel):
    department: str = "General"
    activity: str = "Campus Activity"
    date: str = "" # YYYY-MM-DD or 'tomorrow'/'today'
    start_time: str = "10:00"
    end_time: str = "12:00"
    participants: int = 30
    facility_type: str = "classroom"
    required_equipment: List[str] = []
    priority: str = "Medium"
    building_preference: Optional[str] = None
    accessibility_required: bool = False
    raw_prompt: Optional[str] = None
    parser_used: str = "Deterministic Parser"
    is_ai: bool = False

class AllocationQuery(BaseModel):
    department: str
    activity: str
    date: str
    start_time: str
    end_time: str
    participants: int
    facility_type: str
    required_equipment: List[str] = []
    priority: str = "Medium"
    building_preference: Optional[str] = None
    accessibility_required: bool = False
    preferred_facility_id: Optional[str] = None

class ScoreBreakdown(BaseModel):
    capacity_score: float
    equipment_score: float
    utilization_score: float
    time_score: float
    location_score: float
    quality_score: float

class EvidenceItem(BaseModel):
    label: str
    value: str
    passed: bool
    detail: str

class AlternativeFacility(BaseModel):
    facility: FacilityBase
    match_score: float
    capacity_diff: str
    diff_reason: str
    score_breakdown: ScoreBreakdown
    evidence: List[EvidenceItem]

class AllocationRecommendation(BaseModel):
    request_summary: Dict[str, Any]
    recommended_facility: Optional[FacilityBase] = None
    match_score: float = 0.0
    is_feasible: bool = True
    unfeasible_reason: Optional[str] = None
    score_breakdown: Optional[ScoreBreakdown] = None
    evidence: List[EvidenceItem] = []
    why_selected: List[str] = []
    alternatives: List[AlternativeFacility] = []
    rejected_facilities: List[Dict[str, Any]] = [] # [{id, name, reason}]
    suggested_time_slots: List[Dict[str, str]] = []
    suggested_types: List[str] = []

class ConfirmAllocationRequest(BaseModel):
    department: str
    activity: str
    date: str
    start_time: str
    end_time: str
    participants: int
    priority: str = "Medium"
    organizer: str = "Faculty Admin"
    facility_id: str
    match_score: float
    recommendation_details: Optional[Dict[str, Any]] = None

class BookingSchema(BaseModel):
    id: str
    facility_id: str
    facility_name: Optional[str] = None
    building: Optional[str] = None
    title: str
    department: str
    activity_type: str
    date: str
    start_time: str
    end_time: str
    participants: int
    priority: str
    organizer: str
    status: str
    created_at: str

class ConflictSchema(BaseModel):
    id: str
    facility_id: str
    facility_name: str
    building: str
    booking_1: BookingSchema
    booking_2: BookingSchema
    conflict_type: str
    severity: str
    status: str
    details: str
    created_at: str

class SettingsSchema(BaseModel):
    weight_capacity: float = 0.25
    weight_equipment: float = 0.20
    weight_utilization: float = 0.20
    weight_time: float = 0.15
    weight_location: float = 0.10
    weight_quality: float = 0.10
    underutilized_threshold: float = 30.0
    high_demand_threshold: float = 75.0
    enable_gemini: bool = True

class SimulationStep(BaseModel):
    advance_hours: int = 2
