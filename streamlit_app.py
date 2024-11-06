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

# Read ratings from CSV file
def load_ratings():
    try:
        ratings_df = pd.read_csv('ratings.csv', index_col=0)
    except FileNotFoundError:
        ratings_df = pd.DataFrame(columns=['teacher', 'teaching_rating', 'leniency_rating', 'correction_rating', 'teaching_votes', 'leniency_votes', 'correction_votes'])
    return ratings_df

# Save ratings to CSV file
def save_ratings(ratings_df):
    ratings_df.to_csv('ratings.csv')

# Load teachers data from SCOPE.txt
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher) for teacher in teachers]

# Load existing ratings from the CSV file
ratings_df = load_ratings()

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Leave a Rating for Teaching, Leniency, and Correction (Out of 10)")

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
    
    # Let the user rate each teacher
    for teacher in matches:
        st.subheader(f"Rate {teacher}:")

        # Rating sliders for teaching, leniency, and correction (Range: 1-10)
        teaching_rating = st.slider(f"Rating for Teaching for {teacher}", 1, 10, 5)
        leniency_rating = st.slider(f"Rating for Leniency for {teacher}", 1, 10, 5)
        correction_rating = st.slider(f"Rating for Correction for {teacher}", 1, 10, 5)
        
        # Store the ratings in the DataFrame (update existing or add new)
        if st.button(f"Submit Rating for {teacher}"):
            # Check if teacher already has a rating entry
            teacher_cleaned = clean_name(teacher)
            existing_entry = ratings_df[ratings_df['teacher'] == teacher_cleaned]
            if not existing_entry.empty:
                # Update existing rating and vote count
                ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'teaching_rating'] = (ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'teaching_rating'] * ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'teaching_votes'] + teaching_rating) / (ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'teaching_votes'] + 1)
                ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'leniency_rating'] = (ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'leniency_rating'] * ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'leniency_votes'] + leniency_rating) / (ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'leniency_votes'] + 1)
                ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'correction_rating'] = (ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'correction_rating'] * ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'correction_votes'] + correction_rating) / (ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'correction_votes'] + 1)
                
                # Increment vote counts
                ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'teaching_votes'] += 1
                ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'leniency_votes'] += 1
                ratings_df.loc[ratings_df['teacher'] == teacher_cleaned, 'correction_votes'] += 1
            else:
                # Add new rating entry with vote counts as 1
                new_row = {
                    'teacher': teacher_cleaned,
                    'teaching_rating': teaching_rating,
                    'leniency_rating': leniency_rating,
                    'correction_rating': correction_rating,
                    'teaching_votes': 1,
                    'leniency_votes': 1,
                    'correction_votes': 1
                }
                ratings_df = ratings_df.append(new_row, ignore_index=True)
            
            # Save the updated ratings to CSV
            save_ratings(ratings_df)

# Display the current ratings and vote count from the CSV file
st.header("Current Ratings")
if not ratings_df.empty:
    for _, row in ratings_df.iterrows():
        st.write(f"Ratings for {row['teacher']}:")
        st.write(f"Teaching: {row['teaching_rating']}/10 (Votes: {row['teaching_votes']})")
        st.write(f"Leniency: {row['leniency_rating']}/10 (Votes: {row['leniency_votes']})")
        st.write(f"Correction: {row['correction_rating']}/10 (Votes: {row['correction_votes']})")
else:
    st.write("No ratings yet.")
