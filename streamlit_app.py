import streamlit as st
import re
import csv
import os

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

# Function to load saved reviews from CSV
def load_reviews():
    reviews = {}
    if os.path.exists('ratings.csv'):
        with open('ratings.csv', mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row:  # Skip empty rows
                    teacher_name = row[0]
                    teaching, leniency, correction, da_quiz = map(int, row[1:5])
                    if teacher_name not in reviews:
                        reviews[teacher_name] = {'ratings': [], 'overall': 0}
                    reviews[teacher_name]['ratings'].append((teaching, leniency, correction, da_quiz))
                    reviews[teacher_name]['overall'] = calculate_overall_rating(reviews[teacher_name]['ratings'])
    return reviews

# Function to save reviews to CSV
def save_reviews():
    with open('ratings.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for teacher_name, data in st.session_state.reviews.items():
            for rating in data['ratings']:
                writer.writerow([teacher_name] + list(rating))

# Function to calculate overall rating (based on existing ratings)
def calculate_overall_rating(ratings):
    total_rating = sum([sum(rating) for rating in ratings])
    return total_rating / (len(ratings) * 4) if ratings else 0

# Load reviews into session state
if 'reviews' not in st.session_state:
    st.session_state.reviews = load_reviews()

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
                    'ratings': [],  # Store all individual ratings as a list of tuples (teaching, leniency, correction, da_quiz)
                    'overall': 0     # Overall rating
                }

            # User input section (ratings for the teacher)
            st.markdown("### **Rate the Teacher**")
            teaching = st.slider("Teaching:", 0, 10)
            leniency = st.slider("Leniency:", 0, 10)
            correction = st.slider("Correction:", 0, 10)
            da_quiz = st.slider("DA/Quiz:", 0, 10)

            # Display the teacher's image in a smaller size
            with col2:
                try:
                    st.image(image_url, caption=f"{teacher}'s Picture", width=150)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")

            # Submit button to save the review
            submit_button = st.button("Submit Review")
            
            if submit_button:
                # Save the ratings in session state
                st.session_state.reviews[teacher]['ratings'].append((teaching, leniency, correction, da_quiz))
                
                # Calculate the overall rating
                overall_rating = calculate_overall_rating(st.session_state.reviews[teacher]['ratings'])
                st.session_state.reviews[teacher]['overall'] = overall_rating
                
                # Save the updated reviews to the CSV file
                save_reviews()
                
                # Display success message
                st.success("Review submitted successfully!")

        # Section 2: Overall Rating and Previous Reviews
        if st.session_state.reviews[teacher]['ratings']:
            st.markdown("---")
            st.markdown("### **Overall Rating**")
            
            # Calculate average overall rating (without approximating)
            overall_rating = st.session_state.reviews[teacher]['overall']
            
            # Display the overall rating in the overall rating box
            st.markdown(f"**Overall Rating (based on {len(st.session_state.reviews[teacher]['ratings'])} reviews):**")
            st.markdown(f"{overall_rating:.2f} / 10", unsafe_allow_html=True)  # Display on 10-point scale
            
            # Display reviews and their individual ratings
            st.markdown("### **REVIEWS**")
            for idx, rating in enumerate(st.session_state.reviews[teacher]['ratings']):
                st.write(f"**Review {idx + 1}:**")
                st.write(f"Teaching: {rating[0]}/10, Leniency: {rating[1]}/10, Correction: {rating[2]}/10, DA/Quiz: {rating[3]}/10")

else:
    st.write("No teachers found.")
