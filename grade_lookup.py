import streamlit as st
import pandas as pd

st.title("Grade Lookup System")
st.write("Enter your Student ID to view your grades in all courses.")

# ---------------------------------------------------------------------------
# Course configuration.
#   file      -> Excel filename in the repo
#   id_col    -> column holding the student ID
#   name_col  -> column holding the student name
#   display   -> list of (Label to show, Column name in the file), in order
#
# The first data row of each file holds each column's WEIGHT as a fraction
# (e.g. 0.30 = 30%). The max mark for a column = weight * 100. This is read
# automatically, so totals update if you change a weight in Excel.
# To add another course later, just add a new entry here.
# ---------------------------------------------------------------------------
COURSES = {
    "Discrete Mathematics": {
        "file": "discrete_summer_grades.xlsx",
        "id_col": "ID",
        "name_col": "Name",
        "display": [
            ("Quiz 1", "Quiz 1"),
            ("Quiz 2", "Quiz 2"),
            ("Quiz 3", "Quiz 3"),
            ("Best Quizzes", "Best Quizzes Rounded"),
            ("Midterm", "Midterm"),
            ("Participation", "Participation"),
            ("Total Pre-Final", "Total Pre-Final"),
        ],
    },
    "Introudction to Probability Theory": {
        "file": "prob_summer_grades.xlsx",
        "id_col": "ID",
        "name_col": "Name",
        "display": [
            ("Quiz 1", "Quiz 1"),
            ("Quiz 2", "Quiz 2"),
            ("Best Quiz", "Best Quiz"),
            ("Assign 1", "Assign 1"),
            ("Assign 2", "Assign 2"),
            ("Midterm", "Midterm"),
            ("Participation", "Participation"),
            ("Total Pre-Final", "Total Pre-Final"),
        ],
    },
}


@st.cache_data
def load_course(file_path, id_col):
    """Load a course file. Returns (students_df, totals dict per column)."""
    raw = pd.read_excel(file_path)

    # First row = weights (fraction of 100). Build a max-mark per column.
    weights_row = raw.iloc[0]
    totals = {}
    for col in raw.columns:
        w = weights_row[col]
        if pd.notna(w) and isinstance(w, (int, float)):
            totals[col] = round(w * 100, 2)

    # Remaining rows = students; keep only those with an ID.
    df = raw.iloc[1:].copy()
    df = df[df[id_col].notna()]
    df[id_col] = df[id_col].astype(float).astype("int64").astype(str)
    return df, totals


def clean_num(value):
    """Return a tidy number (drop trailing .0), or 0 for missing marks."""
    if pd.isna(value):
        value = 0
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def format_grade(value, total):
    """Display as grade/total, e.g. 10.5/15."""
    mark = clean_num(value)
    if total is None:
        return f"{mark}"
    return f"{mark}/{clean_num(total)}"


student_id = st.text_input("Student ID").strip()

if student_id:
    found_any = False

    for course_name, cfg in COURSES.items():
        try:
            df, totals = load_course(cfg["file"], cfg["id_col"])
        except FileNotFoundError:
            st.warning(f"⚠️ File for {course_name} not found.")
            continue

        row = df[df[cfg["id_col"]] == student_id]

        if len(row) == 1:
            found_any = True
            r = row.iloc[0]

            st.header(f"📘 {course_name}")
            st.success(f"Student Name: **{r[cfg['name_col']]}**")
            for label, col in cfg["display"]:
                if col in df.columns:
                    st.success(f"{label}: **{format_grade(r[col], totals.get(col))}**")

    if not found_any:
        st.error("❌ Student ID not found in any course.")
