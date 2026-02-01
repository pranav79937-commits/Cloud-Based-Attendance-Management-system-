# =================================================
# 1. IMPORTS
# =================================================
import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from fpdf import FPDF

# =================================================
# 2. PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Smart Attendance Management System",
    page_icon="📊",
    layout="centered"
)

# =================================================
# 3. CONSTANTS
# =================================================
MALE_AVATAR = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
FEMALE_AVATAR = "https://cdn-icons-png.flaticon.com/512/4140/4140051.png"

# =================================================
# 4. DATA ACCESS LAYER
# =================================================
@st.cache_data
def load_data():
    students = pd.read_csv("students.csv")
    attendance = pd.read_csv("attendance.csv")
    subjects = pd.read_csv("subjects.csv")["subject"].tolist()
    return students, attendance, subjects

students, attendance, SUBJECTS = load_data()

# =================================================
# 5. BACKEND LOGIC (CACHED ANALYTICS)
# =================================================
def get_student_attendance(df, roll):
    return df[df["roll"] == roll]

def attendance_percentage(df):
    return round((df["status"] == "Present").mean() * 100, 2) if not df.empty else 0.0

@st.cache_data
def compute_subject_stats(df):
    return df.groupby("subject")["status"].apply(
        lambda x: round((x == "Present").mean() * 100, 2)
    )

@st.cache_data
def compute_monthly_stats(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.groupby(df["date"].dt.to_period("M"))["status"].apply(
        lambda x: round((x == "Present").mean() * 100, 2)
    )

def eligibility_rule(p):
    if p >= 85:
        return "Eligible for Exam", "success"
    elif p >= 75:
        return "Conditional Eligibility", "warning"
    else:
        return "Not Eligible for Exam", "error"

# =================================================
# 6. UI STYLES
# =================================================
dark = st.sidebar.toggle("🌙 Dark Mode")

st.markdown(f"""
<style>
body {{
    background: {"#121212" if dark else "#f4f6f8"};
}}
.card {{
    background: {"#1e1e1e" if dark else "#fff"};
    padding: 20px;
    border-radius: 16px;
    margin-bottom: 20px;
}}
</style>
""", unsafe_allow_html=True)

# =================================================
# 7. HEADER
# =================================================
st.markdown("""
<div class="card">
<h2>📊 Smart Attendance Management System</h2>
<p>Analytics-Driven • AppSheet-Inspired • Cloud-Deployed</p>
</div>
""", unsafe_allow_html=True)

# =================================================
# 8. NAVIGATION
# =================================================
page = st.sidebar.radio("Navigate", ["Student", "Faculty"])

# =================================================
# 9. STUDENT DASHBOARD
# =================================================
if page == "Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    roll = st.text_input("Enter Roll Number", placeholder="e.g. 23AG1A6901")

    if not roll:
        st.info("Please enter your roll number to view attendance.")
    elif roll in students["roll"].values:
        s = students[students["roll"] == roll].iloc[0]
        sa = get_student_attendance(attendance, roll)

        st.image(MALE_AVATAR if s["gender"] == "Male" else FEMALE_AVATAR, width=90)
        st.write(f"**{s['name']} | {s['department']} | {s['year']}**")

        overall = attendance_percentage(sa)
        st.metric("Overall Attendance %", f"{overall}%")

        label, level = eligibility_rule(overall)
        getattr(st, level)(label)

        if sa.empty:
            st.info("No attendance records available yet.")
        else:
            with st.expander("📊 View Attendance Analytics", expanded=True):
                subj_stats = compute_subject_stats(sa)

                fig, ax = plt.subplots()
                ax.pie(subj_stats.values, labels=subj_stats.index, autopct="%1.1f%%")
                st.pyplot(fig)

                st.bar_chart(compute_monthly_stats(sa))
    else:
        st.error("Roll number not found.")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# 10. FACULTY DASHBOARD
# =================================================
if page == "Faculty":
    password = st.text_input("Admin Password", type="password")

    if password == "admin123":
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["👤 Student Management", "📊 Attendance"])

        with tab1:
            st.subheader("Add / Edit Student")
            with st.form("student_form"):
                roll_new = st.text_input("Roll Number")
                name_new = st.text_input("Name")
                gender_new = st.selectbox("Gender", ["Male", "Female"])
                dept_new = st.text_input("Department")
                year_new = st.selectbox("Year", ["1st", "2nd", "3rd", "4th"])
                save = st.form_submit_button("Save Student")

            if save and roll_new and name_new:
                students = students[students["roll"] != roll_new]
                students = pd.concat(
                    [students, pd.DataFrame([[roll_new, name_new, gender_new, dept_new, year_new]],
                    columns=students.columns)],
                    ignore_index=True
                )
                students.to_csv("students.csv", index=False)
                st.success("Student saved")
                st.cache_data.clear()
            elif save:
                st.warning("Roll number and name are required")

        with tab2:
            selected_roll = st.selectbox("Select Student", students["roll"])
            sa = get_student_attendance(attendance, selected_roll)

            if sa.empty:
                st.info("No attendance records yet.")
            else:
                st.dataframe(sa, use_container_width=True)

                fig, ax = plt.subplots()
                stats = compute_subject_stats(sa)
                ax.pie(stats.values, labels=stats.index, autopct="%1.1f%%")
                st.pyplot(fig)

            st.subheader("Mark Attendance")
            subject = st.selectbox("Subject", SUBJECTS)
            status = st.radio("Status", ["Present", "Absent"])

            if st.button("Mark Attendance"):
                attendance = pd.concat(
                    [attendance, pd.DataFrame([[str(date.today()), selected_roll, subject, status]],
                    columns=attendance.columns)],
                    ignore_index=True
                )
                attendance.to_csv("attendance.csv", index=False)
                st.success("Attendance marked")
                st.cache_data.clear()

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Invalid password")

# =================================================
# 11. FOOTER
# =================================================
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center;color:#888;font-size:14px">
Designed & Developed by <b style="color:#2E86C1">Pranav</b><br>
CSE (IoT) | 2025-26
</div>
""", unsafe_allow_html=True)
