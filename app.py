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
# 4. DATA LOADING
# =================================================
@st.cache_data
def load_data():
    students = pd.read_csv("students.csv")
    attendance = pd.read_csv("attendance.csv")
    subjects = pd.read_csv("subjects.csv")["subject"].tolist()
    return students, attendance, subjects

students, attendance, SUBJECTS = load_data()

# =================================================
# 5. HELPER FUNCTIONS (BACKEND LOGIC)
# =================================================
def get_student_attendance(df, roll):
    return df[df["roll"] == roll]

def calculate_percentage(df):
    if df.empty:
        return 0.0
    return round((df["status"] == "Present").mean() * 100, 2)

def subject_wise_percentage(df):
    return df.groupby("subject")["status"].apply(
        lambda x: round((x == "Present").mean() * 100, 2)
    )

def monthly_percentage(df):
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.groupby(df["date"].dt.to_period("M"))["status"].apply(
        lambda x: round((x == "Present").mean() * 100, 2)
    )

# =================================================
# 6. DARK MODE + STYLES (FIGMA-INSPIRED)
# =================================================
dark = st.sidebar.toggle("🌙 Dark Mode")

st.markdown(
    f"""
    <style>
    body {{
        background: {"#121212" if dark else "#f4f6f8"};
        color: {"#eee" if dark else "#000"};
    }}
    .card {{
        background: {"#1e1e1e" if dark else "#ffffff"};
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =================================================
# 7. HEADER
# =================================================
st.markdown(
    """
    <div class="card">
        <h2>📊 Smart Attendance Management System</h2>
        <p>Analytics-Driven • AppSheet-Inspired • Cloud-Deployed</p>
    </div>
    """,
    unsafe_allow_html=True
)

# =================================================
# 8. NAVIGATION
# =================================================
page = st.sidebar.radio("Navigate", ["Student", "Faculty"])

# =================================================
# 9. STUDENT DASHBOARD
# =================================================
if page == "Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    roll = st.text_input("Enter Roll Number")

    if roll in students["roll"].values:
        s = students[students["roll"] == roll].iloc[0]

        avatar = MALE_AVATAR if s["gender"] == "Male" else FEMALE_AVATAR
        st.image(avatar, width=90)

        st.write(f"**Name:** {s['name']}")
        st.write(f"**Department:** {s['department']} | **Year:** {s['year']}")

        sa = get_student_attendance(attendance, roll)

        overall = calculate_percentage(sa)
        st.metric("Overall Attendance %", f"{overall}%")

        if not sa.empty:
            # SUBJECT-WISE PIE
            st.subheader("📚 Subject-wise Attendance (%)")
            subj_pct = subject_wise_percentage(sa)

            fig1, ax1 = plt.subplots()
            ax1.pie(subj_pct.values, labels=subj_pct.index, autopct="%1.1f%%")
            ax1.set_ylabel("")
            st.pyplot(fig1)

            # MONTHLY TREND
            st.subheader("📅 Monthly Attendance (%)")
            st.bar_chart(monthly_percentage(sa))
        else:
            st.info("No attendance records available yet.")

    else:
        st.warning("Roll number not found.")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# 10. FACULTY DASHBOARD
# =================================================
if page == "Faculty":
    password = st.text_input("Admin Password", type="password")

    if password == "admin123":
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # -------------------------------
        # ADD / EDIT STUDENT
        # -------------------------------
        st.subheader("➕ Add / ✏️ Edit Student")

        with st.form("student_form"):
            roll_new = st.text_input("Roll Number")
            name_new = st.text_input("Student Name")
            gender_new = st.selectbox("Gender", ["Male", "Female"])
            dept_new = st.text_input("Department")
            year_new = st.selectbox("Year", ["1st", "2nd", "3rd", "4th"])
            save_student = st.form_submit_button("Save / Update Student")

        if save_student:
            students = students[students["roll"] != roll_new]
            students = pd.concat(
                [
                    students,
                    pd.DataFrame(
                        [[roll_new, name_new, gender_new, dept_new, year_new]],
                        columns=students.columns,
                    ),
                ],
                ignore_index=True,
            )
            students.to_csv("students.csv", index=False)
            st.success("Student saved successfully")
            st.cache_data.clear()

        st.markdown("---")

        # -------------------------------
        # STUDENT PROFILE + ATTENDANCE
        # -------------------------------
        st.subheader("👤 Student Profile & Attendance")

        selected_roll = st.selectbox("Select Student", students["roll"])
        sp = students[students["roll"] == selected_roll].iloc[0]

        avatar = MALE_AVATAR if sp["gender"] == "Male" else FEMALE_AVATAR
        st.image(avatar, width=80)
        st.write(sp)

        sa = get_student_attendance(attendance, selected_roll)
  # ATTENDANCE HISTORY
# -------------------------------
if sa.empty:
    st.info("No attendance records found for this student yet.")
else:
    st.subheader("📋 Attendance History")
    st.dataframe(sa, use_container_width=True)
    
        # -------------------------------

        # SUBJECT-WISE PIE (FACULTY)
        if not sa.empty:
            st.subheader("📊 Subject-wise Attendance (%)")

            subj_pct_f = subject_wise_percentage(sa)
            fig2, ax2 = plt.subplots()
            ax2.pie(subj_pct_f.values, labels=subj_pct_f.index, autopct="%1.1f%%")
            ax2.set_ylabel("")
            st.pyplot(fig2)

        st.markdown("---")

        # -------------------------------
        # MARK ATTENDANCE
        # -------------------------------
        st.subheader("📝 Mark Attendance")

        subject = st.selectbox("Subject", SUBJECTS)
        status = st.radio("Status", ["Present", "Absent"])

        if st.button("Mark Attendance"):
            attendance = pd.concat(
                [
                    attendance,
                    pd.DataFrame(
                        [[str(date.today()), selected_roll, subject, status]],
                        columns=attendance.columns,
                    ),
                ],
                ignore_index=True,
            )
            attendance.to_csv("attendance.csv", index=False)
            st.success("Attendance marked successfully")
            st.cache_data.clear()

        st.markdown("---")

        # -------------------------------
        # EXPORT REPORTS
        # -------------------------------
        st.subheader("⬇️ Download Reports")

        st.download_button(
            "Download CSV",
            sa.to_csv(index=False),
            "attendance_report.csv",
        )

        if st.button("Generate PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.cell(0, 10, "Attendance Report", ln=True)

            for _, r in sa.iterrows():
                pdf.cell(
                    0,
                    8,
                    f"{r['date']} | {r['subject']} | {r['status']}",
                    ln=True,
                )

            pdf.output("attendance_report.pdf")

            with open("attendance_report.pdf", "rb") as f:
                st.download_button(
                    "Download PDF",
                    f,
                    "attendance_report.pdf",
                )

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Invalid password")

# ==========================================================
# 8. FOOTER (Personal Branding)
# ==========================================================

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <style>
    .footer {
        text-align: center;
        color: #888;
        font-size: 14px;
        margin-top: 20px;
        font-family: 'Segoe UI', sans-serif;
    }
    .footer b {
        color: #2E86C1;
    }
    </style>
    <div class="footer">
        Designed & Developed by <br>
        <b>Pranav</b> <br>
        <span style="font-size: 12px">CSE (IoT) | 2025-26</span>
    </div>
    """,
    unsafe_allow_html=True
    )
