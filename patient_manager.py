from exceptions import RecordNotFoundError, ValidationError
from utils import clean_text, normalize_id, valid_age, valid_id


def add_patient(patients, patient_id, name, age):
    patient_id = normalize_id(patient_id)
    name = clean_text(name)
    if not valid_id(patient_id, "P"):
        raise ValidationError("Patient ID must look like P101.")
    if patient_id in patients:
        raise ValidationError("Patient ID already exists.")
    if not name:
        raise ValidationError("Patient name cannot be empty.")
    if not valid_age(age):
        raise ValidationError("Age must be an integer from 0 to 120.")
    patients[patient_id] = {"name": name, "age": int(age)}
    return patients[patient_id]


def update_patient(patients, patient_id, name=None, age=None):
    patient_id = normalize_id(patient_id)
    if patient_id not in patients:
        raise RecordNotFoundError("Patient not found.")
    if name is not None and clean_text(name):
        patients[patient_id]["name"] = clean_text(name)
    if age is not None:
        if not valid_age(age):
            raise ValidationError("Age must be an integer from 0 to 120.")
        patients[patient_id]["age"] = int(age)
    return patients[patient_id]


def delete_patient(patients, patient_id, appointments=None):
    patient_id = normalize_id(patient_id)
    if patient_id not in patients:
        raise RecordNotFoundError("Patient not found.")
    if appointments and any(
        a["patient"] == patient_id and a["status"] != "cancelled"
        for a in appointments
    ):
        raise ValidationError("Cannot delete a patient with active appointments.")
    del patients[patient_id]
    return True


def search_patients(patients, query):
    query = clean_text(query).lower()
    return [
        (pid, data)
        for pid, data in patients.items()
        if query in pid.lower() or query in data["name"].lower()
    ]
