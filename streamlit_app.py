import streamlit as st
import re

# Function to read teacher names and image URLs from the text file
def load_teachers(file):
    teachers = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Assuming the format is: Name: [name] Image: [image_url]
            parts = line.strip().split(' Image: ')
            if len(parts) == 2:
                teachers.append((parts[0].replace('Name: ', ''), parts[1]))
    return teachers

# Clean teacher names for search comparison
def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())

# Load teachers data
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Leave a Review for Teaching, Leniency, Correction, and DA/Quiz (Out of 10)")

# Search bar (case insensitive and ignore titles like Dr, Mr, Ms)
search_query = st.text_input("Search for a teacher:")

# Find matching teachers based on the search query
if search_query:
    search_query_cleaned = clean_name(search_query)
    matches = [teachers[i] for i in range(len(teachers_cleaned)) if search_query_cleaned in teachers_cleaned[i]]
else:
    matches = teachers  # If no search, show all teachers

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher, image_url in matches:
        col1, col2 = st.columns([2, 1])  # Create two columns: one for the name, one for the image

        with col1:
            st.subheader(f"Leave a review for {teacher}:")

            # Rating sliders for teaching, leniency, correction, and DA/Quiz (Range: 1-10)
            teaching_rating = st.slider(f"Rating for Teaching for {teacher}", 1, 10, 5)
            leniency_rating = st.slider(f"Rating for Leniency for {teacher}", 1, 10, 5)
            correction_rating = st.slider(f"Rating for Correction for {teacher}", 1, 10, 5)
            da_quiz_rating = st.slider(f"Rating for DA/Quiz for {teacher}", 1, 10, 5)

            # Calculate overall rating as an average of all individual ratings
            overall_rating = (teaching_rating + leniency_rating + correction_rating + da_quiz_rating) / 4
            overall_rating = round(overall_rating, 2)

            # Display the updated ratings
            st.write(f"Current Ratings (Out of 10):")
            st.write(f"Teaching: {teaching_rating}")
            st.write(f"Leniency: {leniency_rating}")
            st.write(f"Correction: {correction_rating}")
            st.write(f"DA/Quiz: {da_quiz_rating}")

            # Display overall rating as a colored star
            st.markdown(f"Overall Rating: {overall_rating} / 5")
            st.progress(overall_rating / 5)  # Display as progress bar (scaled to 5)

        with col2:
            # Display the teacher's image
            st.image(image_url, caption=f"{teacher}'s Picture", use_column_width=True)

else:
    st.write("No teachers found or no matching results.")
