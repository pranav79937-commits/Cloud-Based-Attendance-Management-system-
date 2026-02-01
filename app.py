import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Smart Attendance Dashboard",
    page_icon="📊",
    layout="centered"
)

# -------------------------------------------------
# DATA (BACKEND UNTOUCHED)
# -------------------------------------------------
students = pd.read_csv("students.csv")
attendance = pd.read_csv("attendance.csv")

# -------------------------------------------------
# DARK MODE TOGGLE
# -------------------------------------------------
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

# -------------------------------------------------
# FIGMA-INSPIRED DESIGN TOKENS → CSS
# -------------------------------------------------
if dark_mode:
    st.markdown("""
    <style>
    :root {
        --bg:#121212;
        --card:#1e1e1e;
        --text:#e0e0e0;
        --primary:#42a5f5;
        --safe:#2e7d32;
        --warn:#f9a825;
        --critical:#c62828;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    :root {
        --bg:#f4f6f8;
        --card:#ffffff;
        --text:#000000;
        --primary:#1565c0;
        --safe:#2e7d32;
        --warn:#f9a825;
        --critical:#c62828;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<style>
body { background-color: var(--bg); color: var(--text); }

.header {
    background: linear-gradient(90deg, var(--primary), #42a5f5);
    padding: 22px;
    border-radius: 16px;
    color: white;
    text-align: center;
    margin-bottom: 24px;
}

.section {
    background: var(--card);
    padding: 22px;
    border-radius: 16px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.metric-box {
    background: rgba(66,165,245,0.12);
    padding: 18px;
    border-radius: 14px;
    text-align: center;
}

.chip {
    padding: 6px 14px;
    border-radius: 20px;
    color: white;
    font-size: 13px;
    font-weight: bold;
}

.safe { background: var(--safe); }
.warn { background: var(--warn); }
.critical { background: var(--critical); }

.stButton > button {
    background-color: var(--primary);
    color: white;
    border-radius: 10px;
    height: 44px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.markdown("""
<div class="header">
<h1>📊 Smart Attendance Dashboard</h1>
<p>Insight-Driven | Cloud-Deployed | Student-Centric</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# NAVIGATION
# -------------------------------------------------
role = st.sidebar.radio("Select Role", ["Student", "Faculty"])

# =================================================
# STUDENT VIEW
# =================================================
if role == "Student":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("👨‍🎓 Student Access")

    roll = st.text_input("Enter Roll Number")

    if roll in students["roll"].values:
        s = students[students["roll"] == roll].iloc[0]

        avatar = (
            "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
            if s["gender"] == "Male"
            else "https://cdn-icons-png.flaticon.com/512/4140051.png"
        )

        st.image(avatar, width=90)
        st.markdown(f"""
**Name:** {s['name']}  
**Department:** {s['department']}  
**Year:** {s['year']}
""")

        sa = attendance[attendance["roll"] == roll]

        if not sa.empty:
            total = len(sa)
            present = len(sa[sa["status"] == "Present"])
            percent = round((present / total) * 100, 2)

            if percent >= 75:
                cls, msg = "safe", "Attendance is healthy"
            elif percent >= 60:
                cls, msg = "warn", "Attendance needs attention"
            else:
                cls, msg = "critical", "Immediate action required"

            st.markdown(f"""
<div class="section">
<div class="metric-box">
<h2>{percent}%</h2>
<span class="chip {cls}">{msg}</span>
</div>
</div>
""", unsafe_allow_html=True)

            if st.checkbox("Show subject-wise breakdown"):
                chart = sa["subject"].value_counts()
                fig, ax = plt.subplots()
                ax.pie(chart.values, labels=chart.index, autopct="%1.1f%%")
                st.pyplot(fig)

            st.caption("Attendance percentage is calculated from recorded classes.")
        else:
            st.info("No attendance records yet.")

    else:
        st.warning("Roll number not registered.")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FACULTY VIEW
# =================================================
if role == "Faculty":
    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.subheader("👩‍🏫 Faculty Dashboard")

    pwd = st.text_input("Admin Password", type="password")

    if pwd == "admin123":
        st.success("Access granted")

        col1, col2 = st.columns(2)
        col1.metric("Total Students", len(students))
        col2.metric("Attendance Records", len(attendance))

        st.caption("System overview for quick decision making.")

        with st.expander("➕ Add / Update Student"):
            r = st.text_input("Roll Number")
            n = st.text_input("Name")
            g = st.selectbox("Gender", ["Male", "Female"])
            d = st.text_input("Department")
            y = st.selectbox("Year", ["1st","2nd","3rd","4th"])

            if st.button("Save Student"):
                students = students[students["roll"] != r]
                students = pd.concat([
                    students,
                    pd.DataFrame([[r,n,g,d,y]], columns=students.columns)
                ])
                students.to_csv("students.csv", index=False)
                st.success("Student record saved")

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

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption("Designed & Developed by Pranav")<p>{msg}</p>
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
