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
        # Tries to load the CSV you created
        return pd.read_csv("students.csv")
    except FileNotFoundError:
        # Fallback if file is missing (prevents crash)
        return pd.DataFrame(columns=["roll", "name", "gender", "email"])

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
        if not df_students.empty and roll_input in df_students['roll'].values:
            student_info = df_students[df_students['roll'] == roll_input].iloc[0]
            name = student_info['name']
            
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
                    m2.metric("Classes Attended", str(present_count))
                    m3.metric("Total Sessions", str(total_classes))
                    
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
            if df_students.empty:
                 st.error("Student database (students.csv) is empty or missing.")
            else:
                 st.error("Student not found. Please check the Roll Number.")

# =================================================
# 6. FACULTY ADMIN PANEL
# =================================================
elif menu == "👮 Faculty Admin":
    st.title("👮 Faculty Command Center")
    
    # Simple Auth
    password = st.sidebar.text_input("Admin Password", type="password")
    
    if password == "admin123":
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
            
            if not df_students.empty:
                # Create a temporary dataframe for editing
                edit_df = df_students[['roll', 'name']].copy()
                edit_df['Status'] = True if action == "Mark All Present" else False
                
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
            else:
                st.warning("No students found in students.csv")
        
        # --- TAB 2: MANAGE STUDENTS ---
        with tab2:
            st.warning("⚠️ Editing the Master Roll List")
            updated_students = st.data_editor(df_students, num_rows="dynamic")
            
            if st.button("Save Changes to Student List"):
                updated_students.to_csv("students.csv", index=False)
                st.success("Student Database Updated!")
                st.rerun()
                
    else:
        st.info("Please enter the admin password to access faculty controls.")

# =================================================
# 7. ANALYTICS HUB
# =================================================
elif menu == "📊 Analytics Hub":
    st.title("📊 Class Analytics Reports")
    
    if st.session_state.attendance_data.empty:
        st.warning("No attendance data available yet.")
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
        if not daily_att.empty:
            fig_line = px.line(daily_att, x='Date', y='Roll', title="Daily Attendance Count", markers=True)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Not enough data for trend analysis.")
        
        # 2. Defaulters List (< 75%)
        st.subheader("🚨 Low Attendance Alert (<75%)")
        
        # Calculate percentages
        student_counts = st.session_state.attendance_data[st.session_state.attendance_data['Status']=='Present']['Name'].value_counts().reset_index()
        student_counts.columns = ['Name', 'Present_Count']
        
        st.dataframe(student_counts, use_container_width=True)
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
