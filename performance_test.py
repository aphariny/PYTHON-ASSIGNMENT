import time
import random
import statistics
from datetime import date, timedelta

from appointment_manager import check_appointment_conflict
from patient_manager import search_patients


def make_dataset(size):
    patients = {
        f"P{i:04d}": {"name": f"Patient {i}", "age": 20 + (i % 60)}
        for i in range(1, size + 1)
    }
    doctors = [f"D{i:03d}" for i in range(1, 11)]
    appointments = []
    target = str(date.today() + timedelta(days=1))

    # Generate non-conflicting appointments across doctors/times.
    for i in range(1, size + 1):
        doctor = doctors[i % len(doctors)]
        hour = 8 + ((i // len(doctors)) % 10)
        minute = (i // (len(doctors) * 10)) * 10
        if minute >= 60:
            minute = minute % 60
        appointments.append({
            "appointment_id": f"A{i:05d}",
            "patient": f"P{i:04d}",
            "doctor": doctor,
            "date": target,
            "time": f"{hour:02d}:{minute:02d}",
            "status": "booked",
        })
    return patients, appointments, target


def timed(fn, repeats=5):
    values = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn()
        values.append((time.perf_counter() - start) * 1000)
    return statistics.mean(values)


def run():
    print("PERFORMANCE COMPARISON")
    print("Times are local prototype measurements in milliseconds; run again on your machine for reproducibility.")
    print(f"{'Dataset':<12}{'Patient search':>18}{'Conflict check':>18}")
    for size in (100, 500, 1000):
        patients, appointments, target = make_dataset(size)
        patient_ms = timed(lambda: search_patients(patients, str(size // 2)))
        conflict_ms = timed(
            lambda: check_appointment_conflict(
                appointments, "D005", target, "12:00"
            )
        )
        print(f"{size:<12}{patient_ms:>18.4f}{conflict_ms:>18.4f}")


if __name__ == "__main__":
    run()
