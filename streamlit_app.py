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

# Create a session state to store the reviews
if 'reviews' not in st.session_state:
    st.session_state.reviews = {}

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher, image_url in matches:
        col1, col2 = st.columns([2, 1])  # Create two columns: one for the name, one for the image

        with col1:
            st.subheader(f"Teacher: {teacher}")

            # Review inputs for ratings (Teaching, Leniency, Correction, DA/Quiz)
            teaching_rating = st.slider(f"Teaching Rating for {teacher}", 1, 10, 5)
            leniency_rating = st.slider(f"Leniency Rating for {teacher}", 1, 10, 5)
            correction_rating = st.slider(f"Correction Rating for {teacher}", 1, 10, 5)
            da_quiz_rating = st.slider(f"DA/Quiz Rating for {teacher}", 1, 10, 5)

            # Overall rating calculation (average of all ratings)
            overall_rating = (teaching_rating + leniency_rating + correction_rating + da_quiz_rating) / 4
            overall_rating = round(overall_rating, 2)

            # Submit button for saving reviews
            if st.button(f"Submit Review for {teacher}"):
                # Save the ratings in session state
                st.session_state.reviews[teacher] = {
                    'teaching': teaching_rating,
                    'leniency': leniency_rating,
                    'correction': correction_rating,
                    'da_quiz': da_quiz_rating,
                    'overall': overall_rating
                }
                st.success(f"Review for {teacher} submitted successfully!")

            # Display the overall rating as a progress bar
            st.markdown(f"Overall Rating: {overall_rating} / 10")
            st.progress(overall_rating / 10)  # Display as progress bar (scaled to 10)

        with col2:
            # Display the teacher's image
            try:
                st.image(image_url, caption=f"{teacher}'s Picture", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {e}")

        # Show the stored reviews for this teacher if already reviewed
        if teacher in st.session_state.reviews:
            review = st.session_state.reviews[teacher]
            st.write(f"Previous Review for {teacher}:")
            st.write(f"Teaching: {review['teaching']} / 10")
            st.write(f"Leniency: {review['leniency']} / 10")
            st.write(f"Correction: {review['correction']} / 10")
            st.write(f"DA/Quiz: {review['da_quiz']} / 10")
            st.write(f"Overall: {review['overall']} / 10")

else:
    st.write("No teachers found.")
