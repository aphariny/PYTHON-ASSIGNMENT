from datetime import date
from analytics import daily_statistics, workload_report


def patient_appointment_report(patients, doctors, appointments, patient_id):
    patient_id = patient_id.upper().strip()
    patient = patients.get(patient_id)
    if not patient:
        return "Patient not found."

    lines = [
        "PATIENT APPOINTMENT REPORT",
        "=" * 28,
        f"Patient ID : {patient_id}",
        f"Name       : {patient['name']}",
        f"Age        : {patient['age']}",
        "",
        "Appointments:",
    ]
    records = [a for a in appointments if a["patient"] == patient_id]
    if not records:
        lines.append("No appointments found.")
    else:
        for a in sorted(records, key=lambda x: (x["date"], x["time"])):
            doctor_name = doctors.get(a["doctor"], {}).get("name", a["doctor"])
            lines.append(
                f"{a['appointment_id']} | {a['date']} {a['time']} | "
                f"{doctor_name} ({a['doctor']}) | {a['status']}"
            )
    return "\n".join(lines)


def doctor_schedule_report(doctors, appointments, doctor_id, target_date=None):
    doctor_id = doctor_id.upper().strip()
    doctor = doctors.get(doctor_id)
    if not doctor:
        return "Doctor not found."

    lines = [
        "DOCTOR DAILY SCHEDULE",
        "=" * 23,
        f"Doctor       : {doctor['name']}",
        f"Doctor ID    : {doctor_id}",
        f"Specialty    : {doctor['specialization']}",
        f"Availability : {doctor['availability']}",
        f"Date         : {target_date or 'All dates'}",
        "",
    ]
    records = [
        a for a in appointments
        if a["doctor"] == doctor_id
        and (target_date is None or a["date"] == str(target_date))
    ]
    records.sort(key=lambda x: (x["date"], x["time"]))
    if not records:
        lines.append("No appointments found.")
    else:
        for a in records:
            lines.append(
                f"{a['date']} {a['time']} | {a['appointment_id']} | "
                f"Patient {a['patient']} | {a['status']}"
            )
    return "\n".join(lines)


def daily_statistics_report(appointments, target_date):
    stats = daily_statistics(appointments, target_date)
    return (
        f"DAILY STATISTICS - {target_date}\n"
        f"{'=' * 32}\n"
        f"Total appointments : {stats['appointments']}\n"
        f"Booked             : {stats['booked']}\n"
        f"Completed          : {stats['completed']}\n"
        f"Cancelled          : {stats['cancellations']}\n"
    )


def full_daily_report(patients, doctors, appointments, target_date=None):
    target_date = target_date or str(date.today())
    return (
        daily_statistics_report(appointments, target_date)
        + "\nDOCTOR WORKLOAD\n"
        + "=" * 16
        + "\n"
        + "\n".join(
            f"{r['doctor_id']} | {r['doctor_name']} | "
            f"{r['specialization']} | {r['appointments']} appointments"
            for r in workload_report(appointments, doctors)
        )
    )
