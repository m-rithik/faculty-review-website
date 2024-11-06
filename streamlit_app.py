import streamlit as st
import pandas as pd
import re
import os

# Function to read teacher names and image URLs from the text file
def load_teachers(file):
    teachers = []
    with open(file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            # Assuming the format is: Name: [name] URL: [image_url]
            parts = line.strip().split(' Image: ')
            if len(parts) == 2:
                teachers.append((parts[0].replace('Name: ', ''), parts[1]))  # Removing 'Name: ' and keeping name
    return teachers

# Clean teacher names for search comparison
def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())

# Function to load ratings from CSV file (from GitHub URL)
def load_ratings():
    file_path = 'ratings.csv'

    # Check if the file exists
    if not os.path.exists(file_path):
        # If file doesn't exist, create an empty DataFrame with headers
        ratings_df = pd.DataFrame(columns=[
            'teacher_name', 'leniency_rating', 'teaching_rating', 'correction_rating', 'da_quiz_rating', 'overall_rating'
        ])
        ratings_df.to_csv(file_path, index=False)  # Create an empty file with headers
        return ratings_df

    # If file exists, try to load it
    try:
        ratings_df = pd.read_csv(file_path)
        if ratings_df.empty:  # If the file is empty
            ratings_df = pd.DataFrame(columns=[
                'teacher_name', 'leniency_rating', 'teaching_rating', 'correction_rating', 'da_quiz_rating', 'overall_rating'
            ])
            ratings_df.to_csv(file_path, index=False)  # Ensure the empty file has headers
        return ratings_df
    except pd.errors.EmptyDataError:
        # Handle the case when CSV is empty
        ratings_df = pd.DataFrame(columns=[
            'teacher_name', 'leniency_rating', 'teaching_rating', 'correction_rating', 'da_quiz_rating', 'overall_rating'
        ])
        ratings_df.to_csv(file_path, index=False)  # Create an empty file with headers
        return ratings_df

# Function to save ratings back to CSV (after update)
def save_ratings(ratings_df):
    ratings_df.to_csv('ratings.csv', index=False)

# Load teachers data
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Load ratings from the CSV file
ratings_df = load_ratings()

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Leave a Review for Teaching, Leniency, Correction, and DA/Quiz (Out of 10)")

# Search bar (case insensitive and ignore titles like Dr, Mr, Ms)
search_query = st.text_input("Search for a teacher:")

# Display all teachers if no search query is provided
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

            # Get past ratings for the teacher (if available)
            teacher_rating_data = ratings_df[ratings_df['teacher_name'] == teacher].iloc[0] if teacher in ratings_df['teacher_name'].values else None
            teaching_rating = teacher_rating_data['teaching_rating'] if teacher_rating_data is not None else 5
            leniency_rating = teacher_rating_data['leniency_rating'] if teacher_rating_data is not None else 5
            correction_rating = teacher_rating_data['correction_rating'] if teacher_rating_data is not None else 5
            da_quiz_rating = teacher_rating_data['da_quiz_rating'] if teacher_rating_data is not None else 5
            overall_rating = teacher_rating_data['overall_rating'] if teacher_rating_data is not None else 3

            # Rating sliders for teaching, leniency, correction, and DA/Quiz (Range: 1-10)
            teaching_rating = st.slider(f"Rating for Teaching for {teacher}", 1, 10, teaching_rating)
            leniency_rating = st.slider(f"Rating for Leniency for {teacher}", 1, 10, leniency_rating)
            correction_rating = st.slider(f"Rating for Correction for {teacher}", 1, 10, correction_rating)
            da_quiz_rating = st.slider(f"Rating for DA/Quiz for {teacher}", 1, 10, da_quiz_rating)

            # Calculate overall rating as an average of all individual ratings
            overall_rating = (teaching_rating + leniency_rating + correction_rating + da_quiz_rating) / 4
            overall_rating = round(overall_rating, 2)

            # Update the ratings in the dataframe
            if teacher not in ratings_df['teacher_name'].values:
                ratings_df = ratings_df.append({
                    'teacher_name': teacher,
                    'leniency_rating': leniency_rating,
                    'teaching_rating': teaching_rating,
                    'correction_rating': correction_rating,
                    'da_quiz_rating': da_quiz_rating,
                    'overall_rating': overall_rating
                }, ignore_index=True)
            else:
                ratings_df.loc[ratings_df['teacher_name'] == teacher, [
                    'leniency_rating', 'teaching_rating', 'correction_rating', 'da_quiz_rating', 'overall_rating']] = [
                    leniency_rating, teaching_rating, correction_rating, da_quiz_rating, overall_rating]

            # Save the updated ratings to CSV
            save_ratings(ratings_df)

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
