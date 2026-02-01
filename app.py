import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Attendance Dashboard",
    page_icon="📊",
    layout="centered"
)

# ---------------- LOAD DATA ----------------
students = pd.read_csv("students.csv")
attendance = pd.read_csv("attendance.csv")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {background-color:#f4f6f8;}
h1 {text-align:center;}
.section {
    background:white;
    padding:22px;
    border-radius:16px;
    margin-bottom:22px;
    box-shadow:0 8px 24px rgba(0,0,0,0.08);
}
.metric-box {
    background:#eef6ff;
    padding:16px;
    border-radius:14px;
    text-align:center;
}
.chip {
    padding:6px 14px;
    border-radius:20px;
    color:white;
    font-size:13px;
    font-weight:bold;
}
.safe {background:#2e7d32;}
.warn {background:#f9a825;}
.critical {background:#c62828;}
.avatar {
    width:90px;
    border-radius:50%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="section" style="background:linear-gradient(90deg,#1565c0,#42a5f5);color:white;">
<h1>📊 Smart Attendance Dashboard</h1>
<p style="text-align:center;">Insight-Driven | Cloud-Deployed | Student-Centric</p>
</div>
""", unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------
role = st.sidebar.radio("Select Role", ["Student", "Faculty"])

# ================= STUDENT =================
if role == "Student":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("👨‍🎓 Student Access")

    roll = st.text_input("Enter Roll Number")

    if roll in students["roll"].values:
        student = students[students["roll"] == roll].iloc[0]

        avatar = (
            "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
            if student["gender"] == "Male"
            else "https://cdn-icons-png.flaticon.com/512/4140051.png"
        )

        st.image(avatar, width=90)
        st.markdown(f"""
**Name:** {student['name']}  
**Department:** {student['department']}  
**Year:** {student['year']}
""")

        student_att = attendance[attendance["roll"] == roll]

        if not student_att.empty:
            total = len(student_att)
            present = len(student_att[student_att["status"] == "Present"])
            percent = round((present / total) * 100, 2)

            # ---- Risk Logic ----
            if percent >= 75:
                status, cls, msg = "SAFE", "safe", "Attendance is healthy"
            elif percent >= 60:
                status, cls, msg = "WARNING", "warn", "Attendance needs attention"
            else:
                status, cls, msg = "CRITICAL", "critical", "Immediate action required"

            st.markdown(f"""
<div class="section">
<div class="metric-box">
<h2>{percent}%</h2>
<span class="chip {cls}">{status}</span>
<p>{msg}</p>
</div>
</div>
""", unsafe_allow_html=True)

            if st.checkbox("Show subject-wise breakdown"):
                chart = student_att["subject"].value_counts()
                fig, ax = plt.subplots()
                ax.pie(chart.values, labels=chart.index, autopct="%1.1f%%")
                st.pyplot(fig)

            st.caption("Attendance percentage is calculated based on recorded classes.")
        else:
            st.info("No attendance data available.")

    else:
        st.warning("Roll number not registered.")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= FACULTY =================
if role == "Faculty":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("👩‍🏫 Faculty Dashboard")

    pwd = st.text_input("Admin Password", type="password")

    if pwd == "admin123":
        st.success("Access granted")

        # ---- INSIGHT ROW ----
        col1, col2 = st.columns(2)
        col1.metric("Total Students", len(students))
        col2.metric("Attendance Records", len(attendance))

        st.caption("Quick system overview for decision making.")

        # ---- ADD STUDENT ----
        with st.expander("➕ Add / Update Student"):
            r = st.text_input("Roll Number")
            n = st.text_input("Name")
            g = st.selectbox("Gender", ["Male", "Female"])
            d = st.text_input("Department")
            y = st.selectbox("Year", ["1st","2nd","3rd","4th"])

            if st.button("Save Student"):
                students = students[students["roll"] != r]
                students = pd.concat([students, pd.DataFrame([[r,n,g,d,y]], columns=students.columns)])
                students.to_csv("students.csv", index=False)
                st.success("Student record saved")

        # ---- MARK ATTENDANCE ----
        with st.expander("📝 Mark Attendance"):
            ar = st.selectbox("Roll", students["roll"])
            subj = st.selectbox("Subject", ["Maths","Physics","CS","Electronics"])
            if st.button("Mark Present"):
                attendance = pd.concat([
                    attendance,
                    pd.DataFrame([[str(date.today()), ar, subj, "Present"]],
                                 columns=attendance.columns)
                ])
                attendance.to_csv("attendance.csv", index=False)
                st.success("Attendance marked")

        # ---- DATA VIEW ----
        with st.expander("📋 View & Export Records"):
            st.dataframe(attendance, use_container_width=True)
            st.download_button(
                "⬇️ Export CSV",
                attendance.to_csv(index=False),
                "attendance.csv"
            )

    else:
        st.error("Invalid password")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Designed & Developed by Pranav")
