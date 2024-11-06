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

# Function to load ratings from CSV file (from GitHub URL)
def load_ratings():
    # URL to your raw CSV file on GitHub
    csv_url = 'https://raw.githubusercontent.com/m-rithik/facrev-app/refs/heads/main/ratings.csv'  # Change this URL
    try:
        ratings_df = pd.read_csv(csv_url, index_col=0)
    except Exception as e:
        st.error(f"Error loading ratings CSV: {e}")
        ratings_df = pd.DataFrame()
    return ratings_df

# Function to save ratings back to CSV (after update)
def save_ratings(ratings_df):
    ratings_df.to_csv('ratings.csv')

# Load teachers data
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Load ratings from the CSV file
ratings_df = load_ratings()

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Leave a Review for Teaching, Leniency, and Correction (Out of 10)")

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
            st.subheader(f"Leave a review for {teacher}:")
            
            # Rating sliders for teaching, leniency, and correction (Range: 1-10)
            teaching_rating = st.slider(f"Rating for Teaching for {teacher}", 1, 10, 5)
            leniency_rating = st.slider(f"Rating for Leniency for {teacher}", 1, 10, 5)
            correction_rating = st.slider(f"Rating for Correction for {teacher}", 1, 10, 5)

            # Update the ratings in the dataframe
            if teacher not in ratings_df.index:
                # If teacher not in ratings_df, initialize their ratings with 0 votes
                ratings_df.loc[teacher] = [0, 0, 0, 0, 0, 0]

            # Update the ratings and the number of votes
            current_teaching_ratings = ratings_df.at[teacher, 'teaching_rating']
            current_leniency_ratings = ratings_df.at[teacher, 'leniency_rating']
            current_correction_ratings = ratings_df.at[teacher, 'correction_rating']

            current_teaching_votes = ratings_df.at[teacher, 'teaching_votes']
            current_leniency_votes = ratings_df.at[teacher, 'leniency_votes']
            current_correction_votes = ratings_df.at[teacher, 'correction_votes']

            # Update ratings and increment vote counts
            new_teaching_avg = (current_teaching_ratings * current_teaching_votes + teaching_rating) / (current_teaching_votes + 1)
            new_leniency_avg = (current_leniency_ratings * current_leniency_votes + leniency_rating) / (current_leniency_votes + 1)
            new_correction_avg = (current_correction_ratings * current_correction_votes + correction_rating) / (current_correction_votes + 1)

            # Increment vote counts
            ratings_df.at[teacher, 'teaching_rating'] = new_teaching_avg
            ratings_df.at[teacher, 'leniency_rating'] = new_leniency_avg
            ratings_df.at[teacher, 'correction_rating'] = new_correction_avg

            ratings_df.at[teacher, 'teaching_votes'] = current_teaching_votes + 1
            ratings_df.at[teacher, 'leniency_votes'] = current_leniency_votes + 1
            ratings_df.at[teacher, 'correction_votes'] = current_correction_votes + 1

            # Save ratings after updating
            save_ratings(ratings_df)

            # Show current ratings and vote count
            st.write(f"Current Ratings (Out of 10):")
            st.write(f"Teaching: {ratings_df.at[teacher, 'teaching_rating']} (Votes: {ratings_df.at[teacher, 'teaching_votes']})")
            st.write(f"Leniency: {ratings_df.at[teacher, 'leniency_rating']} (Votes: {ratings_df.at[teacher, 'leniency_votes']})")
            st.write(f"Correction: {ratings_df.at[teacher, 'correction_rating']} (Votes: {ratings_df.at[teacher, 'correction_votes']})")

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
