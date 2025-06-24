import streamlit as st
import re
import gspread
from google.oauth2.service_account import Credentials




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

#MainMenu {
  visibility: hidden;
}

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
