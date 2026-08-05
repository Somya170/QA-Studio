import random
from datetime import datetime, timedelta
import pandas as pd
from app.db.duckdb_client import db_client

CATEGORIES = [
    "CNC Lathe", "Robotic Arm", "Hydraulic Press", "3D Metal Printer",
    "Laser Cutter", "Injection Molding", "Conveyor Belt System", "AGV Transport"
]

LOCATIONS = [
    "Facility A - Bay 1", "Facility A - Bay 2", "Facility B - Assembly",
    "Facility B - Machining", "Facility C - Cleanroom", "Facility C - Packaging"
]

STATUSES = ["OPERATIONAL", "MAINTENANCE_DUE", "BREAKDOWN", "WARNING"]

OPERATORS = [
    "Rajesh Kumar", "Vikram Singh", "Amit Sharma", "Priya Patel", "Suresh Raina",
    "Sunita Verma", "Rohan Mehta", "Deepak Joshi", "Ananya Roy", "Karan Malhotra",
    "Neha Gupta", "Arjun Reddy", "Manish Tiwari", "Siddharth Rao", "Kavita Nair"
]

ISSUE_TYPES = [
    "Hydraulic Pressure Drop", "Spindle Bearing Vibration", "Motor Overheating",
    "Laser Optics Alignment", "Encoder Calibration Drift", "Gearbox Oil Contamination",
    "Pneumatic Valve Leak", "Emergency Stop Fault", "Control Board Reset Required"
]

PARTS = [
    "High-Temp O-Rings", "Spindle Bearing Unit", "Hydraulic Pump Filter",
    "Servo Motor Driver", "Optics Refine Lens", "Timing Belt Set", "Pressure Transducer"
]

TECHNICIAN_NOTES = [
    "Replaced worn bearing unit. Calibrated zero-point sensors. Machine tested for 2 hours.",
    "Flushed hydraulic fluid due to thermal degradation. Re-seated control module cables.",
    "Overheating caused by blocked intake vent. Cleaned radiator fins and replaced thermal paste.",
    "Operator reported unusual high frequency vibration during heavy cutting cycles. Realigned drive shaft.",
    "Routine 1000-hour inspection completed. All tolerances verified within 0.005mm spec.",
    "Encoder feedback error cleared. Refreshed firmware to v4.2.1.",
    "Emergency maintenance triggered by thermal sensor alarm. Coolant pump impeller replaced."
]

def generate_demo_dataset():
    """Generates 1,000 synthetic machines and 5,000 maintenance records."""
    random.seed(42)
    start_date = datetime(2024, 1, 1)

    # 1. Generate 1,000 Machines
    machines = []
    for i in range(1, 1001):
        m_id = f"MAC-{i:04d}"
        category = random.choice(CATEGORIES)
        location = random.choice(LOCATIONS)
        status = random.choices(STATUSES, weights=[70, 15, 5, 10])[0]
        health_score = round(random.uniform(95.0, 100.0) if status == "OPERATIONAL" else random.uniform(40.0, 85.0), 1)
        
        inst_days = random.randint(100, 900)
        installed_date = (start_date - timedelta(days=inst_days)).strftime("%Y-%m-%d")
        
        last_maint_days = random.randint(5, 90)
        last_maintenance = (datetime.now() - timedelta(days=last_maint_days)).strftime("%Y-%m-%d")
        
        next_maint_days = random.randint(-10, 30)
        next_scheduled = (datetime.now() + timedelta(days=next_maint_days)).strftime("%Y-%m-%d")
        
        total_downtime = round(random.uniform(5.0, 140.0), 1)
        operator = random.choice(OPERATORS)
        
        machines.append({
            "machine_id": m_id,
            "name": f"{category} #{i:04d}",
            "category": category,
            "location": location,
            "status": status,
            "health_score": health_score,
            "installed_date": installed_date,
            "last_maintenance": last_maintenance,
            "next_scheduled_maintenance": next_scheduled,
            "total_downtime_hours": total_downtime,
            "current_operator": operator
        })

    machines_df = pd.DataFrame(machines)
    db_client.load_df("machines", machines_df)

    # 2. Generate 5,000 Maintenance Logs
    logs = []
    for i in range(1, 5001):
        log_id = f"LOG-{i:05d}"
        m_id = f"MAC-{random.randint(1, 1000):04d}"
        log_days = random.randint(1, 700)
        log_date = (datetime.now() - timedelta(days=log_days)).strftime("%Y-%m-%d")
        issue = random.choice(ISSUE_TYPES)
        desc = f"Log record for {issue} on {m_id}."
        notes = random.choice(TECHNICIAN_NOTES)
        cost = round(random.uniform(150.0, 3500.0), 2)
        downtime = round(random.uniform(0.5, 24.0), 1)
        parts = random.choice(PARTS)
        
        logs.append({
            "log_id": log_id,
            "machine_id": m_id,
            "date": log_date,
            "issue_type": issue,
            "description": desc,
            "technician_notes": notes,
            "cost": cost,
            "downtime_hours": downtime,
            "status": "COMPLETED",
            "parts_replaced": parts
        })

    logs_df = pd.DataFrame(logs)
    db_client.load_df("maintenance_logs", logs_df)

    # 3. Generate 3,000 Operator Schedules
    schedules = []
    for i in range(1, 3001):
        sched_id = f"SCH-{i:05d}"
        op_name = random.choice(OPERATORS)
        op_id = f"OP-{OPERATORS.index(op_name)+101:03d}"
        m_id = f"MAC-{random.randint(1, 1000):04d}"
        shift = random.choice(["Morning (06:00-14:00)", "Afternoon (14:00-22:00)", "Night (22:00-06:00)"])
        sched_days = random.randint(1, 180)
        sched_date = (datetime.now() - timedelta(days=sched_days)).strftime("%Y-%m-%d")
        efficiency = round(random.uniform(82.0, 99.5), 1)
        
        schedules.append({
            "schedule_id": sched_id,
            "operator_id": op_id,
            "operator_name": op_name,
            "machine_id": m_id,
            "shift": shift,
            "date": sched_date,
            "efficiency_rating": efficiency,
            "notes": "Normal shift operations logged without incident."
        })

    schedules_df = pd.DataFrame(schedules)
    db_client.load_df("operator_schedules", schedules_df)

    return {
        "status": "SUCCESS",
        "machines_count": len(machines),
        "maintenance_logs_count": len(logs),
        "schedules_count": len(schedules)
    }

if __name__ == "__main__":
    result = generate_demo_dataset()
    print("Demo seed complete:", result)
