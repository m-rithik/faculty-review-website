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
    st.session_state.votes = {}

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher, image_url in matches:
        col1, col2 = st.columns([2, 1])  # Create two columns: one for the name, one for the image

        with col1:
            st.subheader(f"Teacher: {teacher}")

            # Display previous ratings if available
            if teacher in st.session_state.reviews:
                review = st.session_state.reviews[teacher]
                st.write(f"Previous Review for {teacher}:")
                st.write(f"Teaching: {review['teaching']} / {st.session_state.votes[teacher]['teaching']} votes")
                st.write(f"Leniency: {review['leniency']} / {st.session_state.votes[teacher]['leniency']} votes")
                st.write(f"Correction: {review['correction']} / {st.session_state.votes[teacher]['correction']} votes")
                st.write(f"DA/Quiz: {review['da_quiz']} / {st.session_state.votes[teacher]['da_quiz']} votes")
                st.write(f"Overall: {review['overall']} / 10 (based on {sum(st.session_state.votes[teacher].values())} votes)")

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
                # Save the ratings in session state if not already saved
                if teacher not in st.session_state.reviews:
                    st.session_state.reviews[teacher] = {
                        'teaching': 0,
                        'leniency': 0,
                        'correction': 0,
                        'da_quiz': 0,
                        'overall': 0
                    }
                    st.session_state.votes[teacher] = {
                        'teaching': 0,
                        'leniency': 0,
                        'correction': 0,
                        'da_quiz': 0
                    }

                # Update the review ratings and increment votes
                st.session_state.reviews[teacher]['teaching'] += teaching_rating
                st.session_state.reviews[teacher]['leniency'] += leniency_rating
                st.session_state.reviews[teacher]['correction'] += correction_rating
                st.session_state.reviews[teacher]['da_quiz'] += da_quiz_rating

                # Increment the vote counts
                st.session_state.votes[teacher]['teaching'] += 1
                st.session_state.votes[teacher]['leniency'] += 1
                st.session_state.votes[teacher]['correction'] += 1
                st.session_state.votes[teacher]['da_quiz'] += 1

                # Update the overall rating
                st.session_state.reviews[teacher]['overall'] = (
                    (st.session_state.reviews[teacher]['teaching'] +
                     st.session_state.reviews[teacher]['leniency'] +
                     st.session_state.reviews[teacher]['correction'] +
                     st.session_state.reviews[teacher]['da_quiz']) /
                    (st.session_state.votes[teacher]['teaching'] +
                     st.session_state.votes[teacher]['leniency'] +
                     st.session_state.votes[teacher]['correction'] +
                     st.session_state.votes[teacher]['da_quiz'])
                )
                st.session_state.reviews[teacher]['overall'] = round(st.session_state.reviews[teacher]['overall'], 2)
                
                st.success(f"Review for {teacher} submitted successfully!")

            # Display the overall rating as a progress bar
            st.markdown(f"Overall Rating: {st.session_state.reviews[teacher]['overall']} / 10")
            st.progress(st.session_state.reviews[teacher]['overall'] / 10)  # Display as progress bar (scaled to 10)

            # Display the number of votes for each category
            st.write(f"Votes for Teaching: {st.session_state.votes[teacher]['teaching']}")
            st.write(f"Votes for Leniency: {st.session_state.votes[teacher]['leniency']}")
            st.write(f"Votes for Correction: {st.session_state.votes[teacher]['correction']}")
            st.write(f"Votes for DA/Quiz: {st.session_state.votes[teacher]['da_quiz']}")

        with col2:
            # Display the teacher's image
            try:
                st.image(image_url, caption=f"{teacher}'s Picture", use_column_width=True)
            except Exception as e:
                st.error(f"Error displaying image: {e}")
else:
    st.write("No teachers found.")
