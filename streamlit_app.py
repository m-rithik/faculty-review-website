import streamlit as st
import pandas as pd
import re

# Function to read teacher names from SCOPE.txt
def load_teachers(file):
    with open(file, 'r') as f:
        teachers = f.readlines()
    return [teacher.strip() for teacher in teachers]

# Clean teacher names for search comparison
def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())

# Load teachers data from the correct file path
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher) for teacher in teachers]

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Leave a Review ")

# Search bar (case insensitive and ignore titles like Dr, Mr, Ms)
search_query = st.text_input("Search for a teacher:")

# Find matching teachers based on the search query
if search_query:
    search_query_cleaned = clean_name(search_query)
    matches = [teachers[i] for i in range(len(teachers_cleaned)) if search_query_cleaned in teachers_cleaned[i]]
else:
    matches = []

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher in matches:
        st.write(teacher)
    
    # Let the user leave a review for each teacher
    for teacher in matches:
        st.subheader(f"Leave a review for {teacher}:")

        # Text input for review
        teaching_review = st.text_input(f"Review Teaching for {teacher}")
        leniency_review = st.text_input(f"Review Leniency for {teacher}")
        correction_review = st.text_input(f"Review Correction for {teacher}")

        # Rating sliders for teaching, leniency, and correction (Range: 1-10)
        teaching_rating = st.slider(f"Rating for Teaching for {teacher}", 1, 10, 5)
        leniency_rating = st.slider(f"Rating for Leniency for {teacher}", 1, 10, 5)
        correction_rating = st.slider(f"Rating for Correction for {teacher}", 1, 10, 5)
        
        # Store the reviews and ratings in session state (for the session)
        if teaching_review and leniency_review and correction_review:
            st.session_state.reviews[teacher] = {
                'teaching_review': teaching_review,
                'leniency_review': leniency_review,
                'correction_review': correction_review,
                'teaching_rating': teaching_rating,
                'leniency_rating': leniency_rating,
                'correction_rating': correction_rating
            }

# Display reviews and ratings (if there are any reviews in the session state)
if 'reviews' in st.session_state:
    st.header("Current Reviews")
    for teacher, review_data in st.session_state.reviews.items():
        st.write(f"Reviews for {teacher}:")
        st.write(f"Teaching: {review_data['teaching_review']} (Rating: {review_data['teaching_rating']}/10)")
        st.write(f"Leniency: {review_data['leniency_review']} (Rating: {review_data['leniency_rating']}/10)")
        st.write(f"Correction: {review_data['correction_review']} (Rating: {review_data['correction_rating']}/10)")
else:
    st.write("No reviews yet.")
