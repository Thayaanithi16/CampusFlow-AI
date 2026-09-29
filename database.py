import sqlite3
import os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "campusflow.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

@contextmanager
def get_db():
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Facilities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facilities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        building TEXT NOT NULL,
        floor INTEGER NOT NULL,
        capacity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'available', -- available, occupied, maintenance, disabled
        utilization_rate REAL DEFAULT 0.0,
        quality_rating REAL DEFAULT 4.5,
        is_accessible INTEGER DEFAULT 1,
        op_start_time TEXT DEFAULT '08:00',
        op_end_time TEXT DEFAULT '22:00',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Facility Equipment junction table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facility_equipment (
        facility_id TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        PRIMARY KEY (facility_id, equipment_name),
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE
    );
    """)

    # Bookings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        title TEXT NOT NULL,
        department TEXT NOT NULL,
        activity_type TEXT NOT NULL,
        date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        participants INTEGER NOT NULL,
        priority TEXT DEFAULT 'Medium',
        organizer TEXT NOT NULL,
        status TEXT DEFAULT 'confirmed', -- confirmed, cancelled, completed
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE
    );
    """)

    # Allocation Requests log
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allocation_requests (
        id TEXT PRIMARY KEY,
        department TEXT NOT NULL,
        activity TEXT NOT NULL,
        requested_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        participants INTEGER NOT NULL,
        facility_type TEXT NOT NULL,
        required_equipment TEXT, -- JSON array or comma separated
        priority TEXT DEFAULT 'Medium',
        building_preference TEXT,
        accessibility_required INTEGER DEFAULT 0,
        raw_prompt TEXT,
        allocated_facility_id TEXT,
        match_score REAL,
        status TEXT DEFAULT 'completed', -- completed, unfeasible, rejected
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (allocated_facility_id) REFERENCES facilities (id) ON DELETE SET NULL
    );
    """)

    # Allocation Results decision breakdown audit
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS allocation_results (
        id TEXT PRIMARY KEY,
        request_id TEXT NOT NULL,
        facility_id TEXT NOT NULL,
        total_score REAL NOT NULL,
        score_breakdown TEXT NOT NULL, -- JSON string
        evidence TEXT NOT NULL, -- JSON string
        rejected_facilities TEXT, -- JSON string
        reasons TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_id) REFERENCES allocation_requests (id) ON DELETE CASCADE,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE
    );
    """)

    # Conflicts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conflicts (
        id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        booking_id_1 TEXT NOT NULL,
        booking_id_2 TEXT NOT NULL,
        conflict_type TEXT NOT NULL, -- double_booking, capacity_exceeded, maintenance_overlap
        severity TEXT DEFAULT 'High', -- High, Medium, Low
        status TEXT DEFAULT 'active', -- active, resolved, ignored
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE,
        FOREIGN KEY (booking_id_1) REFERENCES bookings (id) ON DELETE CASCADE,
        FOREIGN KEY (booking_id_2) REFERENCES bookings (id) ON DELETE CASCADE
    );
    """)

    # Maintenance Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS maintenance (
        id TEXT PRIMARY KEY,
        facility_id TEXT NOT NULL,
        title TEXT NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        status TEXT DEFAULT 'scheduled', -- scheduled, in_progress, completed
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (facility_id) REFERENCES facilities (id) ON DELETE CASCADE
    );
    """)

    # Simulation State
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS simulation_state (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        current_simulated_date TEXT NOT NULL,
        current_simulated_time TEXT NOT NULL,
        is_simulating INTEGER DEFAULT 0,
        speed_multiplier INTEGER DEFAULT 1
    );
    """)

    # Optimization Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        weight_capacity REAL DEFAULT 0.25,
        weight_equipment REAL DEFAULT 0.20,
        weight_utilization REAL DEFAULT 0.20,
        weight_time REAL DEFAULT 0.15,
        weight_location REAL DEFAULT 0.10,
        weight_quality REAL DEFAULT 0.10,
        underutilized_threshold REAL DEFAULT 30.0,
        high_demand_threshold REAL DEFAULT 75.0,
        enable_gemini INTEGER DEFAULT 1
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
