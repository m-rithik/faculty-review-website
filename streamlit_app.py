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

            # Input new ratings
            teaching = st.slider("Teaching:", 0, 10, st.session_state.reviews[teacher]['teaching'])
            leniency = st.slider("Leniency:", 0, 10, st.session_state.reviews[teacher]['leniency'])
            correction = st.slider("Correction:", 0, 10, st.session_state.reviews[teacher]['correction'])
            da_quiz = st.slider("DA/Quiz:", 0, 10, st.session_state.reviews[teacher]['da_quiz'])

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

            # Display the teacher's image
            with col2:
                try:
                    st.image(image_url, caption=f"{teacher}'s Picture", width=150)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")

        # Display reviews section
        if st.session_state.total_reviews[teacher] > 0:
            st.markdown("### **REVIEWS**")  # Heading for Reviews
            st.write("**Teaching:**", f"{st.session_state.reviews[teacher]['teaching']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['teaching'] > 5 else 'red' if st.session_state.reviews[teacher]['teaching'] < 5 else 'yellow'};")
            st.write("**Leniency:**", f"{st.session_state.reviews[teacher]['leniency']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['leniency'] > 5 else 'red' if st.session_state.reviews[teacher]['leniency'] < 5 else 'yellow'};")
            st.write("**Correction:**", f"{st.session_state.reviews[teacher]['correction']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['correction'] > 5 else 'red' if st.session_state.reviews[teacher]['correction'] < 5 else 'yellow'};")
            st.write("**DA/Quiz:**", f"{st.session_state.reviews[teacher]['da_quiz']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['da_quiz'] > 5 else 'red' if st.session_state.reviews[teacher]['da_quiz'] < 5 else 'yellow'};")

            # Overall rating (below the teacher's image)
            st.markdown("### **Overall Rating**")
            overall_rating = st.session_state.reviews[teacher]['overall']
            st.write(f"{overall_rating:.1f} / 10", style=f"color:{'green' if overall_rating > 5 else 'red' if overall_rating < 5 else 'yellow'};")
            st.progress(overall_rating / 10)  # Display as progress bar (scaled to 10)

        # Submit button to save the review
        if st.button("Submit Review"):
            st.success("Review submitted successfully!")
            st.markdown(f"Overall Rating: {overall_rating:.1f} / 10")
            st.progress(overall_rating / 10)  # Display as progress bar (scaled to 10)

else:
    st.write("No teachers found.")
