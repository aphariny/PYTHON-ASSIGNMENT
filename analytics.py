from collections import Counter


def daily_statistics(appointments, target_date):
    day = [a for a in appointments if a["date"] == str(target_date)]
    return {
        "appointments": len(day),
        "completed": sum(a["status"] == "completed" for a in day),
        "cancellations": sum(a["status"] == "cancelled" for a in day),
        "booked": sum(a["status"] == "booked" for a in day),
    }


def doctor_workload(appointments, doctor_id=None):
    active = [a for a in appointments if a["status"] != "cancelled"]
    if doctor_id:
        return sum(a["doctor"] == doctor_id for a in active)
    return dict(Counter(a["doctor"] for a in active))


def appointment_status_counts(appointments):
    return dict(Counter(a["status"] for a in appointments))


def workload_report(appointments, doctors):
    counts = doctor_workload(appointments)
    return [
        {
            "doctor_id": doctor_id,
            "doctor_name": doctor["name"],
            "specialization": doctor["specialization"],
            "appointments": counts.get(doctor_id, 0),
        }
        for doctor_id, doctor in doctors.items()
    ]
