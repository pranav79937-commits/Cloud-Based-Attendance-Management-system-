import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from fpdf import FPDF
import base64

# =================================================
# 1. PAGE CONFIGURATION & THEME
# =================================================
st.set_page_config(
    page_title="ACE IoT Smart Attendance",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Figma-like Glassmorphism & Cards
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Card Styling */
    .css-card {
        border-radius: 15px;
        padding: 20px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px;
        color: #2E86C1;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1a2e;
        color: white;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        color: #1a1a2e;
    }
</style>
""", unsafe_allow_html=True)

# =================================================
# 2. DATA HANDLER (BACKEND LOGIC)
# =================================================
SUBJECTS = ["BEE", "ODEVC", "DS", "AEP", "IT WORKSHOP", "BEE LAB", "DS LAB", "PPL LAB"]

# Initialize Session State (This acts as your temporary database)
if 'attendance_data' not in st.session_state:
    # Try to load existing csv, else create empty
    try:
        st.session_state.attendance_data = pd.read_csv('attendance_log.csv')
    except:
        columns = ['Date', 'Roll', 'Name', 'Subject', 'Status', 'Timestamp']
        st.session_state.attendance_data = pd.DataFrame(columns=columns)

@st.cache_data
def load_students():
    try:
        return pd.read_csv("students.csv")
    except FileNotFoundError:
        st.error("Please create students.csv file first!")
        return pd.DataFrame()

df_students = load_students()

# =================================================
# 3. HELPER FUNCTIONS
# =================================================
def get_avatar_url(name):
    """Generates a professional avatar based on initials"""
    clean_name = name.replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={clean_name}&background=random&color=fff&size=128&bold=true"

def download_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Attendance Report", ln=True, align='C')
    pdf.ln(10)
    
    # Simple table dump
    for i, row in dataframe.iterrows():
        pdf.cell(0, 10, txt=f"{row['Date']} - {row['Name']} ({row['Roll']}) - {row['Subject']} - {row['Status']}", ln=True)
        
    return pdf.output(dest="S").encode("latin-1")

# =================================================
# 4. APP NAVIGATION & LAYOUT
# =================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2995/2995458.png", width=100)
st.sidebar.title("ACE IoT Portal")
menu = st.sidebar.radio("Navigation", ["🏠 Dashboard (Student)", "👮 Faculty Admin", "📊 Analytics Hub"])

# =================================================
# 5. STUDENT DASHBOARD
# =================================================
if menu == "🏠 Dashboard (Student)":
    st.title("🎓 Student Portal")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("### 🆔 Login")
        roll_input = st.text_input("Enter Roll Number", placeholder="e.g., 25AG1A6901").upper()
        
    if roll_input:
        student_info = df_students[df_students['roll'] == roll_input]
        
        if not student_info.empty:
            name = student_info.iloc[0]['name']
            
            # Profile Card
            with col1:
                st.image(get_avatar_url(name), width=150)
                st.markdown(f"**{name}**")
                st.caption(f"IoT Batch 2025-26 | {roll_input}")
                st.success("✅ Student Verified")
            
            # Attendance Stats
            with col2:
                # Filter data for this student
                student_data = st.session_state.attendance_data[st.session_state.attendance_data['Roll'] == roll_input]
                
                if not student_data.empty:
                    total_classes = len(student_data)
                    present_count = len(student_data[student_data['Status'] == 'Present'])
                    attendance_pct = (present_count / total_classes) * 100 if total_classes > 0 else 0
                    
                    # Top Metrics
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Overall Attendance", f"{attendance_pct:.1f}%", f"{attendance_pct-75:.1f}% vs Target")
                    m2.metric("Classes Attended", present_count)
                    m3.metric("Total Sessions", total_classes)
                    
                    st.divider()
                    
                    # Charts
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("Subject-wise Performance")
                        subj_counts = student_data[student_data['Status'] == 'Present']['Subject'].value_counts().reset_index()
                        subj_counts.columns = ['Subject', 'Count']
                        fig_bar = px.bar(subj_counts, x='Subject', y='Count', color='Count', template="plotly_white")
                        st.plotly_chart(fig_bar, use_container_width=True)
                        
                    with c2:
                        st.subheader("Attendance Distribution")
                        status_counts = student_data['Status'].value_counts().reset_index()
                        status_counts.columns = ['Status', 'Count']
                        fig_pie = px.pie(status_counts, values='Count', names='Status', hole=0.5, color_discrete_sequence=['#00CC96', '#EF553B'])
                        st.plotly_chart(fig_pie, use_container_width=True)
                        
                else:
                    st.info("👋 No attendance records found yet. Ask your faculty to mark attendance.")
        else:
            st.error("Student not found in the IoT 1st Year database.")

# =================================================
# 6. FACULTY ADMIN PANEL
# =================================================
elif menu == "👮 Faculty Admin":
    st.title("👮 Faculty Command Center")
    
    # Simple Auth
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":  # Simple auth for demo
        tab1, tab2 = st.tabs(["📝 Mark Attendance", "👥 Manage Students"])
        
        # --- TAB 1: MARK ATTENDANCE ---
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                sel_date = st.date_input("Date", datetime.now())
            with c2:
                sel_subject = st.selectbox("Select Subject", SUBJECTS)
            with c3:
                action = st.radio("Bulk Action", ["Mark All Present", "Manual"], horizontal=True)
            
            st.subheader(f"Attendance Sheet: {sel_subject} ({sel_date})")
            
            # Create a temporary dataframe for editing
            edit_df = df_students[['roll', 'name']].copy()
            edit_df['Status'] = 'Present' if action == "Mark All Present" else False
            
            # The Data Editor (Excel-like interface)
            edited_df = st.data_editor(
                edit_df,
                column_config={
                    "Status": st.column_config.CheckboxColumn(
                        "Present?",
                        help="Check if present",
                        default=True
                    )
                },
                disabled=["roll", "name"],
                hide_index=True,
                num_rows="fixed",
                use_container_width=True
            )
            
            if st.button("🚀 Submit Attendance to Cloud"):
                # Process the edited dataframe
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_records = []
                
                for index, row in edited_df.iterrows():
                    status = "Present" if row['Status'] else "Absent"
                    new_records.append({
                        'Date': sel_date,
                        'Roll': row['roll'],
                        'Name': row['name'],
                        'Subject': sel_subject,
                        'Status': status,
                        'Timestamp': timestamp
                    })
                
                # Append to session state
                new_df = pd.DataFrame(new_records)
                st.session_state.attendance_data = pd.concat([st.session_state.attendance_data, new_df], ignore_index=True)
                
                # Save to CSV (local backup)
                st.session_state.attendance_data.to_csv('attendance_log.csv', index=False)
                st.success(f"Successfully marked attendance for {len(new_records)} students!")
        
        # --- TAB 2: MANAGE STUDENTS ---
        with tab2:
            st.warning("⚠️ Editing the Master Roll List")
            updated_students = st.data_editor(df_students, num_rows="dynamic")
            
            if st.button("Save Changes to Student List"):
                updated_students.to_csv("students.csv", index=False)
                st.success("Student Database Updated!")
                
    else:
        st.info("Please enter the admin password to access faculty controls.")

# =================================================
# 7. ANALYTICS HUB
# =================================================
elif menu == "📊 Analytics Hub":
    st.title("📊 Class Analytics Reports")
    
    if st.session_state.attendance_data.empty:
        st.warning("No data available yet.")
    else:
        # Download Section
        st.subheader("📥 Export Reports")
        col1, col2 = st.columns(2)
        
        # CSV Download
        csv = st.session_state.attendance_data.to_csv(index=False).encode('utf-8')
        col1.download_button(
            "📄 Download CSV Report",
            csv,
            "attendance_report.csv",
            "text/csv",
            key='download-csv'
        )
        
        # PDF Download
        pdf_bytes = download_pdf(st.session_state.attendance_data)
        col2.download_button(
            "📑 Download PDF Report",
            data=pdf_bytes,
            file_name="attendance_report.pdf",
            mime="application/pdf"
        )
        
        st.divider()
        
        # Visual Analytics
        st.subheader("📈 Trends")
        
        # 1. Attendance by Date
        daily_att = st.session_state.attendance_data[st.session_state.attendance_data['Status']=='Present'].groupby('Date').count()['Roll'].reset_index()
        fig_line = px.line(daily_att, x='Date', y='Roll', title="Daily Attendance Count", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
        # 2. Defaulters List (< 75%)
        st.subheader("🚨 Low Attendance Alert (<75%)")
        
        # Calculate percentages
        total_sessions = st.session_state.attendance_data['Date'].nunique() # Approx
        student_counts = st.session_state.attendance_data[st.session_state.attendance_data['Status']=='Present']['Name'].value_counts().reset_index()
        student_counts.columns = ['Name', 'Present_Count']
        
        # NOTE: In a real app, this logic needs to be more robust based on total classes held per subject
        # Here we just show a leaderboard
        st.dataframe(student_counts, use_container_width=True)
        if not sa.empty:
            total = len(sa)
            present = len(sa[sa["status"]=="Present"])
            overall = round(present/total*100,2)

            st.metric("Overall Attendance %", f"{overall}%")

            # SUBJECT PIE
            st.subheader("📚 Subject-wise Attendance")
            subj_pct = sa.groupby("subject")["status"].apply(
                lambda x: (x=="Present").mean()*100
            )

            fig, ax = plt.subplots()
            ax.pie(subj_pct.values, labels=subj_pct.index, autopct="%1.1f%%")
            st.pyplot(fig)

            # MONTHLY TREND
            st.subheader("📅 Monthly Attendance Trend")
            sa["date"] = pd.to_datetime(sa["date"])
            monthly = sa.groupby(sa["date"].dt.to_period("M"))["status"].apply(
                lambda x:(x=="Present").mean()*100
            )
            st.bar_chart(monthly)

        else:
            st.info("No attendance data available.")

    else:
        st.warning("Roll number not found.")

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FACULTY DASHBOARD
# =================================================
if page == "Faculty":
    pwd = st.text_input("Admin Password", type="password")

    if pwd == "admin123":
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        # STUDENT LIST
        st.subheader("👥 Student Profiles")
        selected = st.selectbox("Select Student", students["roll"])
        sp = students[students["roll"]==selected].iloc[0]

        st.image(MALE_AVATAR if sp["gender"]=="Male" else FEMALE_AVATAR, width=80)
        st.write(sp)

        # MARK ATTENDANCE
        st.subheader("📝 Mark Attendance")
        subj = st.selectbox("Subject", SUBJECTS)
        status = st.radio("Status", ["Present", "Absent"])

        if st.button("Save Attendance"):
            attendance = pd.concat([
                attendance,
                pd.DataFrame([[str(date.today()), selected, subj, status]],
                columns=attendance.columns)
            ])
            attendance.to_csv("attendance.csv", index=False)
            st.success("Attendance recorded")

        # VIEW REPORT
        st.subheader("📊 Attendance Report")
        report = attendance[attendance["roll"]==selected]
        st.dataframe(report)

        # EXPORT CSV
        st.download_button(
            "⬇️ Download CSV",
            report.to_csv(index=False),
            "attendance.csv"
        )

        # EXPORT PDF
        if st.button("⬇️ Download PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=10)
            pdf.cell(0,10,"Attendance Report", ln=True)

            for _,r in report.iterrows():
                pdf.cell(0,8,f"{r['date']} | {r['subject']} | {r['status']}", ln=True)

            pdf.output("report.pdf")
            with open("report.pdf","rb") as f:
                st.download_button("Download PDF File", f, "report.pdf")

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.error("Invalid password")

# =================================================
# FOOTER
# =================================================
st.caption("Designed & Developed by Pranav")    "AEP",
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
