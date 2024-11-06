import streamlit as st
import pandas as pd
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

# Function to load ratings from the CSV file
def load_ratings():
    try:
        ratings_df = pd.read_csv('ratings.csv', index_col=0)
    except FileNotFoundError:
        # If file doesn't exist, create an empty DataFrame
        ratings_df = pd.DataFrame(columns=['leniency_rating', 'teaching_rating', 'correction_rating', 'da_quiz_rating', 'overall_rating'])
    return ratings_df

# Function to save ratings to the CSV file
def save_ratings(ratings_df):
    ratings_df.to_csv('ratings.csv')

# Load teachers data
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Load ratings data
ratings_df = load_ratings()

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
    matches = []

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher, image_url in matches:
        col1, col2 = st.columns([2, 1])  # Create two columns: one for the name, one for the image

        with col1:
            st.subheader(f"Teacher: {teacher}")

            # Rating sliders for leniency, teaching, correction, DA/Quiz
            leniency_rating = st.slider(f"Leniency Rating for {teacher}", 1, 10, 5)
            teaching_rating = st.slider(f"Teaching Rating for {teacher}", 1, 10, 5)
            correction_rating = st.slider(f"Correction Rating for {teacher}", 1, 10, 5)
            da_quiz_rating = st.slider(f"DA/Quiz Rating for {teacher}", 1, 10, 5)

            # Calculate the overall rating as the average of the four ratings
            overall_rating = (leniency_rating + teaching_rating + correction_rating + da_quiz_rating) / 4
            overall_star_rating = (overall_rating / 2)  # Convert to a 0-5 scale for the stars

            # Update ratings in the dataframe
            if teacher not in ratings_df.index:
                ratings_df.loc[teacher] = [0, 0, 0, 0, 0]  # Initialize ratings if teacher not in DataFrame

            # Save the ratings to the dataframe
            ratings_df.at[teacher, 'leniency_rating'] = leniency_rating
            ratings_df.at[teacher, 'teaching_rating'] = teaching_rating
            ratings_df.at[teacher, 'correction_rating'] = correction_rating
            ratings_df.at[teacher, 'da_quiz_rating'] = da_quiz_rating
            ratings_df.at[teacher, 'overall_rating'] = overall_rating

            # Save the ratings back to the CSV
            save_ratings(ratings_df)

            # Display the overall star rating with color coding
            color = "red" if overall_star_rating <= 1 else "orange" if overall_star_rating <= 2 else "yellow" if overall_star_rating <= 3 else "lightgreen" if overall_star_rating <= 4 else "green"
            st.markdown(f'<h3 style="color:{color}">Overall Rating: {overall_star_rating} / 5 ⭐</h3>', unsafe_allow_html=True)

        with col2:
            # Display the teacher's image
            try:
                st.image(image_url, caption=f"{teacher}'s Picture", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {e}")

else:
    st.write("No teachers found.")
