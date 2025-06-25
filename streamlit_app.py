import streamlit as st
import re
import gspread
from google.oauth2.service_account import Credentials
from fpdf import FPDF
import re
from datetime import datetime





@st.cache_resource
def get_google_sheet():
    try:
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(credentials)
        sheet = client.open_by_key("1QYO7pcHGH3DOjogXCKxTTKQVqaQldePvlcvoawS6gxc").sheet1
        return sheet
    except Exception as e:
        st.error(f"Failed to connect to Google Sheets: {str(e)}")
        return None


@st.cache_data(ttl=65)
def load_teachers(file):
    teachers = []
    with open(file, 'r') as f:
        lines = f.readlines()
        teacher_name = None
        image_url = None
        for line in lines:
            if line.startswith("Name:"):
                teacher_name = line.strip().replace("Name: ", "")
            elif line.startswith("Image:"):
                image_url = line.strip().replace("Image: ", "")
                if teacher_name and image_url:
                    teachers.append((teacher_name, image_url))
                    teacher_name, image_url = None, None
    return teachers


def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())


def calculate_overall_rating(reviews):
    if reviews:
        return sum(reviews) / len(reviews)
    return 0


@st.cache_data(ttl=65)
def get_all_reviews():
    sheet = get_google_sheet()
    if sheet:
        return sheet.get_all_records()
    return []


def get_teacher_reviews(records, teacher_name):
    cleaned_teacher_name = clean_name(teacher_name)
    reviews = [record for record in records if clean_name(record.get('Teacher ', '').strip()) == cleaned_teacher_name]
    return reviews

teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]


st.title("VIT Vellore Teacher Review")
st.header("Search for a Teacher")

search_query = st.text_input("Search for a teacher:")

if search_query:
    search_query_cleaned = clean_name(search_query)
    matches = [teachers[i] for i in range(len(teachers_cleaned)) if search_query_cleaned in teachers_cleaned[i]]
else:
    matches = []

records = get_all_reviews()

if matches:
    st.write("Teachers found:")
    for idx, (teacher, image_url) in enumerate(matches):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"Teacher: {teacher}")

            reviews = get_teacher_reviews(records, clean_name(teacher))

            if reviews:
                st.write("### Reviews:")
                overall_ratings = []
                teaching_scores = []
                leniency_scores = []
                correction_scores = []
                da_quiz_scores = []

                for review in reviews:
                    teaching_scores.append(review.get('Teaching ', 0))
                    leniency_scores.append(review.get('Leniency ', 0))
                    correction_scores.append(review.get('Correction ', 0))
                    da_quiz_scores.append(review.get('DA/Quiz ', 0))
                    overall_ratings.append(review.get('Overall Rating', 0))

                    comment = review.get('Comment', '-')
                    comment_display = f"*{comment}*" if comment != '-' else '-'
                    st.write(f"- **Teaching**: {review.get('Teaching ', 'N/A')} | **Leniency**: {review.get('Leniency ', 'N/A')} | "
                             f"**Correction**: {review.get('Correction ', 'N/A')} | **DA/Quiz**: {review.get('DA/Quiz ', 'N/A')} | "
                             f"**Comment**: {comment_display}")

                if overall_ratings:
                    avg_overall_rating = sum(overall_ratings) / len(overall_ratings)
                    avg_overall_rating = min(avg_overall_rating, 10)
                else:
                    avg_overall_rating = 0

                num_reviews = len(reviews)
                st.write(f"### Overall Rating: {avg_overall_rating:.2f} / 10 ({num_reviews} reviews)")
            else:
                st.write("No reviews submitted yet for this teacher.")

            st.markdown("### **Rate the Teacher**")
            teaching = st.slider("Teaching", 0, 10, key=f"teaching_{idx}")
            leniency = st.slider("Leniency", 0, 10, key=f"leniency_{idx}")
            correction = st.slider("Correction", 0, 10, key=f"correction_{idx}")
            da_quiz = st.slider("DA/Quiz", 0, 10, key=f"da_quiz_{idx}")

            overall_rating_input = calculate_overall_rating([teaching, leniency, correction, da_quiz])
            st.write(f"**Overall Rating**: {overall_rating_input:.2f} / 10")

            # Comment section with live character count
            max_comment_length = 100
            comment = st.text_area(
                "Leave a comment (optional, max 100 characters):",
                key=f"comment_{idx}",
                max_chars=max_comment_length,
                placeholder="Type your comment here..."
            )
            comment_length = len(comment)
            st.write(f"{comment_length}/{max_comment_length} characters")

            with col2:
                try:
                    st.image(image_url, caption=f"{teacher}", width=150)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")

            submit_button = st.button(f"Submit Review for {teacher}", key=f"submit_{idx}")

            if submit_button:
                if teacher not in st.session_state.get('submitted_reviews', []):
                    data_to_insert = [teacher, teaching, leniency, correction, da_quiz, overall_rating_input, comment]

                    try:
                        sheet = get_google_sheet()
                        if sheet:
                            sheet.append_row(data_to_insert)
                            st.success(f"Review for {teacher} submitted successfully!")

                            if 'submitted_reviews' not in st.session_state:
                                st.session_state.submitted_reviews = []
                            st.session_state.submitted_reviews.append(teacher)
                    except Exception as e:
                        st.error(f"Failed to submit review: {e}")
                else:
                    st.warning(f"Review for {teacher} has already been submitted. You can only submit one review per teacher.")
else:
    st.write("No teachers found.")

records = get_all_reviews()
total_reviews = len(records)

hide_github_icon = """
    <style>
    /* Hide GitHub icon and viewer badge */
    .css-1jc7ptx, .e1ewe7hr3,
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_,
    .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK,
    .css-1dp5vir { /* GitHub icon container */
        display: none;
    }

    /* Optional: Hide Streamlit Main Menu, Footer, and Header */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
"""


st.markdown(hide_github_icon, unsafe_allow_html=True)

st.markdown(
    f"""
    <hr style="margin-top: 3rem;">
    <div style="text-align: center; color: grey; font-size: 1 rem;">
        Please contribute with reviews, all the old reviews were deleted due to database problems | <a href="https://forms.gle/YFLkZi3UxRtGyxdA9" target="_blank" style="color: #8f8f8f; text-decoration: none; font-weight: bold;">Contact Me</a>
    </div>

    <div style="text-align: center; color: #4CAF50; font-size: 1.5rem; margin-top: 1rem;">
        Total number of reviews: {total_reviews}
    </div>

    """,
    unsafe_allow_html=True
)



# Set Streamlit to wide mode
st.set_page_config(layout="wide")

# --- Clear form fields if needed (before widgets are created) ---
# (No clearing after every entry)

def parse_time(t):
    # Handles both '8:00 AM' and '08:00 AM' and returns minutes since midnight
    t = t.strip().replace('AM', ' AM').replace('PM', ' PM')
    try:
        return int(datetime.strptime(t, "%I:%M %p").hour) * 60 + int(datetime.strptime(t, "%I:%M %p").minute)
    except Exception:
        return None

def time_range_to_tuple(start, end):
    s = parse_time(start)
    e = parse_time(end)
    return (s, e)

# --- FFCS TimetableData mapping (from ffcs-planner-main/lib/slots.ts) ---
days = ["MON", "TUE", "WED", "THU", "FRI"]
timetableData = {
    "MON": [
        ["A1", "L1"], ["F1", "L2"], ["D1", "L3"], ["TB1", "L4"], ["TG1", "L5"], ["L6"], [""],
        ["A2", "L31"], ["F2", "L32"], ["D2", "L33"], ["TB2", "L34"], ["TG2", "L35"], ["L36"]
    ],
    "TUE": [
        ["B1", "L7"], ["G1", "L8"], ["E1", "L9"], ["TC1", "L10"], ["TAA1", "L11"], ["L12"], [""],
        ["B2", "L37"], ["G2", "L38"], ["E2", "L39"], ["TC2", "L40"], ["TAA2", "L41"], ["L42"]
    ],
    "WED": [
        ["C1", "L13"], ["A1", "L14"], ["F1", "L15"], ["V1", "L16"], ["V2", "L17"], ["L18"], [""],
        ["C2", "L43"], ["A2", "L44"], ["F2", "L45"], ["TD2", "L46"], ["TBB2", "L47"], ["L48"]
    ],
    "THU": [
        ["D1", "L19"], ["B1", "L20"], ["G1", "L21"], ["TE1", "L22"], ["TCC1", "L23"], ["L24"], [""],
        ["D2", "L49"], ["B2", "L50"], ["G2", "L51"], ["TE2", "L52"], ["TCC2", "L53"], ["L54"]
    ],
    "FRI": [
        ["E1", "L25"], ["C1", "L26"], ["TA1", "L27"], ["TF1", "L28"], ["TD1", "L29"], ["L30"], [""],
        ["E2", "L55"], ["C2", "L56"], ["TA2", "L57"], ["TF2", "L58"], ["TDD2", "L59"], ["L60"]
    ]
}
# Theory and lab time labels (for header)
theory_times = [
    "8:00 AM to 8:50 AM", "9:00 AM to 9:50 AM", "10:00 AM to 10:50 AM", "11:00 AM to 11:50 AM", "12:00 PM to 12:50 PM", "-", "-", "2:00 PM to 2:50 PM", "3:00 PM to 3:50 PM", "4:00 PM to 4:50 PM", "5:00 PM to 5:50 PM", "6:00 PM to 6:50 PM", "6:51 PM to 7:00 PM"
]
lab_times = [
    "8:00 AM to 8:50 AM", "8:51 AM to 9:40 AM", "9:50 AM to 10:40 AM","10:41 AM to 11:30 AM","11:40 AM to 12:30 PM","12:30 PM to 1:20 AM", "-", "2:00 PM to 2:50 PM", "2:51 PM to 3:40 PM", "3:51 PM to 4:40 PM", "4:41 PM to 5:30 PM", "5:40 PM to 6:30 PM", "6:30 PM to 7:20 PM",
]

# --- Build slot-to-cell mapping and slot-to-time mapping ---
slot_to_cells = {}
cell_to_slots = {}  # (day, period) -> [slot, ...]
slot_time_map = {}
for day in days:
    for period, slots in enumerate(timetableData[day]):
        cell_to_slots[(day, period)] = slots
        for slot in slots:
            if slot:
                slot_to_cells.setdefault(slot, []).append((day, period))
                # Map time for both theory and lab slots
                if not slot.startswith("L"):
                    # Theory slot
                    if period < len(theory_times) and theory_times[period] != "-":
                        start, end = theory_times[period].split(" to ") if "to" in theory_times[period] else (theory_times[period], theory_times[period])
                        slot_time_map[(day, slot)] = time_range_to_tuple(start, end)
                else:
                    # Lab slot
                    if period < len(lab_times) and lab_times[period] != "-":
                        start, end = lab_times[period].split(" to ") if "to" in lab_times[period] else (lab_times[period], lab_times[period])
                        slot_time_map[(day, slot)] = time_range_to_tuple(start, end)

# --- State ---
def get_state():
    if "faculty_list" not in st.session_state:
        st.session_state["faculty_list"] = []
    if "timetable" not in st.session_state:
        st.session_state["timetable"] = {(day, period): None for day in days for period in range(len(timetableData[day]))}
    # Add form state for clearing
    for key in ["course_code", "course_name", "faculty", "slot_str", "room"]:
        if key not in st.session_state or st.session_state[key] is None:
            st.session_state[key] = ""
    return st.session_state
state = get_state()

# --- UI Styling ---
st.markdown("""
    <style>
    body, .main, .stApp {background-color: #181e29 !important; color: #fff;}
    .ffcs-table {border-collapse: collapse; width: 100%; background: #181e29; color: #fff;}
    .ffcs-table th, .ffcs-table td {border: 1px solid #232b3b; text-align: center; font-weight: bold;}
    .ffcs-table th {background: #232b3b; color: #7ecfff;}
    .ffcs-table .lunch {background: #232b3b; color: #ffb347;}
    .ffcs-table .green {background: #2ecc40 !important; color: #fff;}
    .ffcs-table .red {background: #e74c3c !important; color: #fff;}
    .ffcs-table .empty {background: #181e29;}
    .ffcs-table .period-label {background: #232b3b; color: #fff; font-weight: bold;}
    .ffcs-table .theory-time {background: #bfcafc; color: #222; font-weight: bold;}
    .ffcs-table .lab-time {background: #b3e0fc; color: #222; font-weight: bold;}
    .ffcs-table td, .ffcs-table th {width: 110px; height: 60px; min-width: 110px; min-height: 60px; max-width: 110px; max-height: 60px; overflow: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("FFCS Faculty Timetable")
st.write("Add faculty directly to the timetable. No course management. No clashes allowed.")

# --- Faculty Input Form ---
st.subheader("Add Faculty")
with st.form("add_faculty_form"):
    course_code = st.text_input("Course Code", value=state["course_code"], key="course_code")
    course_name = st.text_input("Course Name", value=state["course_name"], key="course_name")
    faculty = st.text_input("Faculty Name", value=state["faculty"], key="faculty")
    slot_str = st.text_input("Slot(s) (e.g. A1+A2+B1)", value=state["slot_str"], key="slot_str")
    room = st.text_input("Room Number", value=state["room"], key="room")
    submitted = st.form_submit_button("Add to Timetable")
    clash_msg = ""
    if submitted:
        # Only slot_str is compulsory
        if not slot_str.strip():
            st.error("Slot(s) is a required field.")
        else:
            slots = [s.strip().upper() for s in re.split(r'\+|,|\s+', slot_str) if s.strip()]
            clash = False
            cells_to_fill = set()
            # --- Check for timing overlap between input slots ---
            for i in range(len(slots)):
                for j in range(i+1, len(slots)):
                    slot1, slot2 = slots[i], slots[j]
                    for cell1 in slot_to_cells.get(slot1, []):
                        for cell2 in slot_to_cells.get(slot2, []):
                            if cell1[0] == cell2[0]:  # Same day
                                t1 = slot_time_map.get((cell1[0], slot1))
                                t2 = slot_time_map.get((cell2[0], slot2))
                                if t1 and t2 and not (t1[1] <= t2[0] or t1[0] >= t2[1]):
                                    clash = True
                                    clash_msg = f"Timing clash between {slot1} and {slot2} on {cell1[0]}."
                                    break
                        if clash:
                            break
                    if clash:
                        break
                if clash:
                    break
            # --- End input slot timing overlap check ---
            if not clash:
                for slot in slots:
                    if slot not in slot_to_cells:
                        clash = True
                        clash_msg = f"Invalid slot: {slot}."
                        break
                    for cell in slot_to_cells[slot]:
                        if state["timetable"][cell] is not None:
                            clash = True
                            clash_msg = f"Clash: {slot} already assigned on {cell[0]} period {cell[1]+1}."
                            break
                        # --- FFCSonTheGo-style timing clash detection ---
                        this_time = slot_time_map.get((cell[0], slot))
                        if this_time:
                            for p in range(len(timetableData[cell[0]])):
                                other_entry = state["timetable"][(cell[0], p)]
                                if other_entry:
                                    for other_slot in cell_to_slots[(cell[0], p)]:
                                        if other_slot and (cell[0], other_slot) in slot_time_map:
                                            other_time = slot_time_map[(cell[0], other_slot)]
                                            # Check for overlap
                                            if other_time and not (this_time[1] <= other_time[0] or this_time[0] >= other_time[1]):
                                                clash = True
                                                clash_msg = f"Timing clash: {slot} ({theory_times[cell[1]] if not slot.startswith('L') else lab_times[cell[1]]}) overlaps with {other_slot} on {cell[0]}."
                                                break
                                if clash:
                                    break
                        if clash:
                            break
                        cells_to_fill.add(cell)
                    if clash:
                        break
            if not clash:
                for cell in cells_to_fill:
                    state["timetable"][cell] = {
                        "course_code": course_code,
                        "course_name": course_name,
                        "faculty": faculty,
                        "slots": slot_str,
                        "room": room
                    }
                state["faculty_list"].append({
                    "course_code": course_code,
                    "course_name": course_name,
                    "faculty": faculty,
                    "slots": slot_str,
                    "room": room
                })
            else:
                st.error(clash_msg or "Slot or timing clash detected.")

# --- Timetable Preview ---
def render_timetable():
    html = '<table class="ffcs-table">'
    # Header row: time slots
    html += '<tr><th class="period-label" rowspan="2">DAY</th>'
    for i in range(len(theory_times)):
        html += f'<th class="theory-time">{theory_times[i]}</th>'
    html += '</tr>'
    html += '<tr>'
    for i in range(len(lab_times)):
        html += f'<th class="lab-time">{lab_times[i]}</th>'
    html += '</tr>'
    # Rows for each day
    for day in days:
        html += f'<tr><td class="period-label">{day}</td>'
        # Theory row
        for period in range(len(theory_times)):
            slots = timetableData[day][period] if period < len(timetableData[day]) else []
            entry = state["timetable"][(day, period)] if (day, period) in state["timetable"] else None
            slot_label = " / ".join([s for s in slots if s])
            if not slot_label:
                html += '<td class="lunch">LUNCH</td>'
            elif entry:
                is_lab = any(s.startswith("L") for s in slots if s) and any(s.startswith("L") for s in slots if s and s in [x.upper() for x in entry["slots"].replace(",", "+").split("+")])
                cell_class = "red" if is_lab else "green"
                # Only show course code and room number
                html += f'<td class="{cell_class}">{slot_label}<br>{entry["course_code"]}<br>{entry["room"]}</td>'
            else:
                html += f'<td class="empty">{slot_label}</td>'
        html += '</tr>'
    html += '</table>'
    return html

with st.expander("Timetable Preview", expanded=True):
    st.markdown(render_timetable(), unsafe_allow_html=True)

# --- Faculty List ---
st.subheader("Faculty List")
st.dataframe(state["faculty_list"])

# --- Export as PDF ---
def export_pdf():
    # Use mm for A4 sizing
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "FFCS Faculty Timetable", ln=True, align="C")
    pdf.ln(2)
    n_cols = len(theory_times)
    margin = 10
    table_width = 297 - 2 * margin
    cell_w = table_width / (n_cols + 1)  # +1 for DAY column
    cell_h = 14  # Slightly taller for readability
    # --- Header: Theory times ---
    pdf.set_x(margin)
    pdf.set_font("Arial", size=6)
    pdf.set_fill_color(235, 235, 235)  # Very light gray for DAY header
    pdf.cell(cell_w, cell_h, "DAY", border=1, align='C', fill=True)
    pdf.set_fill_color(191, 202, 252)  # Light blue for theory header
    for i in range(n_cols):
        header = theory_times[i]
        if 'to' in header:
            t1, t2 = header.split(' to ')
            t1 = t1.strip()
            t2 = t2.strip()
            header_fmt = f"{t1}\nto\n{t2}"
        else:
            header_fmt = header
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(cell_w, cell_h / 3, header_fmt, border=1, align='C', fill=True)
        pdf.set_xy(x + cell_w, y)
    pdf.ln(cell_h)
    # --- Header: Lab times ---
    pdf.set_x(margin)
    pdf.set_fill_color(220, 230, 250)  # Lighter blue for lab header
    pdf.cell(cell_w, cell_h, "", border=1, align='C', fill=True)
    for i in range(n_cols):
        header = lab_times[i]
        if 'to' in header:
            t1, t2 = header.split(' to ')
            t1 = t1.strip()
            t2 = t2.strip()
            header_fmt = f"{t1}\nto\n{t2}"
        else:
            header_fmt = header
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.multi_cell(cell_w, cell_h / 3, header_fmt, border=1, align='C', fill=True)
        pdf.set_xy(x + cell_w, y)
    pdf.ln(cell_h)
    pdf.set_font("Arial", size=7)
    # --- Rows for each day ---
    for day in days:
        pdf.set_x(margin)
        pdf.set_fill_color(235, 235, 235)  # Very light gray for day cells
        pdf.cell(cell_w, cell_h, day, border=1, align='C', fill=True)
        for period in range(n_cols):
            slots = timetableData[day][period] if period < len(timetableData[day]) else []
            entry = state["timetable"][(day, period)] if (day, period) in state["timetable"] else None
            slot_label = " / ".join([s for s in slots if s])
            if not slot_label:
                pdf.set_fill_color(235, 235, 235)  # Very light gray for lunch
                pdf.cell(cell_w, cell_h, "LUNCH", border=1, align='C', fill=True)
            elif entry:
                is_lab = any(s.startswith("L") for s in slots if s) and any(s.startswith("L") for s in slots if s and s in [x.upper() for x in entry["slots"].replace(",", "+").split("+")])
                if is_lab:
                    pdf.set_fill_color(231, 76, 60)
                else:
                    pdf.set_fill_color(46, 204, 64)
                # Only show course code and room number
                content = f'{slot_label}\n{entry["course_code"]}\n{entry["room"]}'
                # Truncate to 3 lines if needed
                lines = content.split('\n')
                if len(lines) > 3:
                    lines = lines[:3]
                    lines[-1] = lines[-1][:12] + '...' if len(lines[-1]) > 12 else lines[-1]
                content = '\n'.join(lines)
                x = pdf.get_x()
                y = pdf.get_y()
                # Use multi_cell for filled cells, but keep height fixed
                pdf.multi_cell(cell_w, cell_h / 3, content, border=1, align='C', fill=True)
                # Move cursor to the right of the cell
                pdf.set_xy(x + cell_w, y)
            else:
                pdf.set_fill_color(255, 255, 255)  # White for empty cells
                pdf.cell(cell_w, cell_h, slot_label, border=1, align='C', fill=True)
        pdf.ln(cell_h)
    # Faculty List Table
    pdf.ln(5)
    pdf.set_font("Arial", size=8)
    pdf.set_x(margin)
    pdf.cell(0, 8, "Faculty List", ln=True, align="L")
    pdf.set_x(margin)
    headers = ["Course Code", "Course Name", "Faculty", "Slots", "Room"]
    col_widths = [30, 45, 45, 45, 30]
    for i, h in enumerate(headers):
        pdf.set_fill_color(191, 202, 252)
        pdf.cell(col_widths[i], 8, h, border=1, align='C', fill=True)
    pdf.ln(8)
    for entry in state["faculty_list"]:
        pdf.set_x(margin)
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_widths[0], 8, entry["course_code"], border=1, align='C', fill=True)
        pdf.cell(col_widths[1], 8, entry["course_name"], border=1, align='C', fill=True)
        pdf.cell(col_widths[2], 8, entry["faculty"], border=1, align='C', fill=True)
        pdf.cell(col_widths[3], 8, entry["slots"], border=1, align='C', fill=True)
        pdf.cell(col_widths[4], 8, entry["room"], border=1, align='C', fill=True)
        pdf.ln(8)
    return pdf.output(dest="S").encode("latin1")

if st.button("Export as PDF"):
    pdf_bytes = export_pdf()
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="ffcs_faculty_timetable.pdf",
        mime="application/pdf"
    ) 



