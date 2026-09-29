# CampusFlow AI
### Intelligent Resource Allocation System for Campus Facilities

> **Elevator Pitch:**  
> CampusFlow AI transforms campus facility booking into intelligent resource allocation by combining natural-language understanding, hard-constraint validation, and weighted optimization to assign suitable facilities, prevent conflicts, recommend alternatives, and improve campus utilization.

---

## 1. Problem Statement & Executive Summary
Traditional university room booking systems operate as dumb CRUD forms. They suffer from:
1. **Double bookings & scheduling collisions** during peak examination and conference periods.
2. **Resource waste & capacity mismatch**, assigning a 300-seat auditorium to a 15-person study meeting.
3. **Severe utilization imbalances**, leaving some modern smart rooms bottlenecked at 95%+ utilization while other lecture halls sit idle under 20%.
4. **Dead ends**: When a requested space is unavailable, legacy systems simply state "Unavailable" with zero alternative suggestions.

**CampusFlow AI** re-architects facility scheduling from passive record-keeping into an active, **two-stage optimization engine** paired with **explainable AI decision audit trails**.

---

## 2. Key Capabilities
- **Dual-Mode Request Intake**:
  - *Mode A: Structured Parameter Form* (Department, activity, participants, facility type, equipment, priority, accessibility).
  - *Mode B: Natural-Language Understanding* powered by Gemini AI with deterministic fallback.
- **Stage 1 Hard Constraint Filtering**:
  - Availability & time overlap rule: `requested_start < existing_end AND requested_end > existing_start`.
  - Capacity adequacy: `facility.capacity >= requested.participants`.
  - Facility type category match.
  - Mandatory equipment presence.
  - Active maintenance status exclusion.
  - ADA wheelchair accessibility compliance.
  - Operational hours boundary verification.
- **Stage 2 Weighted Suitability Scoring (0–100)**:
  - Capacity Fit (25% default)
  - Equipment Match (20% default)
  - Utilization Balance (20% default)
  - Time Suitability (15% default)
  - Location Preference (10% default)
  - Facility Quality Rating (10% default)
- **Explainable AI Decisions**:
  - "Why this facility?" breakdown with score weighting and hard constraint evidence audit.
- **Feasible Alternatives Engine**:
  - When a preferred facility is booked or unfeasible, automatically surfaces top 3 ranked alternatives with seat delta and location comparison.
- **Active Conflict Resolution Center**:
  - Detects schedule collisions, double-booking attempts, and offers 1-click reassign or cancellation workflows.
- **Empirical Campus Utilization Analytics**:
  - Calculated directly from SQLite: `Utilization = (Booked Hours / Available Hours) * 100`.
  - Underutilized (<30%) and high-demand (>75%) classification.
  - CSV export for administrative records.
- **Judge Demo Mode**:
  - 3 pre-configured judging scenarios (Optimal Smart Allocation, Conflict Overlap Prevention, Alternative Discovery) plus a 1-click "Run Full Demo" sequential runner.

---

## 3. Technology Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Recharts
- **Backend**: Python 3.11, FastAPI, Pydantic, Uvicorn
- **Database**: SQLite (48 seeded campus facilities, 150+ historical & upcoming bookings, active conflicts, maintenance logs)
- **AI/NLP**: Google GenAI SDK (`gemini-2.5-flash`) with automatic regex/rule-based deterministic fallback

---

## 4. Database Schema
- `facilities`: `id`, `name`, `type`, `building`, `floor`, `capacity`, `status`, `utilization_rate`, `quality_rating`, `is_accessible`, `op_start_time`, `op_end_time`.
- `facility_equipment`: `facility_id`, `equipment_name`.
- `bookings`: `id`, `facility_id`, `title`, `department`, `activity_type`, `date`, `start_time`, `end_time`, `participants`, `priority`, `organizer`, `status`.
- `conflicts`: `id`, `facility_id`, `booking_id_1`, `booking_id_2`, `conflict_type`, `severity`, `status`, `details`.
- `allocation_requests`: `id`, `department`, `activity`, `requested_date`, `start_time`, `end_time`, `participants`, `facility_type`, `allocated_facility_id`, `match_score`, `status`.
- `maintenance`: `id`, `facility_id`, `title`, `start_date`, `end_date`, `status`, `notes`.
- `settings`: Configurable scoring weights and utilization thresholds.
- `simulation_state`: Simulated time and date tracker.

---

## 5. API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard` | Top KPIs, active conflicts, recent decisions, AI insights |
| `GET` | `/api/facilities` | List all facilities with filters (type, building, status, capacity) |
| `GET` | `/api/facilities/{id}` | Detailed facility record with upcoming calendar schedule |
| `POST` | `/api/allocation/parse` | Parse natural language prompt into structured parameters |
| `POST` | `/api/allocation/recommend` | Two-stage optimization pipeline returning best match & alternatives |
| `POST` | `/api/allocation/confirm` | Confirm booking and commit record into SQLite |
| `GET` | `/api/bookings` | List schedule bookings filtered by date and department |
| `GET` | `/api/conflicts` | List active scheduling conflicts |
| `POST` | `/api/conflicts/{id}/resolve` | Resolve conflict (cancel colliding session or mark resolved) |
| `GET` | `/api/analytics/utilization` | Utilization stats, category counts, demand distributions |
| `GET` | `/api/analytics/export/csv` | Download utilization report CSV |
| `GET` | `/api/history` | Audit log of allocation requests and match scores |
| `GET` | `/api/settings` | Read multi-criteria scoring weights |
| `PUT` | `/api/settings` | Update scoring weights and thresholds |
| `POST` | `/api/simulation/advance` | Advance simulated campus time (+2 hours) |

---

## 6. How to Run Locally

### Quick Start
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the unified application server
python app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

The root script `app.py` automatically initializes the SQLite database, seeds 48 campus facilities across 7 buildings, loads demo bookings and conflicts, and serves the web command center.
