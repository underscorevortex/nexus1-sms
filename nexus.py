import streamlit as st
import json
import os

# ─────────────────────────────────────────────
#  FILE PERSISTENCE (Unique Feature)
# ─────────────────────────────────────────────
DATA_FILE = "students.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(students):
    with open(DATA_FILE, "w") as f:
        json.dump(students, f, indent=2)

# ─────────────────────────────────────────────
#  GPA CALCULATION
# ─────────────────────────────────────────────
def grade_to_points(grade):
    scale = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D": 1.0,  "F": 0.0
    }
    return scale.get(grade.strip().upper(), 0.0)

def calculate_gpa(courses):
    total_points = 0
    total_credits = 0
    for c in courses:
        if c["grade"]:
            total_points += grade_to_points(c["grade"]) * c["credits"]
            total_credits += c["credits"]
    if total_credits == 0:
        return 0.0
    return round(total_points / total_credits, 2)

# ─────────────────────────────────────────────
#  INIT SESSION STATE
# ─────────────────────────────────────────────
if "students" not in st.session_state:
    st.session_state.students = load_data()

students = st.session_state.students

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="Nexus SMS", page_icon="🎓", layout="wide")

st.title("🎓 Nexus — Student Management System")
st.caption("OOP Lab Project | Group M: Saleh Omar · Maryam Nadeem · Hamayal Fatima")
st.divider()

# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
page = st.sidebar.radio("Navigation", [
    "📋 All Students",
    "➕ Add Student",
    "📚 Enroll in Course",
    "🎯 Assign Grade",
    "📊 View GPA",
    "❌ Remove Student"
])

st.sidebar.divider()
st.sidebar.caption(f"Total students: **{len(students)}**")

if st.sidebar.button("💾 Save Data to File"):
    save_data(students)
    st.sidebar.success("Saved!")

# ─────────────────────────────────────────────
#  PAGE: ALL STUDENTS
# ─────────────────────────────────────────────
if page == "📋 All Students":
    st.subheader("All Students")

    if not students:
        st.info("No students yet. Go to 'Add Student' to get started.")
    else:
        for sid, s in students.items():
            gpa = calculate_gpa(s["courses"])
            with st.expander(f"**{s['name']}** — ID: {sid} | GPA: {gpa}"):
                col1, col2 = st.columns(2)
                col1.write(f"**Name:** {s['name']}")
                col1.write(f"**ID:** {sid}")
                col2.write(f"**Contact:** {s['contact']}")
                col2.write(f"**GPA:** {gpa}")

                if s["courses"]:
                    st.write("**Courses:**")
                    course_data = []
                    for c in s["courses"]:
                        course_data.append({
                            "Code": c["code"],
                            "Name": c["name"],
                            "Credits": c["credits"],
                            "Grade": c["grade"] if c["grade"] else "Not graded"
                        })
                    st.table(course_data)
                else:
                    st.write("No courses enrolled.")

# ─────────────────────────────────────────────
#  PAGE: ADD STUDENT
# ─────────────────────────────────────────────
elif page == "➕ Add Student":
    st.subheader("Add New Student")

    with st.form("add_student_form"):
        name    = st.text_input("Full Name")
        sid     = st.text_input("Student ID (e.g. S001)")
        contact = st.text_input("Contact Number")
        submit  = st.form_submit_button("Add Student")

    if submit:
        if not name or not sid or not contact:
            st.error("Please fill in all fields.")
        elif sid in students:
            st.error(f"Student with ID {sid} already exists.")
        else:
            students[sid] = {"name": name, "contact": contact, "courses": []}
            save_data(students)
            st.success(f"Student '{name}' added successfully!")

# ─────────────────────────────────────────────
#  PAGE: ENROLL IN COURSE
# ─────────────────────────────────────────────
elif page == "📚 Enroll in Course":
    st.subheader("Enroll Student in a Course")

    if not students:
        st.info("No students yet.")
    else:
        with st.form("enroll_form"):
            sid         = st.selectbox("Select Student", list(students.keys()),
                            format_func=lambda x: f"{students[x]['name']} ({x})")
            course_code = st.text_input("Course Code (e.g. CS101)")
            course_name = st.text_input("Course Name (e.g. OOP)")
            credits     = st.number_input("Credit Hours", min_value=1, max_value=6, value=3)
            submit      = st.form_submit_button("Enroll")

        if submit:
            if not course_code or not course_name:
                st.error("Please fill in all fields.")
            else:
                existing = [c["code"] for c in students[sid]["courses"]]
                if course_code in existing:
                    st.error("Already enrolled in this course.")
                else:
                    students[sid]["courses"].append({
                        "code": course_code,
                        "name": course_name,
                        "credits": credits,
                        "grade": ""
                    })
                    save_data(students)
                    st.success(f"Enrolled in {course_name}!")

# ─────────────────────────────────────────────
#  PAGE: ASSIGN GRADE
# ─────────────────────────────────────────────
elif page == "🎯 Assign Grade":
    st.subheader("Assign Grade to a Course")

    if not students:
        st.info("No students yet.")
    else:
        with st.form("grade_form"):
            sid    = st.selectbox("Select Student", list(students.keys()),
                        format_func=lambda x: f"{students[x]['name']} ({x})")
            courses = students[sid]["courses"]

            if courses:
                course_options = {c["code"]: c["name"] for c in courses}
                course_code    = st.selectbox("Select Course", list(course_options.keys()),
                                    format_func=lambda x: f"{x} — {course_options[x]}")
                grade          = st.selectbox("Grade", ["A+","A","A-","B+","B","B-","C+","C","C-","D","F"])
                submit         = st.form_submit_button("Assign Grade")
            else:
                st.warning("This student has no courses enrolled.")
                submit = False

        if submit:
            for c in students[sid]["courses"]:
                if c["code"] == course_code:
                    c["grade"] = grade
                    break
            save_data(students)
            st.success(f"Grade {grade} assigned to {course_code}!")

# ─────────────────────────────────────────────
#  PAGE: VIEW GPA
# ─────────────────────────────────────────────
elif page == "📊 View GPA":
    st.subheader("GPA Calculator")

    if not students:
        st.info("No students yet.")
    else:
        sid = st.selectbox("Select Student", list(students.keys()),
                format_func=lambda x: f"{students[x]['name']} ({x})")

        s   = students[sid]
        gpa = calculate_gpa(s["courses"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Student", s["name"])
        col2.metric("GPA", gpa)
        col3.metric("Courses", len(s["courses"]))

        if s["courses"]:
            st.write("**Grade Breakdown:**")
            for c in s["courses"]:
                points = grade_to_points(c["grade"]) if c["grade"] else "—"
                st.write(f"- {c['code']} ({c['name']}): **{c['grade'] or 'Not graded'}** | Points: {points} | Credits: {c['credits']}")

# ─────────────────────────────────────────────
#  PAGE: REMOVE STUDENT
# ─────────────────────────────────────────────
elif page == "❌ Remove Student":
    st.subheader("Remove Student")

    if not students:
        st.info("No students yet.")
    else:
        sid = st.selectbox("Select Student to Remove", list(students.keys()),
                format_func=lambda x: f"{students[x]['name']} ({x})")

        st.warning(f"This will permanently delete **{students[sid]['name']}** and all their records.")

        if st.button("Delete Student", type="primary"):
            name = students[sid]["name"]
            del students[sid]
            save_data(students)
            st.success(f"Student '{name}' removed.")
            st.rerun()