from collections import deque
from exceptions import RecordNotFoundError


def build_daily_queue(appointments, target_date):
    """Return patient IDs in appointment time order, excluding cancelled visits."""
    day_appointments = [
        a for a in appointments
        if a["date"] == str(target_date) and a["status"] != "cancelled"
    ]
    day_appointments.sort(key=lambda a: a["time"])
    return [a["patient"] for a in day_appointments]


def enqueue(queue, patient_id):
    queue.append(patient_id)
    return list(queue)


def dequeue(queue):
    if not queue:
        raise RecordNotFoundError("Queue is empty.")
    return queue.popleft()


def queue_position(queue, patient_id):
    try:
        return list(queue).index(patient_id) + 1
    except ValueError:
        return -1
