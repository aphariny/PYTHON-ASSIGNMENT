from exceptions import RecordNotFoundError, ValidationError
from utils import clean_text, normalize_id, valid_id


def add_doctor(doctors, doctor_id, name, specialization, availability):
    doctor_id = normalize_id(doctor_id)
    name = clean_text(name)
    specialization = clean_text(specialization)
    availability = clean_text(availability)

    if not valid_id(doctor_id, "D"):
        raise ValidationError("Doctor ID must look like D101.")
    if doctor_id in doctors:
        raise ValidationError("Doctor ID already exists.")
    if not name or not specialization or not availability:
        raise ValidationError("Name, specialization and availability are required.")

    doctors[doctor_id] = {
        "name": name,
        "specialization": specialization,
        "availability": availability,
    }
    return doctors[doctor_id]


def update_doctor(doctors, doctor_id, name=None, specialization=None, availability=None):
    doctor_id = normalize_id(doctor_id)
    if doctor_id not in doctors:
        raise RecordNotFoundError("Doctor not found.")

    if name is not None and clean_text(name):
        doctors[doctor_id]["name"] = clean_text(name)
    if specialization is not None and clean_text(specialization):
        doctors[doctor_id]["specialization"] = clean_text(specialization)
    if availability is not None and clean_text(availability):
        doctors[doctor_id]["availability"] = clean_text(availability)
    return doctors[doctor_id]


def delete_doctor(doctors, doctor_id, appointments=None):
    doctor_id = normalize_id(doctor_id)
    if doctor_id not in doctors:
        raise RecordNotFoundError("Doctor not found.")
    if appointments and any(
        a["doctor"] == doctor_id and a["status"] != "cancelled"
        for a in appointments
    ):
        raise ValidationError("Cannot delete a doctor with active appointments.")
    del doctors[doctor_id]
    return True


def search_doctors(doctors, specialization):
    query = clean_text(specialization).lower()
    return [
        (did, data)
        for did, data in doctors.items()
        if query in data["specialization"].lower()
    ]


def get_specializations(doctors):
    return {data["specialization"] for data in doctors.values()}
