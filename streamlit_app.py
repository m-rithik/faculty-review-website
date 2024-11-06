import streamlit as st
import re

# Function to read teacher names and image URLs from the text file
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
                    teacher_name, image_url = None, None  # Reset for the next entry
    return teachers

# Clean teacher names for search comparison
def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())

# Load teachers data
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Search for a Teacher")

# Search bar (case insensitive and ignore titles like Dr, Mr, Ms)
search_query = st.text_input("Search for a teacher:")

# Find matching teachers based on the search query
if search_query:
    search_query_cleaned = clean_name(search_query)
    matches = [teachers[i] for i in range(len(teachers_cleaned)) if search_query_cleaned in teachers_cleaned[i]]
else:
    matches = []

# Create a session state to store the reviews and votes
if 'reviews' not in st.session_state:
    st.session_state.reviews = {}
    st.session_state.total_reviews = {}

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher, image_url in matches:
        col1, col2 = st.columns([2, 1])  # Create two columns: one for the name, one for the image

        with col1:
            st.subheader(f"Teacher: {teacher}")

            # Initialize teacher's reviews in session state if not already present
            if teacher not in st.session_state.reviews:
                st.session_state.reviews[teacher] = {
                    'teaching': 0,
                    'leniency': 0,
                    'correction': 0,
                    'da_quiz': 0,
                    'overall': 0
                }
                st.session_state.total_reviews[teacher] = 0

            # Display previous reviews if available
            review = st.session_state.reviews[teacher]
            if st.session_state.total_reviews[teacher] > 0:
                st.write(f"Previous Reviews (out of 10):")
                st.write(f"Teaching: {review['teaching']}")
                st.write(f"Leniency: {review['leniency']}")
                st.write(f"Correction: {review['correction']}")
                st.write(f"DA/Quiz: {review['da_quiz']}")
                st.write(f"Overall: {review['overall']}")
            
            # Input new ratings
            teaching = st.slider("Teaching:", 0, 10, review['teaching'])
            leniency = st.slider("Leniency:", 0, 10, review['leniency'])
            correction = st.slider("Correction:", 0, 10, review['correction'])
            da_quiz = st.slider("DA/Quiz:", 0, 10, review['da_quiz'])

            # Calculate the overall rating
            overall_rating = (teaching + leniency + correction + da_quiz) / 4
            st.session_state.reviews[teacher] = {
                'teaching': teaching,
                'leniency': leniency,
                'correction': correction,
                'da_quiz': da_quiz,
                'overall': overall_rating
            }
            st.session_state.total_reviews[teacher] += 1

            # Display the overall rating as a progress bar
            st.markdown(f"### Overall Rating: {overall_rating:.1f} / 10")
            st.progress(overall_rating / 10)  # Display as progress bar (scaled to 10)

            # Display the teacher's image
            with col2:
                try:
                    st.image(image_url, caption=f"{teacher}'s Picture", use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")

            # Submit button to save the review
            if st.button("Submit Review"):
                st.success("Review submitted successfully!")
else:
    st.write("No teachers found.")
