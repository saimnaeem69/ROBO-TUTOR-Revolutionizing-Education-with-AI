from PIL import Image, ImageDraw
import streamlit as st
import speech_recognition as sr
import pyttsx3
import openai
import fitz  # PyMuPDF
import os
import time
import json

def get_speech_input(language="en-US"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            recognized_text = recognizer.recognize_google(audio, language=language)
            return recognized_text
        except sr.WaitTimeoutError:
            st.write('Timeout: No speech detected.')
        except sr.UnknownValueError:
            st.write("Sorry, didn't get that.")
        except sr.RequestError:
            st.write('Sorry, speech recognition service is currently unavailable.')
        return None

def speak(reply):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Set the voice to Microsoft Zira (female)
    for voice in voices:
        if voice.name == 'Microsoft Zira Desktop - English (United States)':
            engine.setProperty('voice', voice.id)
            break
    engine.say(reply)
    engine.runAndWait()

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Securely load OpenAI API key from environment variable
openai.api_key = "sk-proj-bhkYYCoV8CV1zeNapLbST3BlbkFJTLxGRk4SGbpKI2U1gXBI"
model_name = "gpt-3.5-turbo"
messages = []

st.set_page_config(page_title="ROBO TUTOR", layout="wide")

# Centering the title using HTML and CSS
st.markdown("""
    <div style="display: flex; justify-content: center;">
        <h1>ROBO TUTOR</h1>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")
# Function to load and resize image
def load_and_resize_image(image_path, size):
    image = Image.open(image_path)
    image = image.resize(size, Image.LANCZOS)
    return image

# Function to create circular icons
def create_circular_icon(image):
    width, height = image.size
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, width, height), fill=255)
    result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    result.paste(image, (0, 0), mask=mask)
    return result

# Set the desired size for the icons
icon_size = (300, 300)

# Load and resize icon images
power_electronics_img = load_and_resize_image("Power Electronics.png", icon_size)
chemistry_img = load_and_resize_image("Chemistry.png", icon_size)
dld_img = load_and_resize_image("Digital Logic Design.png", icon_size)
history_img = load_and_resize_image("Human.png", icon_size)

# Create circular icons
power_electronics_img = create_circular_icon(power_electronics_img)
chemistry_img = create_circular_icon(chemistry_img)
dld_img = create_circular_icon(dld_img)
history_img = create_circular_icon(history_img)

# Display buttons with icons and style
col1, col2, col3, col4 = st.columns(4)

# Initialize st.session_state.role if it doesn't exist
if "role" not in st.session_state:
    st.session_state.role = None

button_style = """
    <style>
    .stButton button {
        background-color: #9370DB;
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: 4px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        transition-duration: 0.4s;
    }
    .stButton button:hover {
        background-color: #E6E6FA;
        color: black;
        border: 2px solid #9370DB;
    }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)

if col1.button("Power Electronics", key="PE"):
    st.session_state.role = "Power Electronics"
col1.image(power_electronics_img, use_column_width=True)

if col2.button("Chemistry", key="Chemistry"):
    st.session_state.role = "Chemistry"
col2.image(chemistry_img, use_column_width=True)

if col3.button("Digital Logic Design", key="DLD"):
    st.session_state.role = "Digital Logic Design"
col3.image(dld_img, use_column_width=True)

if col4.button("Machine Learning", key="Machine Learning"):
    st.session_state.role = "Machine Learning"
col4.image(history_img, use_column_width=True)

# Initialize selected_role
selected_role = None

# Check the selected role
if st.session_state.role == "Power Electronics":
    assistant_name = "Vania"
    prompt = '''Scenario: Power Electronics Q&A Role-Play

Role: You are Vania, a Power Electronics Teacher.

Instructions:

The user is a student asking questions specifically related to Power Electronics.
You will respond to the student's questions.
Each answer should be summarized in a complete sentence of no more than 35 words.
Answer only the queries related to Power Electronics.
Begin the role-play'''
    messages.append({"role": "system", "content": prompt})
    selected_role = "Power Electronics"

elif st.session_state.role == "Chemistry":
    assistant_name = "Vaniza"
    prompt = '''Scenario: Chemistry Q&A Role-Play

Role: You are Vaniza, a Chemistry Teacher.

Instructions:

The user is a student asking questions specifically related to Chemistry.
You will respond to the student's questions.
Each answer should be summarized in a complete sentence of no more than 35 words.
Answer only the queries related to Chemistry.
Begin the role-play'''
    messages.append({"role": "system", "content": prompt})
    selected_role = "Chemistry"

elif st.session_state.role == "Digital Logic Design":
    assistant_name = "Abeerah"
    prompt = '''Scenario: Digital Logic Design Q&A Role-Play

Role: You are Abeerah, a Digital Logic Design Teacher.

Instructions:

The user is a student asking questions specifically related to Digital Logic Design.
You will respond to the student's questions.
Each answer should be summarized in a complete sentence of no more than 35 words.
Answer only the queries related to Digital Logic Design.
Begin the role-play.'''
    messages.append({"role": "system", "content": prompt})
    selected_role = "Digital Logic Design"

elif st.session_state.role == "Machine Learning":
    assistant_name = "Ayesha"
    prompt = '''Scenario: Machine Learning Q&A Role-Play

Role: You are Ayesha, a Machine Learning Teacher.

Instructions:

The user is a student asking questions specifically related to Machine Learning.
You will respond to the student's questions.
Each answer should be summarized in a complete sentence of no more than 35 words.
Answer only the queries related to Machine Learning.
Begin the role-play.'''
    messages.append({"role": "system", "content": prompt})
    selected_role = "Machine Learning"

else:
    st.text("Invalid role selected.")

# Display selected subject
if selected_role:
    st.markdown(f"<h3 style='text-align: center; color: #9370DB;'>Selected Role: {selected_role}</h3>", unsafe_allow_html=True)

def save_message(role, content):
    with open("conversation_history.txt", "a", encoding="utf-8") as file:
        file.write(f"{role}: {content}\n")

def load_conversation():
    try:
        with open("conversation_history.txt", "r") as file:
            return file.read()
    except FileNotFoundError:
        return "No saved conversation found."

def continue_conversation():
    conversation_placeholder = st.empty()
    progress_placeholder = st.empty()
    while True:
        conversation_placeholder.text("Listening...")
        user_input = get_speech_input()
        conversation_placeholder.empty()

        if user_input and user_input.lower() in ['bye', 'goodbye', 'stop','thank you']:
            st.text('Stopping conversation...')
            speak('Stopping conversation...')
            st.session_state.role = None
            messages.clear()
            break
        elif user_input:
            messages.append({"role": "user", "content": user_input})
            save_message("User", user_input)
            conversation_placeholder.text(f"User: {user_input}")

            # Show a single loading bar
            with progress_placeholder:
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01)  # Simulate a delay for loading
                    progress_bar.progress(percent_complete + 1)

            # Use the OpenAI API to generate a response
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )

            # Extract the assistant's reply from the API response
            reply = response['choices'][0]['message']['content'].strip()
            conversation_placeholder.text(f"User: {user_input}\n\n{assistant_name.capitalize()}: {reply}")
            messages.append({"role": "assistant", "content": reply})
            save_message(assistant_name, reply)

            # Speak the assistant's reply
            speak(reply)

def continue_pdf_conversation(pdf_text):
    conversation_placeholder = st.empty()
    progress_placeholder = st.empty()
    while True:
        conversation_placeholder.text("Listening...")
        user_input = get_speech_input()
        conversation_placeholder.empty()
        if user_input and user_input.lower() in ['bye', 'goodbye', 'stop']:
            st.text('Stopping conversation...')
            speak('Stopping conversation...')
            messages.clear()
            break
        elif user_input:
            messages.append({"role": "user", "content": user_input})
            save_message("User", user_input)
            conversation_placeholder.text(f"User: {user_input}")
            
            # Show a single loading bar
            with progress_placeholder:
                progress_bar = st.progress(0)
                for percent_complete in range(100):
                    time.sleep(0.01)  # Simulate a delay for loading
                    progress_bar.progress(percent_complete + 1)
            
            # Use the OpenAI API to generate a response
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Answer questions exclusively based on the content of the uploaded file. If the answer is not found in the file, clearly state that the information is not available. Provide answers in 40 words maximum."},
                    {"role": "user", "content": pdf_text},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150,
                temperature=0.7,
            )
            reply = response['choices'][0]['message']['content'].strip()
            conversation_placeholder.text(f"User: {user_input}\n\nAssistant: {reply}")
            messages.append({"role": "assistant", "content": reply})
            save_message("Assistant", reply)
            speak(reply)

# Start the conversation loop
if st.button("Start Conversation"):
    continue_conversation()

# View previous conversation
if st.button("View Previous Conversation"):
    st.text(load_conversation())

# File upload with style
st.markdown("---")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
pdf_text = ""
if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.text("PDF content successfully extracted. You can now ask questions about the content.")

if pdf_text:
    if st.button("Start PDF Conversation"):
        continue_pdf_conversation(pdf_text)
st.markdown("## Quiz")
# Function to generate quiz questions
import streamlit as st
import openai

# Function to generate quiz questions
def generate_quiz(selected_role):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Generate 3 multiple-choice quiz questions (MCQs) related to the role of a {selected_role}. Ensure that each question is unique and covers different aspects of the {selected_role}. Do not include the correct answers in the prompt."}
        ],
        max_tokens=200,
        temperature=0.7,
    )
    quiz_content = response['choices'][0]['message']['content'].strip()
    return quiz_content

# Function to generate the correct answers separately
def generate_correct_answers(questions):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Provide the correct answers for the following questions:\n\n{questions}"}
        ],
        max_tokens=100,
        temperature=0.7,
    )
    answers = response['choices'][0]['message']['content'].strip()
    return answers

# Function to display the quiz with correct answers
def display_quiz_with_answers(quiz_content, correct_answers):
    questions = quiz_content.split("\n\n")
    correct_answers_list = correct_answers.split("\n")

    for i, question in enumerate(questions):
        st.markdown(f"### Question {i+1}")
        lines = question.split("\n")
        st.markdown(lines[0])
        options = lines[1:]

        for option in options:
            st.markdown(option)

        if i < len(correct_answers_list):
            st.markdown(f"**Correct answer: {correct_answers_list[i]}**")

# Generate and display quiz
if st.button("Generate Quiz", key="generate_quiz"):
    if selected_role:
        quiz_content = generate_quiz(selected_role)
        correct_answers_text = generate_correct_answers(quiz_content)
        st.session_state.quiz_content = quiz_content
        st.session_state.correct_answers = correct_answers_text

        st.session_state.quiz_active = True
    else:
        st.warning("Please enter a role first.")

# Display the quiz with correct answers if it is active
if 'quiz_content' in st.session_state and 'correct_answers' in st.session_state:
    display_quiz_with_answers(st.session_state.quiz_content, st.session_state.correct_answers)

from datetime import datetime

st.markdown("## Feedback")

# User identification
user_name = st.text_input("Your Name (optional):")

# Feedback categories
category = st.selectbox(
    "Category:",
    ["General Comment", "Bug Report", "Feature Request", "Other"]
)

# Feedback text area
feedback = st.text_area("Please provide your feedback:")

# Rating system
rating = st.slider("Rate your experience:", 1, 5, 3)

# Submit button
if st.button("Submit Feedback"):
    with open("feedback.txt", "a") as file:
        file.write(f"Name: {user_name if user_name else 'Anonymous'}\n")
        file.write(f"Category: {category}\n")
        file.write(f"Rating: {rating}\n")
        file.write(f"Feedback: {feedback}\n")
        file.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write("\n" + "-"*50 + "\n\n")
    st.success("Thank you for your feedback!")

# Optional: Display previously submitted feedback
if st.checkbox("Show previous feedback"):
    with open("feedback.txt", "r") as file:
        st.text(file.read())