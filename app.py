
import streamlit as st
from pathlib import Path
from datetime import date
from collections import deque
import pandas as pd

from patient_manager import add_patient, update_patient, delete_patient, search_patients
from doctor_manager import add_doctor, update_doctor, delete_doctor, search_doctors
from appointment_manager import book_appointment, reschedule_appointment, cancel_appointment, complete_appointment, search_appointments, get_appointments_for_date
from queue_manager import build_daily_queue, queue_position
from analytics import daily_statistics, doctor_workload
from file_handler import save_all, load_all

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(page_title="Healthcare Management System", page_icon="🏥", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:1.5rem}
.hero{padding:25px;border-radius:18px;background:linear-gradient(135deg,#0f766e,#2563eb);color:white;margin-bottom:18px}
.hero h1{margin:0}.hero p{margin:6px 0 0}
[data-testid="stMetric"]{border:1px solid #e5e7eb;padding:12px;border-radius:12px}
</style>
""", unsafe_allow_html=True)

def load_data():
    try:
        return load_all(DATA_DIR)
    except Exception:
        return {}, {}, []

if "patients" not in st.session_state:
    st.session_state.patients, st.session_state.doctors, st.session_state.appointments = load_data()

patients = st.session_state.patients
doctors = st.session_state.doctors
appointments = st.session_state.appointments

def save():
    save_all(DATA_DIR, patients, doctors, appointments)

def appt_df(rows=None):
    rows = appointments if rows is None else rows
    return pd.DataFrame([{
        "Appointment ID":a["appointment_id"], "Patient":a["patient"],
        "Doctor":a["doctor"], "Date":a["date"], "Time":a["time"],
        "Status":a["status"].title()
    } for a in rows])

st.markdown("""
<div class="hero">
<h1>🏥 Healthcare Appointment & Patient Service Management</h1>
<p>Complete clinic management web application built with Python and Streamlit</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Select module", [
        "🏠 Dashboard","👤 Patients","👨‍⚕️ Doctors","📅 Appointments","🚶 Queue","📊 Reports"
    ])
    st.divider()
    if st.button("💾 Save All Data", use_container_width=True):
        try:
            save(); st.success("Saved to CSV files.")
        except Exception as e: st.error(str(e))
    if st.button("🔄 Reload Data", use_container_width=True):
        st.session_state.patients, st.session_state.doctors, st.session_state.appointments = load_data()
        st.rerun()

if page == "🏠 Dashboard":
    st.subheader("Dashboard")
    a,b,c,d = st.columns(4)
    a.metric("Patients",len(patients)); b.metric("Doctors",len(doctors))
    c.metric("Appointments",len(appointments))
    d.metric("Active",sum(x["status"]!="cancelled" for x in appointments))
    st.divider()
    st.markdown("### All Appointments")
    rows = sorted(appointments,key=lambda x:(x["date"],x["time"]))
    if rows: st.dataframe(appt_df(rows),use_container_width=True,hide_index=True)
    else: st.info("No appointments.")

elif page == "👤 Patients":
    st.subheader("Patient Management")
    t1,t2,t3,t4=st.tabs(["Add","Update","Delete","Search & View"])
    with t1:
        with st.form("addp"):
            c1,c2,c3=st.columns(3)
            pid=c1.text_input("Patient ID",placeholder="P111")
            name=c2.text_input("Name")
            age=c3.number_input("Age",0,120,18)
            if st.form_submit_button("Add Patient",type="primary"):
                try:
                    add_patient(patients,pid,name,age); save(); st.success("Patient added."); st.rerun()
                except Exception as e: st.error(str(e))
    with t2:
        if patients:
            pid=st.selectbox("Patient",list(patients))
            p=patients[pid]
            with st.form("editp"):
                name=st.text_input("Name",value=p["name"])
                age=st.number_input("Age",0,120,int(p["age"]))
                if st.form_submit_button("Update Patient"):
                    try:
                        update_patient(patients,pid,name,age); save(); st.success("Updated."); st.rerun()
                    except Exception as e: st.error(str(e))
        else: st.info("No patients.")
    with t3:
        if patients:
            pid=st.selectbox("Patient to delete",list(patients),key="delp")
            st.warning("Patients with active appointments cannot be deleted.")
            if st.button("Delete Patient",type="primary"):
                try:
                    delete_patient(patients,pid,appointments); save(); st.success("Deleted."); st.rerun()
                except Exception as e: st.error(str(e))
        else: st.info("No patients.")
    with t4:
        q=st.text_input("Search patient")
        rows=search_patients(patients,q) if q else list(patients.items())
        st.dataframe(pd.DataFrame([{"Patient ID":k,"Name":v["name"],"Age":v["age"]} for k,v in rows]),
                     use_container_width=True,hide_index=True)

elif page == "👨‍⚕️ Doctors":
    st.subheader("Doctor Management")
    t1,t2,t3,t4=st.tabs(["Add","Update","Delete","Search & View"])
    with t1:
        with st.form("addd"):
            c1,c2=st.columns(2)
            did=c1.text_input("Doctor ID",placeholder="D105")
            name=c2.text_input("Doctor Name")
            spec=c1.text_input("Specialization")
            availability=c2.text_input("Availability",placeholder="Mon-Fri 09:00-17:00")
            if st.form_submit_button("Add Doctor",type="primary"):
                try:
                    add_doctor(doctors,did,name,spec,availability); save(); st.success("Doctor added."); st.rerun()
                except Exception as e: st.error(str(e))
    with t2:
        if doctors:
            did=st.selectbox("Doctor",list(doctors))
            x=doctors[did]
            with st.form("editd"):
                name=st.text_input("Name",value=x["name"])
                spec=st.text_input("Specialization",value=x["specialization"])
                av=st.text_input("Availability",value=x["availability"])
                if st.form_submit_button("Update Doctor"):
                    try:
                        update_doctor(doctors,did,name,spec,av); save(); st.success("Updated."); st.rerun()
                    except Exception as e: st.error(str(e))
        else: st.info("No doctors.")
    with t3:
        if doctors:
            did=st.selectbox("Doctor to delete",list(doctors),key="deld")
            st.warning("Doctors with active appointments cannot be deleted.")
            if st.button("Delete Doctor",type="primary"):
                try:
                    delete_doctor(doctors,did,appointments); save(); st.success("Deleted."); st.rerun()
                except Exception as e: st.error(str(e))
        else: st.info("No doctors.")
    with t4:
        q=st.text_input("Search specialization")
        rows=search_doctors(doctors,q) if q else list(doctors.items())
        st.dataframe(pd.DataFrame([{"Doctor ID":k,"Name":v["name"],"Specialization":v["specialization"],"Availability":v["availability"]} for k,v in rows]),
                     use_container_width=True,hide_index=True)

elif page == "📅 Appointments":
    st.subheader("Appointment Management")
    t1,t2,t3,t4,t5=st.tabs(["Book","Reschedule","Cancel","Complete","Search & View"])
    with t1:
        if patients and doctors:
            with st.form("book"):
                c1,c2,c3=st.columns(3)
                aid=c1.text_input("Appointment ID",placeholder="A101")
                pid=c2.selectbox("Patient",list(patients))
                did=c3.selectbox("Doctor",list(doctors))
                dt=c1.date_input("Date",min_value=date.today())
                tm=c2.time_input("Time")
                if st.form_submit_button("Book Appointment",type="primary"):
                    try:
                        book_appointment(patients,doctors,appointments,aid,pid,did,dt,tm); save()
                        st.success("Appointment booked successfully."); st.rerun()
                    except Exception as e: st.error(str(e))
        else: st.warning("Add a patient and doctor first.")
    with t2:
        active=[x for x in appointments if x["status"]!="cancelled"]
        if active:
            aid=st.selectbox("Appointment",[x["appointment_id"] for x in active],key="resa")
            nd=st.date_input("New date",min_value=date.today())
            nt=st.time_input("New time")
            if st.button("Reschedule",type="primary"):
                try:
                    reschedule_appointment(patients,doctors,appointments,aid,nd,nt); save(); st.success("Rescheduled."); st.rerun()
                except Exception as e: st.error(str(e))
        else: st.info("No active appointments.")
    with t3:
        active=[x for x in appointments if x["status"]!="cancelled"]
        if active:
            aid=st.selectbox("Appointment",[x["appointment_id"] for x in active],key="cana")
            if st.button("Cancel Appointment",type="primary"):
                try:
                    cancel_appointment(appointments,aid); save(); st.success("Cancelled."); st.rerun()
                except Exception as e: st.error(str(e))
        else: st.info("No active appointments.")
    with t4:
        booked=[x for x in appointments if x["status"]=="booked"]
        if booked:
            aid=st.selectbox("Appointment",[x["appointment_id"] for x in booked],key="coma")
            if st.button("Mark Completed",type="primary"):
                try:
                    complete_appointment(appointments,aid); save(); st.success("Completed."); st.rerun()
                except Exception as e: st.error(str(e))
        else: st.info("No booked appointments.")
    with t5:
        q=st.text_input("Search by appointment ID, patient, doctor, date or status")
        rows=search_appointments(appointments,q) if q else appointments
        st.dataframe(appt_df(rows),use_container_width=True,hide_index=True)

elif page == "🚶 Queue":
    st.subheader("Daily Patient Queue")
    dt=st.date_input("Select date",value=date.today())
    q=deque(build_daily_queue(appointments,dt))
    day=get_appointments_for_date(appointments,dt)
    a,b=st.columns(2); a.metric("Queue Size",len(q)); b.metric("Appointments",len(day))
    if q:
        st.dataframe(pd.DataFrame([
            {"Position":i,"Patient ID":pid,"Patient":patients.get(pid,{}).get("name","Unknown")}
            for i,pid in enumerate(q,1)
        ]),use_container_width=True,hide_index=True)
        pid=st.selectbox("Check patient position",list(q))
        st.info(f"{pid} is at queue position {queue_position(q,pid)}.")
    else: st.info("No active appointments in this queue.")
    st.markdown("### Day's Appointments")
    st.dataframe(appt_df(day),use_container_width=True,hide_index=True)

else:
    st.subheader("📊 Analysis & Reports")
    dt=st.date_input("Report date",value=date.today())

    # daily_statistics() returns: appointments, completed, cancellations and booked.
    s=daily_statistics(appointments,dt)

    # doctor_workload() expects the appointment list and optionally one doctor ID.
    # Filter to the selected day first so the report is date-specific.
    day_appointments=get_appointments_for_date(appointments,dt)
    w=doctor_workload(day_appointments)

    total=s["appointments"]
    booked=s["booked"]
    completed=s["completed"]
    cancelled=s["cancellations"]
    active=booked

    a,b,c,d,e=st.columns(5)
    a.metric("Total",total)
    b.metric("Booked",booked)
    c.metric("Completed",completed)
    d.metric("Cancelled",cancelled)
    e.metric("Active",active)

    left,right=st.columns(2)
    with left:
        st.markdown("### Doctor Workload")
        if w:
            df=pd.DataFrame([
                {"Doctor":doctors.get(k,{}).get("name",k),"Appointments":v}
                for k,v in w.items()
            ]).sort_values("Appointments",ascending=False)
            st.dataframe(df,use_container_width=True,hide_index=True)
            st.bar_chart(df.set_index("Doctor"))
        else:
            st.info("No workload data for the selected date.")

    with right:
        st.markdown("### Appointment Status")
        df=pd.DataFrame({
            "Status":["Booked","Completed","Cancelled"],
            "Count":[booked,completed,cancelled]
        })
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.bar_chart(df.set_index("Status"))

    st.download_button(
        "⬇️ Export appointments CSV",
        appt_df().to_csv(index=False).encode(),
        "appointments_report.csv",
        "text/csv"
    )
