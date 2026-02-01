
import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="📋",
    layout="centered"
)

# ---------- LOAD DATA ----------
students = pd.read_csv("students.csv")
attendance = pd.read_csv("attendance.csv")

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
h1 {text-align:center;color:#2c3e50;}
.card {
    background:#f9fafb;
    padding:20px;
    border-radius:12px;
    margin-bottom:20px;
    box-shadow:0 4px 10px rgba(0,0,0,0.08);
}
.avatar {
    width:120px;
    border-radius:50%;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>📋 Attendance Management System</h1>", unsafe_allow_html=True)

# ---------- NAVIGATION ----------
role = st.sidebar.radio("Login As", ["Student", "Faculty"])

# ================= STUDENT PAGE =================
if role == "Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👨‍🎓 Student Login")

    roll = st.text_input("Enter Roll Number")

    if roll in students["roll"].values:
        student = students[students["roll"] == roll].iloc[0]

        avatar = (
            "https://cdn-icons-png.flaticon.com/512/4140/4140048.png"
            if student["gender"] == "Male"
            else "https://cdn-icons-png.flaticon.com/512/4140/4140051.png"
        )

        st.image(avatar, width=120)
        st.write(f"**Name:** {student['name']}")
        st.write(f"**Department:** {student['department']}")
        st.write(f"**Year:** {student['year']}")

        student_att = attendance[attendance["roll"] == roll]

        if not student_att.empty:
            total = len(student_att)
            present = len(student_att[student_att["status"] == "Present"])
            percent = round((present / total) * 100, 2)

            st.markdown("### 📊 Attendance Percentage")
            st.progress(percent / 100)
            st.write(f"**{percent}%**")

            chart = student_att["subject"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(chart.values, labels=chart.index, autopct="%1.1f%%")
            st.pyplot(fig)
        else:
            st.info("No attendance records available.")

    else:
        st.warning("Roll number not found. Contact faculty.")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= FACULTY PAGE =================
if role == "Faculty":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("👩‍🏫 Faculty Login")

    pwd = st.text_input("Admin Password", type="password")

    if pwd == "admin123":
        st.success("Login successful")

        # ---- ADD STUDENT ----
        st.markdown("## ➕ Add Student")
        r = st.text_input("Roll Number")
        n = st.text_input("Name")
        g = st.selectbox("Gender", ["Male", "Female"])
        d = st.text_input("Department")
        y = st.selectbox("Year", ["1st", "2nd", "3rd", "4th"])

        if st.button("Add Student"):
            if r in students["roll"].values:
                st.warning("Student already exists")
            else:
                students = pd.concat([
                    students,
                    pd.DataFrame([[r, n, g, d, y]], columns=students.columns)
                ])
                students.to_csv("students.csv", index=False)
                st.success("Student added successfully")

        # ---- MARK ATTENDANCE ----
        st.markdown("## 📝 Mark Attendance")
        ar = st.selectbox("Select Roll", students["roll"])
        subj = st.selectbox("Subject", ["Maths", "Physics", "CS", "Electronics"])

        if st.button("Mark Present"):
            today = str(date.today())
            attendance = pd.concat([
                attendance,
                pd.DataFrame([[today, ar, subj, "Present"]],
                             columns=attendance.columns)
            ])
            attendance.to_csv("attendance.csv", index=False)
            st.success("Attendance marked")

        # ---- VIEW & EXPORT ----
        st.markdown("## 📋 Attendance Records")
        st.dataframe(attendance, use_container_width=True)

        st.download_button(
            "⬇️ Export Attendance CSV",
            attendance.to_csv(index=False),
            "attendance.csv"
        )

    else:
        st.error("Invalid password")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("---")
st.caption("Designed & Developed by Pranav")
