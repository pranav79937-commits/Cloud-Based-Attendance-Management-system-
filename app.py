# =================================================
# 1. IMPORTS
# =================================================
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import matplotlib.pyplot as plt
import random


# =================================================
# 2. PAGE CONFIGURATION
# =================================================
st.set_page_config(
    page_title="Smart Attendance Dashboard",
    page_icon="📊",
    layout="centered"
)


# =================================================
# 3. DATA LOADING (CACHED)
# =================================================
@st.cache_data
def load_data():
    students = pd.read_csv("students.csv")
    attendance = pd.read_csv("attendance.csv")
    return students, attendance

students, attendance = load_data()


# =================================================
# 4. GLOBAL UI CONTROLS
# =================================================
dark_mode = st.sidebar.toggle("🌙 Dark Mode")


# =================================================
# 5. GLOBAL STYLES
# =================================================
st.markdown(f"""
<style>
body {{
    background-color: {"#121212" if dark_mode else "#f4f6f8"};
    color: {"#e0e0e0" if dark_mode else "#000000"};
}}
.header {{
    background: linear-gradient(90deg, #1565c0, #42a5f5);
    padding: 22px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 24px;
}}
.section {{
    background: {"#1e1e1e" if dark_mode else "#ffffff"};
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}}
.metric-box {{
    background: {"#263238" if dark_mode else "#eef6ff"};
    padding: 18px;
    border-radius: 14px;
    text-align: center;
}}
.chip {{
    padding: 6px 14px;
    border-radius: 20px;
    color: white;
    font-size: 13px;
    font-weight: bold;
}}
.safe {{ background: #2e7d32; }}
.warn {{ background: #f9a825; }}
.critical {{ background: #c62828; }}
.stButton > button {{
    background-color: #1565c0;
    color: white;
    border-radius: 10px;
    height: 44px;
    font-size: 16px;
}}
</style>
""", unsafe_allow_html=True)


# =================================================
# 6. HELPERS
# =================================================
def get_attendance_status(percent):
    if percent >= 75:
        return "SAFE", "safe", "Attendance is healthy"
    elif percent >= 60:
        return "WARNING", "warn", "Attendance needs attention"
    else:
        return "CRITICAL", "critical", "Immediate action required"


SUBJECTS = [
    "BEE",
    "ODEVC",
    "DS",
    "AEP",
    "IT WORKSHOP",
    "BEE LAB",
    "DS LAB",
    "PPL LAB"
]


# =================================================
# 7. HEADER
# =================================================
st.markdown("""
<div class="header">
<h1>📊 Smart Attendance Dashboard</h1>
<p>Insight-Driven | Cloud-Deployed | Academic Analytics</p>
</div>
""", unsafe_allow_html=True)


# =================================================
# 8. NAVIGATION
# =================================================
page = st.sidebar.radio(
    "Navigate",
    ["Student", "Faculty", "Analytics"]
)


# =================================================
# 9. STUDENT PAGE
# =================================================
if page == "Student":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("👨‍🎓 Student Dashboard")

    roll = st.text_input("Enter Roll Number")

    if roll in students["roll"].values:
        sa = attendance[attendance["roll"] == roll]

        if not sa.empty:
            total = len(sa)
            present = len(sa[sa["status"] == "Present"])
            percent = round((present / total) * 100, 2)

            status, cls, msg = get_attendance_status(percent)

            st.markdown(f"""
            <div class="metric-box">
            <h2>{percent}%</h2>
            <span class="chip {cls}">{status}</span>
            <p>{msg}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 📊 Subject-wise Attendance")
            fig, ax = plt.subplots()
            sa["subject"].value_counts().plot(kind="pie", autopct="%1.1f%%", ax=ax)
            ax.set_ylabel("")
            st.pyplot(fig)

        else:
            st.info("No attendance records found.")

    else:
        st.warning("Roll number not registered.")

    st.markdown("</div>", unsafe_allow_html=True)


# =================================================
# 10. FACULTY PAGE
# =================================================
if page == "Faculty":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("👩‍🏫 Faculty Dashboard")

    pwd = st.text_input("Admin Password", type="password")

    if pwd == "admin123":
        st.success("Access granted")

        with st.expander("📝 Mark Attendance"):
            ar = st.selectbox("Roll", students["roll"])
            subj = st.selectbox("Subject", SUBJECTS)

            if st.button("Mark Present"):
                attendance = pd.concat([
                    attendance,
                    pd.DataFrame([[str(date.today()), ar, subj, "Present"]],
                                 columns=attendance.columns)
                ])
                attendance.to_csv("attendance.csv", index=False)
                st.toast("Attendance marked")

        with st.expander("⚙️ Generate Demo Attendance"):
            if st.button("Generate 15-Day Demo Data"):
                records = []
                for _, s in students.iterrows():
                    for i in range(1, 16):
                        records.append([
                            str(date.today() - timedelta(days=i)),
                            s["roll"],
                            random.choice(SUBJECTS),
                            "Present" if random.random() > 0.2 else "Absent"
                        ])
                attendance = pd.concat(
                    [attendance, pd.DataFrame(records, columns=attendance.columns)],
                    ignore_index=True
                )
                attendance.to_csv("attendance.csv", index=False)
                st.toast("Demo data generated")

    else:
        st.error("Invalid password")

    st.markdown("</div>", unsafe_allow_html=True)


# =================================================
# 11. ANALYTICS PAGE (🔥 NEW)
# =================================================
if page == "Analytics":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("📈 Attendance Analytics")

    if attendance.empty:
        st.info("No attendance data available.")
    else:
        st.markdown("### 👤 Student-wise Attendance %")
        student_stats = (
            attendance.groupby("roll")["status"]
            .apply(lambda x: (x == "Present").mean() * 100)
        )

        st.bar_chart(student_stats)

        st.markdown("### 📚 Subject-wise Attendance Count")
        st.bar_chart(attendance["subject"].value_counts())

        st.markdown("### 🗓 Weekly Attendance Trend")
        attendance["date"] = pd.to_datetime(attendance["date"])
        weekly = (
            attendance.groupby(attendance["date"].dt.to_period("W"))["status"]
            .apply(lambda x: (x == "Present").mean() * 100)
        )
        weekly.index = weekly.index.astype(str)
        st.line_chart(weekly)

        st.caption("Trends help faculty identify attendance patterns over time.")

    st.markdown("</div>", unsafe_allow_html=True)


# =================================================
# 12. FOOTER
# =================================================
st.markdown("---")
st.caption("Designed & Developed by Pranav")
