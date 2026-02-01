# =================================================
# IMPORTS
# =================================================
import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from fpdf import FPDF

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config("Smart Attendance System", "📊", layout="centered")

# =================================================
# CONSTANTS
# =================================================
MALE_AVATAR = "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
FEMALE_AVATAR = "https://cdn-icons-png.flaticon.com/512/4140/4140051.png"

# =================================================
# DATA LOADING
# =================================================
@st.cache_data
def load_data():
    students = pd.read_csv("students.csv")
    attendance = pd.read_csv("attendance.csv")
    subjects = pd.read_csv("subjects.csv")["subject"].tolist()
    return students, attendance, subjects

students, attendance, SUBJECTS = load_data()

# =================================================
# HELPER FUNCTIONS (BACKEND LOGIC)
# =================================================
def get_student_attendance(df, roll):
    return df[df["roll"] == roll]

def calculate_percentage(df):
    if df.empty:
        return 0
    return round((df["status"] == "Present").mean() * 100, 2)

def subject_wise_percentage(df):
    return df.groupby("subject")["status"].apply(
        lambda x: round((x == "Present").mean() * 100, 2)
    )

def monthly_percentage(df):
    df["date"] = pd.to_datetime(df["date"])
    return df.groupby(df["date"].dt.to_period("M"))["status"].apply(
        lambda x: round((x == "Present").mean() * 100, 2)
    )

# =================================================
# UI STYLES
# =================================================
dark = st.sidebar.toggle("🌙 Dark Mode")
st.markdown(f"""
<style>
body {{
 background: {"#121212" if dark else "#f4f6f8"};
 color: {"#eee" if dark else "#000"};
}}
.card {{
 background: {"#1e1e1e" if dark else "#fff"};
 padding:20px;
 border-radius:16px;
 margin-bottom:20px;
 box-shadow:0 8px 24px rgba(0,0,0,.08);
}}
</style>
""", unsafe_allow_html=True)

# =================================================
# HEADER
# =================================================
st.markdown("""
<div class="card">
<h2>📊 Smart Attendance Management System</h2>
<p>Analytics-Driven • AppSheet-Inspired • Cloud-Deployed</p>
</div>
""", unsafe_allow_html=True)

# =================================================
# NAVIGATION
# =================================================
page = st.sidebar.radio("Navigate", ["Student", "Faculty"])

# =================================================
# STUDENT DASHBOARD
# =================================================
if page == "Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    roll = st.text_input("Enter Roll Number")

    if roll in students["roll"].values:
        s = students[students["roll"] == roll].iloc[0]
        st.image(MALE_AVATAR if s["gender"]=="Male" else FEMALE_AVATAR, width=90)
        st.write(f"**{s['name']} | {s['department']} | {s['year']}**")

        sa = get_student_attendance(attendance, roll)

        overall = calculate_percentage(sa)
        st.metric("Overall Attendance %", f"{overall}%")

        if not sa.empty:
            st.subheader("📚 Subject-wise Attendance")
            fig, ax = plt.subplots()
            subject_wise_percentage(sa).plot(kind="pie", autopct="%1.1f%%", ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)

            st.subheader("📅 Monthly Attendance")
            st.bar_chart(monthly_percentage(sa))

    else:
        st.warning("Roll number not found")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FACULTY DASHBOARD
# =================================================
if page == "Faculty":
    pwd = st.text_input("Admin Password", type="password")

    if pwd == "admin123":
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        roll = st.selectbox("Select Student", students["roll"])
        sa = get_student_attendance(attendance, roll)

        st.dataframe(sa)

        subj = st.selectbox("Subject", SUBJECTS)
        status = st.radio("Status", ["Present", "Absent"])

        if st.button("Mark Attendance"):
            attendance = pd.concat([
                attendance,
                pd.DataFrame([[str(date.today()), roll, subj, status]],
                columns=attendance.columns)
            ])
            attendance.to_csv("attendance.csv", index=False)
            st.success("Attendance updated")

        st.download_button(
            "Download CSV",
            sa.to_csv(index=False),
            "attendance.csv"
        )

        if st.button("Download PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.cell(0,10,"Attendance Report", ln=True)
            for _, r in sa.iterrows():
                pdf.cell(0,8,f"{r['date']} | {r['subject']} | {r['status']}", ln=True)
            pdf.output("report.pdf")
            with open("report.pdf","rb") as f:
                st.download_button("Click to Download PDF", f, "report.pdf")

        st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# 8. FOOTER (Personal Branding)
# =================================================
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
