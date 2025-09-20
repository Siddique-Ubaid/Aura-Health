import streamlit as st
import datetime
from gtts import gTTS
import io
import base64
import streamlit.components.v1 as components
import pandas as pd
import os
import requests
from streamlit_lottie import st_lottie
import time
import smtplib
import ssl
from email.message import EmailMessage

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Aura Health",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- UI/UX ENHANCEMENTS ---
def load_css():
    css = """
    <style>
        /* Main app background */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        /* Sidebar styling */
        .stSidebar {
            background-color: #161A25;
        }
        /* Button styling */
        .stButton>button {
            border: 2px solid #00F6A7;
            background-color: transparent;
            color: #00F6A7;
            padding: 0.5em 1em;
            border-radius: 0.5rem;
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #00F6A7;
            color: #0E1117;
            border-color: #00F6A7;
        }
        .stButton>button:focus {
            box-shadow: none;
        }
        /* Container styling for cards */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {
            border: 1px solid #2D3D4D;
            border-radius: 0.5rem;
            padding: 1em;
            background-color: #161A25;
        }
        /* Header and title colors */
        h1, h2, h3 {
            color: #00F6A7;
        }
        /* Success message styling */
        .stSuccess {
            background-color: rgba(0, 246, 167, 0.2);
            border: 1px solid #00F6A7;
            border-radius: 0.5rem;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

load_css()

# --- LOTTIE ANIMATION FUNCTION ---
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_doctor = load_lottieurl("https://lottie.host/192796e3-207a-4252-8d01-1372c65a2e5a/bAPf29s3xG.json")

# --- TRANSLATIONS DICTIONARY (STREAMLINED) ---
translations = {
    "en": {
        "login": "Log In", "signup": "Sign Up", "username": "Username", "password": "Password", "email": "Email", "full_name": "Full Name",
        "select_language": "Please Select Your Language", "language_selected": "Language Selected", "welcome_tts": "Welcome to Aura Health. Please select your language to continue.",
        "personal_details": "Step 1: Your Personal Details", "personal_details_tts": "First, let's get some of your personal details.",
        "age": "Age", "gender": "Gender", "contact": "Contact Number", "next_step": "Next Step",
        "select_category": "Step 2: Select a Doctor's Specialty", "select_category_tts": "Now, please select a medical specialty.",
        "select_doctor": "Step 3: Select Your Doctor", "select_doctor_tts": "Here are the available doctors in that specialty.",
        "book_appointment": "Book Appointment", "fees": "Consultation Fees", "view_profile": "View Profile",
        "find_date": "Let's find a date for your appointment.",
        "doctor_busy": "Sorry, the doctor is unavailable on this date. Please choose another.",
        "great_date_set": "Great! The date is set for {date}. Now, let's pick a time.",
        "all_set": "All set! Your appointment is confirmed and an email has been sent to the doctor.",
        "confirm_date": "Confirm Date", "confirm_time": "Confirm Time", "book_another": "Book Another Appointment",
        "admin_dashboard": "Admin Dashboard",
        "about": "About", "welcome": "Welcome", "logout": "Log Out", 
        "logout_tts_feedback": "Thank you for using Aura Health. I hope your appointment is done. Please fill the feedback form after your appointment is done so we will get to know how our app is working.",
        "feedback_title": "Feedback Form", "rating": "Rate your experience (1-5)", "comments": "Any comments?", "submit_feedback": "Submit Feedback & Log Out",
        "appointment_details": "Appointment Details", "patient": "Patient", "doctor": "Doctor", "date": "Date", "time": "Time",
        "warning_all_fields": "Please fill out all fields before proceeding."
    },
    "hi": {
        "login": "लॉग इन करें", "signup": "साइन अप करें", "username": "उपयोगकर्ता नाम", "password": "पासवर्ड", "email": "ईमेल", "full_name": "पूरा नाम",
        "select_language": "कृपया अपनी भाषा चुनें", "language_selected": "भाषा चुनें", "welcome_tts": "ऑरा हेल्थ में आपका स्वागत है। जारी रखने के लिए कृपया अपनी भाषा चुनें।",
        "personal_details": "चरण 1: आपका व्यक्तिगत विवरण", "personal_details_tts": "सबसे पहले, आपके कुछ व्यक्तिगत विवरण चाहिए।",
        "age": "आयु", "gender": "लिंग", "contact": "संपर्क नंबर", "next_step": "अगला चरण",
        "select_category": "चरण 2: डॉक्टर की विशेषज्ञता चुनें", "select_category_tts": "अब, कृपया एक चिकित्सा विशेषता चुनें।",
        "select_doctor": "चरण 3: अपने डॉक्टर का चयन करें", "select_doctor_tts": "इस विशेषज्ञता में उपलब्ध डॉक्टर यहां दिए गए हैं।",
        "book_appointment": "अपॉइंटमेंट बुक करें", "fees": "परामर्श शुल्क", "view_profile": "प्रोफ़ाइल देखें",
        "find_date": "आइए आपकी नियुक्ति के लिए एक तारीख खोजें।",
        "doctor_busy": "माफ़ कीजिए, इस तारीख को डॉक्टर उपलब्ध नहीं हैं। कृपया कोई और तारीख चुनें।",
        "great_date_set": "बहुत बढ़िया! तारीख {date} के लिए निर्धारित है। अब, चलिए एक समय चुनते हैं।",
        "all_set": "सब तैयार है! आपकी नियुक्ति की पुष्टि हो गई है और डॉक्टर को एक ईमेल भेज दिया गया है।",
        "confirm_date": "तारीख की पुष्टि करें", "confirm_time": "समय की पुष्टि करें", "book_another": "एक और अपॉइंटमेंट बुक करें",
        "admin_dashboard": "एडमिन डैशबोर्ड",
        "about": "हमारे बारे में", "welcome": "स्वागत है", "logout": "लॉग आउट",
        "logout_tts_feedback": "ऑरा हेल्थ का उपयोग करने के लिए धन्यवाद। कृपया हमें अपनी प्रतिक्रिया देने के लिए कुछ समय दें।",
        "feedback_title": "प्रतिक्रिया प्रपत्र", "rating": "अपने अनुभव को रेट करें (1-5)", "comments": "कोई टिप्पणी?", "submit_feedback": "प्रतिक्रिया सबमिट करें और लॉग आउट करें",
        "appointment_details": "अपॉइंटमेंट विवरण", "patient": "मरीज़", "doctor": "डॉक्टर", "date": "तारीख", "time": "समय",
        "warning_all_fields": "कृपया आगे बढ़ने से पहले सभी फ़ील्ड भरें।"
    },
    "mr": {
        "login": "लॉग इन करा", "signup": "साइन अप करा", "username": "वापरकर्तानाव", "password": "पासवर्ड", "email": "ईमेल", "full_name": "पूर्ण नाव",
        "select_language": "कृपया तुमची भाषा निवडा", "language_selected": "भाषा निवडा", "welcome_tts": "ऑरा हेल्थमध्ये आपले स्वागत आहे. पुढे जाण्यासाठी कृपया तुमची भाषा निवडा.",
        "personal_details": "पायरी 1: तुमची वैयक्तिक माहिती", "personal_details_tts": "प्रथम, तुमची काही वैयक्तिक माहिती घेऊया.",
        "age": "वय", "gender": "लिंग", "contact": "संपर्क क्रमांक", "next_step": "पुढील पायरी",
        "select_category": "पायरी 2: डॉक्टरचे स्पेशलायझेशन निवडा", "select_category_tts": "आता, कृपया एक वैद्यकीय स्पेशलायझेशन निवडा.",
        "select_doctor": "पायरी 3: तुमचे डॉक्टर निवडा", "select_doctor_tts": "या स्पेशलायझेशनमधील उपलब्ध डॉक्टर येथे आहेत.",
        "book_appointment": "अपॉइंटमेंट बुक करा", "fees": "सल्ला शुल्क", "view_profile": "प्रोफाइल पहा",
        "find_date": "चला तुमच्या भेटीसाठी एक तारीख शोधूया.",
        "doctor_busy": "क्षमस्व, या तारखेला डॉक्टर उपलब्ध नाहीत. कृपया दुसरी तारीख निवडा.",
        "great_date_set": "उत्तम! तारीख {date} साठी निश्चित झाली आहे. आता, वेळ निवडूया.",
        "all_set": "सर्वकाही तयार आहे! तुमची भेट निश्चित झाली आहे आणि डॉक्टरांना एक ईमेल पाठवला गेला आहे.",
        "confirm_date": "तारीख निश्चित करा", "confirm_time": "वेळ निश्चित करा", "book_another": "दुसरी अपॉइंटमेंट बुक करा",
        "admin_dashboard": "ऍडमिन डॅशबोर्ड",
        "about": "आमच्याबद्दल", "welcome": "स्वागत आहे", "logout": "लॉग आउट",
        "logout_tts_feedback": "ऑरा हेल्थ वापरल्याबद्दल धन्यवाद. कृपया आम्हाला तुमचा अभिप्राय देण्यासाठी थोडा वेळ द्या.",
        "feedback_title": "अभिप्राय फॉर्म", "rating": "तुमचा अनुभव रेट करा (1-5)", "comments": "काही टिप्पण्या?", "submit_feedback": "अभिप्राय सबमिट करा आणि लॉग आउट करा",
        "appointment_details": "अपॉइंटमेंट तपशील", "patient": "रुग्ण", "doctor": "डॉक्टर", "date": "तारीख", "time": "वेळ",
        "warning_all_fields": "कृपया पुढे जाण्यापूर्वी सर्व फील्ड भरा."
    }
}


# --- DATABASE AND USER MANAGEMENT ---
USERS_FILE = 'users.csv'
APPOINTMENTS_FILE = 'appointments.csv'
FEEDBACK_FILE = 'feedback.csv'

def register_user(username, password, email, full_name):
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=['username', 'password', 'email', 'full_name']).to_csv(USERS_FILE, index=False)
    users_df = pd.read_csv(USERS_FILE, on_bad_lines='skip')
    if username in users_df['username'].values:
        return False, "Username already exists."
    new_user = pd.DataFrame([[username, password, email, full_name]], columns=['username', 'password', 'email', 'full_name'])
    new_user.to_csv(USERS_FILE, mode='a', header=False, index=False)
    return True, "Signup successful!"

def verify_user(username, password):
    if not os.path.exists(USERS_FILE): return False, 'Patient'
    users_df = pd.read_csv(USERS_FILE, on_bad_lines='skip')
    if username == 'admin' and password == 'admin':
        return True, 'Admin'
    user_data = users_df[(users_df['username'] == username) & (users_df['password'] == str(password))]
    if not user_data.empty:
        return True, 'Patient'
    return False, ''

def save_appointment(patient_details, doctor, date, time):
    if not os.path.exists(APPOINTMENTS_FILE):
        pd.DataFrame(columns=['Patient_Name', 'Patient_Age', 'Patient_Gender', 'Patient_Contact', 'Doctor_Name', 'Doctor_Specialty', 'Date', 'Time']).to_csv(APPOINTMENTS_FILE, index=False)
    new_appointment = pd.DataFrame([[
        patient_details['full_name'], patient_details['age'], patient_details['gender'], patient_details['contact'],
        doctor['name'], doctor['specialty'], date.strftime('%Y-%m-%d'), time
    ]], columns=['Patient_Name', 'Patient_Age', 'Patient_Gender', 'Patient_Contact', 'Doctor_Name', 'Doctor_Specialty', 'Date', 'Time'])
    new_appointment.to_csv(APPOINTMENTS_FILE, mode='a', header=False, index=False)

def save_feedback(username, rating, comments):
    if not os.path.exists(FEEDBACK_FILE):
        pd.DataFrame(columns=['username', 'rating', 'comments', 'timestamp']).to_csv(FEEDBACK_FILE, index=False)
    new_feedback = pd.DataFrame([[username, rating, comments, datetime.datetime.now()]], columns=['username', 'rating', 'comments', 'timestamp'])
    new_feedback.to_csv(FEEDBACK_FILE, mode='a', header=False, index=False)

# --- EMAIL FUNCTIONALITY ---
def send_email(patient_details, doctor, date, time):
    try:
        sender_email = st.secrets["email_credentials"]["sender_email"]
        password = st.secrets["email_credentials"]["sender_password"]
        receiver_email = doctor['email']

        subject = f"New Appointment Booking for Dr. {doctor['name']}"
        body = f"""
        Dear Dr. {doctor['name']},

        A new appointment has been booked via Aura Health.

        Appointment Details:
        - Patient Name: {patient_details['full_name']}
        - Patient Age: {patient_details['age']}
        - Patient Gender: {patient_details['gender']}
        - Patient Contact: {patient_details['contact']}
        - Appointment Date: {date.strftime('%A, %B %d, %Y')}
        - Appointment Time: {time}

        Please update your schedule accordingly.

        Sincerely,
        The Aura Health Team
        """
        
        em = EmailMessage()
        em['From'] = sender_email
        em['To'] = receiver_email
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(sender_email, password)
            smtp.sendmail(sender_email, receiver_email, em.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email. Please check your credentials in secrets.toml. Error: {e}")
        return False

# --- DOCTOR DATABASE ---
doctors = [
    {"name": "Dr. Evelyn Reed", "specialty": "Cardiology", "fees": "₹1500", "qualifications": "MD, FACC", "experience": "15 Years", "bio": "A leading expert in cardiovascular diseases...", "email": "doctor.reed@example.com"},
    {"name": "Dr. Ben Carter", "specialty": "Cardiology", "fees": "₹1200", "qualifications": "MBBS, DNB", "experience": "10 Years", "bio": "Specializes in preventative cardiology...", "email": "doctor.carter@example.com"},
    {"name": "Dr. Aarav Sharma", "specialty": "Cardiology", "fees": "₹1400", "qualifications": "MD", "experience": "12 Years", "bio": "Expert in interventional cardiology...", "email": "doctor.sharma@example.com"},
    {"name": "Dr. Priya Desai", "specialty": "Cardiology", "fees": "₹1600", "qualifications": "MD, DM", "experience": "14 Years", "bio": "Focuses on heart rhythm disorders...", "email": "doctor.desai@example.com"},
    {"name": "Dr. Rohan Joshi", "specialty": "Cardiology", "fees": "₹1350", "qualifications": "MBBS, MD", "experience": "9 Years", "bio": "Dedicated to patient education...", "email": "doctor.joshi@example.com"},
    {"name": "Dr. Marcus Chen", "specialty": "Neurology", "fees": "₹2000", "qualifications": "MD, DM", "experience": "18 Years", "bio": "Renowned for his work in neurodegenerative disorders...", "email": "doctor.chen@example.com"},
    {"name": "Dr. Anika Reddy", "specialty": "Neurology", "fees": "₹2200", "qualifications": "MBBS, MD", "experience": "12 Years", "bio": "Focuses on epilepsy and sleep disorders...", "email": "doctor.reddy@example.com"},
    {"name": "Dr. Vikram Singh", "specialty": "Neurology", "fees": "₹1900", "qualifications": "MD", "experience": "11 Years", "bio": "Specialist in treating migraines...", "email": "doctor.singh@example.com"},
    {"name": "Dr. Sofia Garcia", "specialty": "Pediatrics", "fees": "₹800", "qualifications": "MD, DCH", "experience": "20 Years", "bio": "A compassionate pediatrician...", "email": "doctor.garcia@example.com"},
    {"name": "Dr. Ishan Patel", "specialty": "Pediatrics", "fees": "₹900", "qualifications": "MBBS", "experience": "8 Years", "bio": "Specializes in pediatric nutrition...", "email": "doctor.patel@example.com"},
]
doctor_categories = sorted(list(set(d['specialty'] for d in doctors)))
doctor_busy_dates = { "Dr. Evelyn Reed": [datetime.date(2025, 9, 22), datetime.date(2025, 9, 24)] }


# --- TEXT TO SPEECH FUNCTION ---
def text_to_speech(text, lang='en'):
    if 'tts_played' not in st.session_state: st.session_state.tts_played = set()
    message_key = f"{st.session_state.page}-{st.session_state.booking_step}-{lang}-{text[:20]}"
    if message_key not in st.session_state.tts_played:
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            audio_bytes = audio_fp.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            audio_html = f'<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mpeg"></audio>'
            components.html(audio_html, height=0)
            st.session_state.tts_played.add(message_key)
        except Exception as e:
            st.warning(f"Could not generate audio. Please proceed manually.")

# --- SESSION STATE INITIALIZATION ---
if 'page' not in st.session_state:
    st.session_state.update({
        'page': 'login_signup', 'logged_in': False, 'username': '', 'language': None, 'role': 'Patient',
        'booking_step': 0, 'patient_details': {}, 'doctor_category': '', 'selected_doctor': None,
        'appointment_date': None, 'appointment_time': None, 'tts_played': set()
    })

# --- PAGE ROUTING ---
if not st.session_state.logged_in:
    st.title("🩺 Aura Health Patient Portal")
    login_tab, signup_tab = st.tabs([translations['en']['login'], translations['en']['signup']])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input(translations['en']['username'])
            password = st.text_input(translations['en']['password'], type='password')
            submitted = st.form_submit_button(translations['en']['login'])
            if submitted:
                verified, role = verify_user(username, password)
                if verified:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.session_state.page = 'language_selection' if role == 'Patient' else 'admin_dashboard'
                    st.session_state.tts_played = set()
                    st.rerun()
                else: st.error("Invalid username or password.")
    with signup_tab:
        with st.form("signup_form"):
            full_name = st.text_input(translations['en']['full_name'])
            email = st.text_input(translations['en']['email'])
            username = st.text_input(translations['en']['username'])
            password = st.text_input(translations['en']['password'], type='password')
            submitted = st.form_submit_button(translations['en']['signup'])
            if submitted:
                if not all([full_name, email, username, password]): st.warning("Please fill out all fields.")
                else:
                    success, message = register_user(username, password, email, full_name)
                    if success: st.success(message + " Please log in.")
                    else: st.error(message)

elif st.session_state.language is None and st.session_state.role == 'Patient':
    st.title(f"Welcome, {st.session_state.username}!")
    st.header(translations['en']['select_language'])
    text_to_speech(translations['en']['welcome_tts'], 'en')
    lang_map = {"English": "en", "हिंदी": "hi", "मराठी": "mr"}
    lang_name = st.selectbox("Language / भाषा / भाषा", options=lang_map.keys())
    if st.button(translations['en']['language_selected']):
        st.session_state.language = lang_map[lang_name]
        st.session_state.page = 'patient_dashboard'
        st.rerun()

# --- ADMIN DASHBOARD ---
elif st.session_state.role == 'Admin':
    st.sidebar.title(f"Welcome, Admin!")
    if st.sidebar.button("Log Out"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
    st.title("Admin Dashboard")
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    if os.path.exists(USERS_FILE): col1.metric("Total Users", pd.read_csv(USERS_FILE, on_bad_lines='skip').shape[0])
    if os.path.exists(APPOINTMENTS_FILE): col2.metric("Total Appointments", pd.read_csv(APPOINTMENTS_FILE, on_bad_lines='skip').shape[0])
    if os.path.exists(FEEDBACK_FILE): col3.metric("Total Feedbacks", pd.read_csv(FEEDBACK_FILE, on_bad_lines='skip').shape[0])

    if os.path.exists(APPOINTMENTS_FILE):
        st.subheader("Appointments per Doctor")
        try:
            appointments_df = pd.read_csv(APPOINTMENTS_FILE, on_bad_lines='skip')
            if not appointments_df.empty:
                doctor_counts = appointments_df['Doctor_Name'].value_counts()
                st.bar_chart(doctor_counts)
        except pd.errors.ParserError:
            st.error("Could not parse appointments file. It might be corrupted.")
            
    if os.path.exists(FEEDBACK_FILE):
        st.subheader("Recent Feedback")
        feedback_df = pd.read_csv(FEEDBACK_FILE, on_bad_lines='skip')
        st.dataframe(feedback_df.tail(5))

# --- PATIENT DASHBOARD ---
elif st.session_state.page == 'patient_dashboard':
    lang = st.session_state.language
    st.sidebar.title(f"{translations[lang]['welcome']}, {st.session_state['username']}!")
    
    if st.sidebar.button(translations[lang]['logout']):
        st.session_state.page = 'feedback'
        st.rerun()
    
    # booking_step is now a simple linear flow
    if st.session_state.booking_step == 0:
        st.title(translations[lang]['personal_details'])
        text_to_speech(translations[lang]['personal_details_tts'], lang)
        with st.form("details_form"):
            full_name = st.text_input(translations[lang]['full_name'], st.session_state.username)
            age = st.number_input(translations[lang]['age'], min_value=0, max_value=120)
            gender = st.selectbox(translations[lang]['gender'], ["Male", "Female", "Other"])
            contact = st.text_input(translations[lang]['contact'])
            submitted = st.form_submit_button(translations[lang]['next_step'])
            if submitted:
                if not all([full_name, age > 0, contact]): st.warning(translations[lang]['warning_all_fields'])
                else:
                    st.session_state.patient_details = {'full_name': full_name, 'age': age, 'gender': gender, 'contact': contact}
                    st.session_state.booking_step = 1
                    st.rerun()
    
    elif st.session_state.booking_step == 1:
        st.title(translations[lang]['select_category'])
        text_to_speech(translations[lang]['select_category_tts'], lang)
        category = st.selectbox("Specialty", options=doctor_categories)
        if st.button(translations[lang]['next_step']):
            st.session_state.doctor_category = category
            st.session_state.booking_step = 2
            st.rerun()

    elif st.session_state.booking_step == 2:
        st.title(translations[lang]['select_doctor'])
        text_to_speech(translations[lang]['select_doctor_tts'], lang)
        filtered_doctors = [d for d in doctors if d['specialty'] == st.session_state.doctor_category]
        cols = st.columns(len(filtered_doctors) or 1)
        for i, doctor in enumerate(filtered_doctors):
            with cols[i % len(cols)]:
                with st.container(border=True):
                    st.subheader(doctor['name'])
                    st.markdown(f"**{translations[lang]['fees']}:** {doctor['fees']}")
                    with st.expander(translations[lang]['view_profile']):
                        st.write(f"**Qualifications:** {doctor['qualifications']}")
                        st.write(f"**Experience:** {doctor['experience']}")
                        st.write(f"_{doctor['bio']}_")
                    if st.button(translations[lang]['book_appointment'], key=f"book_{i}"):
                        st.session_state.selected_doctor = doctor
                        st.session_state.booking_step = 3
                        st.rerun()

    elif st.session_state.booking_step == 3:
        st.title(f"Booking with {st.session_state.selected_doctor['name']}")
        if st.session_state.appointment_date is None:
            speech_message = translations[lang]['find_date']
            st.info(f"MediHelp AI: {speech_message}")
            text_to_speech(speech_message, lang)
            selected_date = st.date_input("Select a date", min_value=datetime.date.today(), key="date_picker")
            if st.button(translations[lang]['confirm_date']):
                if selected_date in doctor_busy_dates.get(st.session_state.selected_doctor['name'], []):
                    busy_message = translations[lang]['doctor_busy']
                    st.error(busy_message)
                    text_to_speech(busy_message, lang)
                else:
                    st.session_state.appointment_date = selected_date
                    st.rerun()
        elif st.session_state.appointment_time is None:
            date_str = st.session_state.appointment_date.strftime('%A, %B %d, %Y')
            speech_message = translations[lang]['great_date_set'].format(date=date_str)
            st.info(f"MediHelp AI: {speech_message}")
            text_to_speech(speech_message, lang)
            available_times = ["09:00 AM", "11:30 AM", "02:00 PM", "04:30 PM"]
            time_selection = st.selectbox("Select a time", options=available_times)
            if st.button(translations[lang]['confirm_time']):
                st.session_state.appointment_time = time_selection
                st.rerun()
        else:
            speech_message = translations[lang]['all_set']
            st.success(f"MediHelp AI: {speech_message}")
            text_to_speech(speech_message, lang)
            st.balloons()
            save_appointment(st.session_state.patient_details, st.session_state.selected_doctor, st.session_state.appointment_date, st.session_state.appointment_time)
            send_email(st.session_state.patient_details, st.session_state.selected_doctor, st.session_state.appointment_date, st.session_state.appointment_time)
            
            with st.container(border=True):
                st.markdown(f"### {translations[lang]['appointment_details']}:")
                st.markdown(f"- **{translations[lang]['patient']}:** {st.session_state.patient_details['full_name']}")
                st.markdown(f"- **{translations[lang]['doctor']}:** {st.session_state.selected_doctor['name']} ({st.session_state.selected_doctor['specialty']})")
                st.markdown(f"- **{translations[lang]['date']}:** {st.session_state.appointment_date.strftime('%A, %B %d, %Y')}")
                st.markdown(f"- **{translations[lang]['time']}:** {st.session_state.appointment_time}")
            if st.button(translations[lang]['book_another']):
                st.session_state.booking_step = 0
                st.session_state.patient_details = {}
                st.session_state.doctor_category = ''
                st.session_state.selected_doctor = None
                st.session_state.appointment_date = None
                st.session_state.appointment_time = None
                st.session_state.tts_played = set()
                st.rerun()

# --- FEEDBACK PAGE ---
elif st.session_state.page == 'feedback':
    lang = st.session_state.language or 'en'
    st.title(translations[lang]['feedback_title'])
    feedback_message = translations[lang]['logout_tts_feedback']
    st.info(feedback_message)
    text_to_speech(feedback_message, lang)
    with st.form("feedback_form"):
        rating = st.slider(translations[lang]['rating'], 1, 5, 3)
        comments = st.text_area(translations[lang]['comments'])
        submitted = st.form_submit_button(translations[lang]['submit_feedback'])
        if submitted:
            save_feedback(st.session_state.username, rating, comments)
            st.success("Thank you for your feedback!")
            time.sleep(6) # Wait for long TTS to finish
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

