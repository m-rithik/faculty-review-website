import streamlit as st
import re
import gspread
from google.oauth2.service_account import Credentials

# Test Block for CSS Validation
st.markdown(
    """
    <div style="background-color: #f9f9f9; border: 1px solid #ddd; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center;">
        <h3 style="color: #4CAF50;">Test Block</h3>
        <p>If you see this styled block, your CSS works correctly!</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Google Sheets Connection
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

# Load Teachers from File
@st.cache_data(ttl=65)
def load_teachers(file):
    teachers = []
    with open(file, 'r') as f:
        lines = f.readlines()
        teacher_name, image_url = None, None
        for line in lines:
            if line.startswith("Name:"):
                teacher_name = line.strip().replace("Name: ", "")
            elif line.startswith("Image:"):
                image_url = line.strip().replace("Image: ", "")
                if teacher_name and image_url:
                    teachers.append((teacher_name, image_url))
    return teachers

# Helper Functions
def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())

def calculate_overall_rating(reviews):
    return sum(reviews) / len(reviews) if reviews else 0

@st.cache_data(ttl=65)
def get_all_reviews():
    sheet = get_google_sheet()
    return sheet.get_all_records() if sheet else []

def get_teacher_reviews(records, teacher_name):
    cleaned_teacher_name = clean_name(teacher_name)
    return [record for record in records if clean_name(record.get('Teacher ', '').strip()) == cleaned_teacher_name]

# Load Teachers and Reviews
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Title and Header
st.title("VIT Vellore Teacher Review")
st.header("Search for a Teacher")

# Search Input
search_query = st.text_input("Search for a teacher:")

# Search Logic
if search_query:
    search_query_cleaned = clean_name(search_query)
    matches = [teachers[i] for i in range(len(teachers_cleaned)) if search_query_cleaned in teachers_cleaned[i]]
else:
    matches = []

records = get_all_reviews()

# Display Results
if matches:
    st.write("Teachers found:")
    for idx, (teacher, image_url) in enumerate(matches):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(
                f"""
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px;">
                    <h3 style="color: #2c3e50;">{teacher}</h3>
                </div>
                """,
                unsafe_allow_html=True,
            )

            reviews = get_teacher_reviews(records, teacher)

            if reviews:
                overall_ratings = [review.get('Overall Rating', 0) for review in reviews]
                avg_overall_rating = calculate_overall_rating(overall_ratings)
                num_reviews = len(reviews)
                st.write(f"### Overall Rating: {avg_overall_rating:.2f} / 10 ({num_reviews} reviews)")

                for review in reviews:
                    st.markdown(
                        f"""
                        <div style="background-color: #fff; padding: 10px; border: 1px solid #ddd; border-radius: 5px; margin-bottom: 10px;">
                            <p>**Teaching**: {review.get('Teaching ', 'N/A')} | **Leniency**: {review.get('Leniency ', 'N/A')} | **Correction**: {review.get('Correction ', 'N/A')} | **DA/Quiz**: {review.get('DA/Quiz ', 'N/A')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No reviews submitted yet for this teacher.")

            st.markdown("### Rate the Teacher")
            teaching = st.slider("Teaching", 0, 10, key=f"teaching_{idx}")
            leniency = st.slider("Leniency", 0, 10, key=f"leniency_{idx}")
            correction = st.slider("Correction", 0, 10, key=f"correction_{idx}")
            da_quiz = st.slider("DA/Quiz", 0, 10, key=f"da_quiz_{idx}")
            overall_rating_input = calculate_overall_rating([teaching, leniency, correction, da_quiz])
            st.write(f"**Overall Rating**: {overall_rating_input:.2f} / 10")

        with col2:
            st.image(image_url, caption=teacher, width=150)

        submit_button = st.button(f"Submit Review for {teacher}", key=f"submit_{idx}")
        if submit_button:
            sheet = get_google_sheet()
            if sheet:
                sheet.append_row([teacher, teaching, leniency, correction, da_quiz, overall_rating_input])
                st.success(f"Review for {teacher} submitted successfully!")
else:
    st.write("No teachers found.")

# Footer
st.markdown(
    f"""
    <hr style="margin-top: 3rem;">
    <div style="text-align: center; color: grey; font-size: 1rem;">
        Please contribute with reviews | <a href="https://forms.gle/YFLkZi3UxRtGyxdA9" target="_blank" style="color: #8f8f8f; text-decoration: none; font-weight: bold;">Contact Me</a>
    </div>
    <div style="text-align: center; color: #4CAF50; font-size: 1.5rem; margin-top: 1rem;">
        Total number of reviews: {len(records)}
    </div>
    """,
    unsafe_allow_html=True,
)
