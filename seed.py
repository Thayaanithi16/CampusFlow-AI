import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqlite3
import datetime
import random
import json
from backend.database import get_db_connection, init_db


BUILDINGS = [
    "Block A",
    "Block B",
    "Innovation Center",
    "Engineering Block",
    "Science Block",
    "Library Building",
    "Admin Block"
]

FACILITY_TYPES = [
    "classroom",
    "computer_lab",
    "science_lab",
    "seminar_hall",
    "auditorium",
    "meeting_room",
    "sports_facility"
]

EQUIPMENT_OPTIONS = [
    "projector",
    "wifi",
    "computers",
    "smart_board",
    "AC",
    "lab_equipment",
    "audio_system"
]

DEPARTMENTS = [
    "Computer Science & AI",
    "Electronics & Communication",
    "Mechanical Engineering",
    "Natural Sciences",
    "School of Management",
    "Data Science & Analytics",
    "Department of Mathematics"
]

def seed_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data cleanly for fresh re-seed
    cursor.execute("DELETE FROM conflicts;")
    cursor.execute("DELETE FROM allocation_results;")
    cursor.execute("DELETE FROM allocation_requests;")
    cursor.execute("DELETE FROM bookings;")
    cursor.execute("DELETE FROM facility_equipment;")
    cursor.execute("DELETE FROM maintenance;")
    cursor.execute("DELETE FROM facilities;")
    cursor.execute("DELETE FROM settings;")
    cursor.execute("DELETE FROM simulation_state;")

    # 1. Seed 48 Facilities
    facilities_data = []
    
    # Specific iconic facilities
    iconic = [
        ("FAC-B201", "AI Supercomputing Lab 1", "computer_lab", "Block B", 2, 75, "available", 88.5, 4.9, 1, ["computers", "projector", "wifi", "AC", "smart_board"]),
        ("FAC-B202", "Innovation Lab 3", "computer_lab", "Block B", 2, 100, "available", 58.0, 4.8, 1, ["computers", "projector", "wifi", "AC", "smart_board", "audio_system"]),
        ("FAC-B203", "Data Science Lab 2", "computer_lab", "Block B", 2, 80, "available", 96.0, 4.7, 1, ["computers", "projector", "wifi", "AC"]),
        ("FAC-A101", "Grand Seminar Hall A", "seminar_hall", "Block A", 1, 200, "available", 74.0, 4.8, 1, ["projector", "wifi", "audio_system", "AC", "smart_board"]),
        ("FAC-A102", "Lecture Theatre A-102", "classroom", "Block A", 1, 120, "available", 18.0, 4.2, 1, ["projector", "wifi"]),
        ("FAC-IC101", "Quantum & Robotics Lab", "science_lab", "Innovation Center", 1, 60, "available", 62.0, 4.9, 1, ["lab_equipment", "computers", "wifi", "AC", "projector"]),
        ("FAC-ADM501", "Main University Auditorium", "auditorium", "Admin Block", 5, 500, "available", 45.0, 4.9, 1, ["audio_system", "projector", "wifi", "AC"]),
        ("FAC-LIB301", "Executive Conference Room C", "meeting_room", "Library Building", 3, 25, "available", 24.0, 4.6, 1, ["wifi", "AC", "smart_board", "projector"]),
        ("FAC-ENG104", "Mechanical CAD Lab", "computer_lab", "Engineering Block", 1, 60, "maintenance", 35.0, 4.3, 1, ["computers", "projector", "wifi", "AC"])
    ]

    for f_id, name, f_type, building, floor, cap, status, util, qual, acc, eq in iconic:
        facilities_data.append((f_id, name, f_type, building, floor, cap, status, util, qual, acc, eq))

    # Generate remaining to reach 48 facilities
    counter = 10
    for b in BUILDINGS:
        for f_type in FACILITY_TYPES:
            if len(facilities_data) >= 48:
                break
            counter += 1
            f_id = f"FAC-{b[:3].upper()}{counter}"
            
            if f_type == "auditorium":
                cap = random.choice([300, 400, 500])
            elif f_type == "seminar_hall":
                cap = random.choice([150, 200, 250])
            elif f_type == "computer_lab":
                cap = random.choice([50, 60, 80, 100])
            elif f_type == "science_lab":
                cap = random.choice([40, 50, 60])
            elif f_type == "meeting_room":
                cap = random.choice([15, 20, 30])
            elif f_type == "sports_facility":
                cap = random.choice([100, 200, 300])
            else:
                cap = random.choice([40, 60, 80, 100])

            name = f"{b} {f_type.replace('_', ' ').title()} {counter}"
            util = round(random.uniform(15.0, 92.0), 1)
            qual = round(random.uniform(4.0, 5.0), 1)
            
            # Select random equipment
            eq = ["wifi", "projector"]
            if f_type in ["computer_lab"]: eq.append("computers")
            if f_type in ["science_lab"]: eq.append("lab_equipment")
            if f_type in ["seminar_hall", "auditorium"]: eq.extend(["audio_system", "AC"])
            if random.random() > 0.4: eq.append("smart_board")
            if random.random() > 0.3: eq.append("AC")

            facilities_data.append((f_id, name, f_type, b, random.randint(1, 4), cap, "available", util, qual, 1, list(set(eq))))

    # Insert facilities & equipment
    for f_id, name, f_type, building, floor, cap, status, util, qual, acc, eq in facilities_data:
        cursor.execute("""
            INSERT INTO facilities (id, name, type, building, floor, capacity, status, utilization_rate, quality_rating, is_accessible, op_start_time, op_end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '08:00', '22:00')
        """, (f_id, name, f_type, building, floor, cap, status, util, qual, acc))

        for item in eq:
            cursor.execute("""
                INSERT INTO facility_equipment (facility_id, equipment_name)
                VALUES (?, ?)
            """, (f_id, item))

    # 2. Seed Bookings (historical + upcoming)
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    
    booking_titles = [
        ("Advanced Deep Learning Workshop", "Computer Science & AI", "computer_lab", 70),
        ("Embedded Systems Architecture", "Electronics & Communication", "computer_lab", 55),
        ("Fluid Mechanics Lab Demonstration", "Mechanical Engineering", "science_lab", 40),
        ("Quantum Physics Research Symposium", "Natural Sciences", "seminar_hall", 120),
        ("Strategic Leadership Seminar", "School of Management", "seminar_hall", 90),
        ("Big Data Analytics Bootcamp", "Data Science & Analytics", "computer_lab", 65),
        ("Linear Algebra & Optimization Lecture", "Department of Mathematics", "classroom", 80),
        ("Campus AI Hackathon Keynote", "Computer Science & AI", "auditorium", 350),
        ("Robotics Team Weekly Review", "Mechanical Engineering", "meeting_room", 20),
        ("Inter-Department Badminton Tournament", "School of Management", "sports_facility", 150)
    ]

    booking_id_counter = 100
    for offset in range(-7, 8):
        b_date = (today + datetime.timedelta(days=offset)).strftime("%Y-%m-%d")
        
        # Add 8-12 bookings per day
        for _ in range(random.randint(6, 10)):
            booking_id_counter += 1
            title, dept, req_type, parts = random.choice(booking_titles)
            
            # Find matching facility
            cursor.execute("SELECT id FROM facilities WHERE type = ? ORDER BY RANDOM() LIMIT 1", (req_type,))
            row = cursor.fetchone()
            if not row:
                cursor.execute("SELECT id FROM facilities ORDER BY RANDOM() LIMIT 1")
                row = cursor.fetchone()
            fac_id = row["id"]

            start_hour = random.choice([8, 10, 11, 13, 14, 16, 18])
            duration = random.choice([1, 2, 3])
            end_hour = start_hour + duration
            
            s_time = f"{start_hour:02d}:00"
            e_time = f"{end_hour:02d}:00"

            cursor.execute("""
                INSERT INTO bookings (id, facility_id, title, department, activity_type, date, start_time, end_time, participants, priority, organizer, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Medium', 'Faculty Organizer', 'confirmed')
            """, (f"BK-{booking_id_counter}", fac_id, title, dept, "Academic", b_date, s_time, e_time, parts))

    # 3. Seed Specific Demo Conflicts for Conflict Center
    # Conflict 1: Double booking on Grand Seminar Hall A
    cursor.execute("""
        INSERT INTO bookings (id, facility_id, title, department, activity_type, date, start_time, end_time, participants, priority, organizer, status)
        VALUES ('BK-CONF-101', 'FAC-A101', 'CSE AI Guest Lecture', 'Computer Science & AI', 'Lecture', ?, '10:00', '12:00', 140, 'High', 'Dr. Smith', 'confirmed')
    """, (tomorrow.strftime("%Y-%m-%d"),))

    cursor.execute("""
        INSERT INTO bookings (id, facility_id, title, department, activity_type, date, start_time, end_time, participants, priority, organizer, status)
        VALUES ('BK-CONF-102', 'FAC-A101', 'ECE Wireless Systems Exam', 'Electronics & Communication', 'Exam', ?, '11:00', '13:00', 130, 'High', 'Prof. Davis', 'confirmed')
    """, (tomorrow.strftime("%Y-%m-%d"),))

    cursor.execute("""
        INSERT INTO conflicts (id, facility_id, booking_id_1, booking_id_2, conflict_type, severity, status, details)
        VALUES ('C-101', 'FAC-A101', 'BK-CONF-101', 'BK-CONF-102', 'Schedule Overlap', 'High', 'active', 'Time overlap detected between 11:00 AM and 12:00 PM on Grand Seminar Hall A.')
    """)

    # Conflict 2: Innovation Lab 3 Overlap
    cursor.execute("""
        INSERT INTO bookings (id, facility_id, title, department, activity_type, date, start_time, end_time, participants, priority, organizer, status)
        VALUES ('BK-CONF-201', 'FAC-B202', 'Data Science Workshop', 'Data Science & Analytics', 'Workshop', ?, '14:00', '16:00', 80, 'Medium', 'Dr. Alan', 'confirmed')
    """, (tomorrow.strftime("%Y-%m-%d"),))

    cursor.execute("""
        INSERT INTO bookings (id, facility_id, title, department, activity_type, date, start_time, end_time, participants, priority, organizer, status)
        VALUES ('BK-CONF-202', 'FAC-B202', 'Web Dev Hackathon Prep', 'Computer Science & AI', 'Hackathon', ?, '15:00', '17:00', 70, 'Medium', 'Student Council', 'confirmed')
    """, (tomorrow.strftime("%Y-%m-%d"),))

    cursor.execute("""
        INSERT INTO conflicts (id, facility_id, booking_id_1, booking_id_2, conflict_type, severity, status, details)
        VALUES ('C-102', 'FAC-B202', 'BK-CONF-201', 'BK-CONF-202', 'Schedule Overlap', 'Medium', 'active', 'Overlap detected between 15:00 and 16:00 on Innovation Lab 3.')
    """)

    # 4. Seed Maintenance Records
    cursor.execute("""
        INSERT INTO maintenance (id, facility_id, title, start_date, end_date, status, notes)
        VALUES ('M-101', 'FAC-ENG104', 'HVAC & CAD Workstation Maintenance', ?, ?, 'in_progress', 'Upgrading GPU drivers and air filtration system')
    """, ((today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), (today + datetime.timedelta(days=3)).strftime("%Y-%m-%d")))

    # 5. Seed Simulation State & Default Settings
    cursor.execute("""
        INSERT INTO simulation_state (id, current_simulated_date, current_simulated_time, is_simulating, speed_multiplier)
        VALUES (1, ?, '10:00', 0, 1)
    """, (today.strftime("%Y-%m-%d"),))

    cursor.execute("""
        INSERT INTO settings (id, weight_capacity, weight_equipment, weight_utilization, weight_time, weight_location, weight_quality, underutilized_threshold, high_demand_threshold, enable_gemini)
        VALUES (1, 0.25, 0.20, 0.20, 0.15, 0.10, 0.10, 30.0, 75.0, 1)
    """)

    conn.commit()
    conn.close()
    print("CampusFlow AI database seeded successfully with 48 facilities, bookings, and demo conflicts.")

if __name__ == "__main__":
    seed_database()
