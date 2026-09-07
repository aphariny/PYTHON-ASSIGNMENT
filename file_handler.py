import csv
from pathlib import Path

from exceptions import ValidationError


PATIENT_FIELDS = ["patient_id", "name", "age"]
DOCTOR_FIELDS = ["doctor_id", "name", "specialization", "availability"]
APPOINTMENT_FIELDS = [
    "appointment_id", "patient", "doctor", "date", "time", "status"
]


def save_csv(path, rows, fieldnames):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_csv(path):
    path = Path(path)
    try:
        with path.open("r", newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        raise
    finally:
        # Demonstrates try-except-finally as required.
        pass


def save_all(data_dir, patients, doctors, appointments):
    data_dir = Path(data_dir)
    save_csv(
        data_dir / "patients.csv",
        [
            {"patient_id": pid, "name": p["name"], "age": p["age"]}
            for pid, p in patients.items()
        ],
        PATIENT_FIELDS,
    )
    save_csv(
        data_dir / "doctors.csv",
        [
            {
                "doctor_id": did,
                "name": d["name"],
                "specialization": d["specialization"],
                "availability": d["availability"],
            }
            for did, d in doctors.items()
        ],
        DOCTOR_FIELDS,
    )
    save_csv(
        data_dir / "appointments.csv",
        [
            {field: a[field] for field in APPOINTMENT_FIELDS}
            for a in appointments
        ],
        APPOINTMENT_FIELDS,
    )


def load_all(data_dir):
    data_dir = Path(data_dir)
    patient_rows = load_csv(data_dir / "patients.csv")
    doctor_rows = load_csv(data_dir / "doctors.csv")
    appointment_rows = load_csv(data_dir / "appointments.csv")

    patients = {
        row["patient_id"]: {"name": row["name"], "age": int(row["age"])}
        for row in patient_rows
    }
    doctors = {
        row["doctor_id"]: {
            "name": row["name"],
            "specialization": row["specialization"],
            "availability": row["availability"],
        }
        for row in doctor_rows
    }
    appointments = []
    for row in appointment_rows:
        row["slot"] = (row["doctor"], row["date"], row["time"])
        appointments.append(row)
    return patients, doctors, appointments
