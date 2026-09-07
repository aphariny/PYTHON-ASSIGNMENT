from datetime import date
from exceptions import DuplicateAppointmentError, RecordNotFoundError, ValidationError
from utils import clean_text, format_slot, normalize_id, parse_date, parse_time


def _validate_refs(patients, doctors, patient_id, doctor_id):
    patient_id = normalize_id(patient_id)
    doctor_id = normalize_id(doctor_id)
    if patient_id not in patients:
        raise RecordNotFoundError("Patient not found.")
    if doctor_id not in doctors:
        raise RecordNotFoundError("Doctor not found.")
    return patient_id, doctor_id


def check_appointment_conflict(appointments, doctor_id, appointment_date, appointment_time, exclude_id=None):
    """Return True when an active appointment occupies the same doctor/date/time tuple."""
    doctor_id = normalize_id(doctor_id)
    for appointment in appointments:
        if appointment["status"] == "cancelled":
            continue
        if exclude_id and appointment["appointment_id"] == exclude_id:
            continue
        if (
            appointment["doctor"] == doctor_id
            and appointment["date"] == str(appointment_date)
            and appointment["time"] == clean_text(appointment_time)
        ):
            return True
    return False


def book_appointment(
    patients, doctors, appointments, appointment_id,
    patient_id, doctor_id, appointment_date, appointment_time
):
    patient_id, doctor_id = _validate_refs(patients, doctors, patient_id, doctor_id)
    appointment_id = normalize_id(appointment_id)
    if not appointment_id:
        raise ValidationError("Appointment ID cannot be empty.")
    if any(a["appointment_id"] == appointment_id for a in appointments):
        raise ValidationError("Appointment ID already exists.")

    parsed_date = parse_date(appointment_date)
    parsed_time = parse_time(appointment_time)
    if parsed_date < date.today():
        raise ValidationError("Appointment date cannot be in the past.")

    if check_appointment_conflict(appointments, doctor_id, parsed_date, parsed_time.strftime("%H:%M")):
        raise DuplicateAppointmentError("Conflict detected: doctor is already booked for this time slot.")

    # Tuple required by the assignment: immutable scheduling information.
    slot = format_slot(doctor_id, parsed_date, parsed_time.strftime("%H:%M"))
    appointment = {
        "appointment_id": appointment_id,
        "patient": patient_id,
        "doctor": doctor_id,
        "date": str(parsed_date),
        "time": parsed_time.strftime("%H:%M"),
        "slot": slot,
        "status": "booked",
    }
    appointments.append(appointment)
    return appointment


def reschedule_appointment(
    patients, doctors, appointments, appointment_id, new_date, new_time
):
    appointment_id = normalize_id(appointment_id)
    target = next((a for a in appointments if a["appointment_id"] == appointment_id), None)
    if target is None:
        raise RecordNotFoundError("Appointment not found.")
    if target["status"] == "cancelled":
        raise ValidationError("Cancelled appointments cannot be rescheduled.")

    parsed_date = parse_date(new_date)
    parsed_time = parse_time(new_time)
    if parsed_date < date.today():
        raise ValidationError("Appointment date cannot be in the past.")

    new_time = parsed_time.strftime("%H:%M")
    if check_appointment_conflict(
        appointments, target["doctor"], parsed_date, new_time, exclude_id=appointment_id
    ):
        raise DuplicateAppointmentError("Conflict detected: new time slot is already occupied.")

    target["date"] = str(parsed_date)
    target["time"] = new_time
    target["slot"] = format_slot(target["doctor"], parsed_date, new_time)
    return target


def cancel_appointment(appointments, appointment_id):
    appointment_id = normalize_id(appointment_id)
    for appointment in appointments:
        if appointment["appointment_id"] == appointment_id:
            if appointment["status"] == "cancelled":
                raise ValidationError("Appointment is already cancelled.")
            appointment["status"] = "cancelled"
            return appointment
    raise RecordNotFoundError("Appointment not found.")


def complete_appointment(appointments, appointment_id):
    appointment_id = normalize_id(appointment_id)
    for appointment in appointments:
        if appointment["appointment_id"] == appointment_id:
            if appointment["status"] == "cancelled":
                raise ValidationError("Cancelled appointment cannot be completed.")
            appointment["status"] = "completed"
            return appointment
    raise RecordNotFoundError("Appointment not found.")


def search_appointments(appointments, query):
    query = clean_text(query).lower()
    return [
        a for a in appointments
        if query in a["appointment_id"].lower()
        or query in a["patient"].lower()
        or query in a["doctor"].lower()
        or query in a["date"].lower()
        or query in a["status"].lower()
    ]


def get_unique_dates(appointments):
    return {a["date"] for a in appointments}


def get_appointments_for_date(appointments, target_date):
    return [a for a in appointments if a["date"] == str(target_date)]
