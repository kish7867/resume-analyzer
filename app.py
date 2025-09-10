# # ==============================================================================
# # FILE: app.py (place this in your project's root directory)
# # ==============================================================================
# import streamlit as st
# import requests
# import pandas as pd # For better table display, optional

# # What: Defines the base URL for our Django API.
# # Why: This makes the code cleaner and easier to update. If we deploy our backend, we only have to change this one line.
# # Consequence if not done: We would have to hardcode "[http://127.0.0.1:8000](http://127.0.0.1:8000)" in every API call, which is repetitive and hard to maintain.
# BACKEND_URL = "http://127.0.0.1:8000/"

# # What: Configures the Streamlit page with a title and an icon.
# # Why: This is the first thing a user sees. It sets the branding and context for the entire application.
# # Consequence if not done: The browser tab would show a generic title, and the page would lack a professional look.
# st.set_page_config(page_title="AI Resume Analyzer", page_icon="🧠")

# # --- Helper Functions for API calls ---

# # What: A function to handle user login.
# # Why: Encapsulates the logic for sending a POST request to the token endpoint. It helps keep the main app logic clean.
# # Consequence if not done: The login API call logic would be mixed in with the UI code, making it harder to read and debug.
# def login_user(username, password):
#     response = requests.post(f"{BACKEND_URL}/api/token/", data={"username": username, "password": password})
#     return response

# # What: A function to handle user registration.
# # Why: Similar to login, it isolates the API call for creating a new user.
# # Consequence if not done: Signup logic would clutter the main part of the app.
# def register_user(username, email, password):
#     response = requests.post(f"{BACKEND_URL}/api/register/", json={"username": username, "email": email, "password": password})
#     return response

# # --- UI Rendering Functions ---

# # What: Displays the analysis results in a visually appealing way.
# # Why: A good UI is crucial for user experience. This function uses Streamlit components like metrics, progress bars, and expanders to present the complex AI output in an easy-to-digest format.
# # Consequence if not done: We would just be printing the raw JSON, which is ugly and not user-friendly.
# def display_results(result):
#     st.subheader("Analysis Results")
#     score = result.get('suitability_score', 0)
    
#     st.metric(label="Suitability Score", value=f"{score}%")
#     st.progress(score / 100)

#     col1, col2 = st.columns(2)
#     with col1:
#         st.success("✅ Matching Skills")
#         st.write(", ".join(result.get('matching_skills', [])))
#     with col2:
#         st.warning("❌ Missing Skills")
#         st.write(", ".join(result.get('missing_skills', [])))

#     st.info(f"✨ Suggested Job Title: **{result.get('suggested_title', 'N/A')}**")

#     with st.expander("📝 Tailored Suggestions for Improvement"):
#         st.write(result.get('tailored_suggestions', 'No suggestions available.'))


# # --- Main Application Logic ---

# # What: Initializes session state variables.
# # Why: Streamlit reruns the entire script on every user interaction. `st.session_state` is the only way to maintain data (like login status or tokens) between these reruns.
# # Consequence if not done: The user would be logged out after every single click, and we couldn't store the authentication token, making the app unusable.
# if 'auth_token' not in st.session_state:
#     st.session_state['auth_token'] = None
# if 'page' not in st.session_state:
#     st.session_state['page'] = 'Login'
# if 'uploaded_resume_id' not in st.session_state:
#     st.session_state['uploaded_resume_id'] = None


# # --- Authentication Pages ---
# if not st.session_state['auth_token']:
#     st.title("Welcome to the AI Resume Analyzer")
#     choice = st.radio("Choose an action", ["Login", "Sign Up"])

#     if choice == "Login":
#         username = st.text_input("Username")
#         password = st.text_input("Password", type="password")
#         if st.button("Login"):
#             response = login_user(username, password)
#             if response.status_code == 200:
#                 st.session_state['auth_token'] = response.json().get('access')
#                 st.success("Logged in successfully!")
#                 st.rerun() # What: Forces Streamlit to rerun the script immediately. Why: To show the main app dashboard instead of the login page.
#             else:
#                 st.error("Invalid credentials.")
#     else: # Sign Up
#         username = st.text_input("Choose a Username")
#         email = st.text_input("Your Email")
#         password = st.text_input("Choose a Password", type="password")
#         if st.button("Sign Up"):
#             response = register_user(username, email, password)
#             if response.status_code == 201:
#                 st.success("Account created! Please log in.")
#             else:
#                 st.error(f"Failed to create account: {response.json()}")

# # --- Main App & History Pages ---
# else:
#     st.sidebar.title("Navigation")
#     page = st.sidebar.radio("Go to", ["Analyze New Resume", "View History"])

#     if page == "Analyze New Resume":
#         st.title("📄 AI-Powered Resume Analyzer")

#         col1, col2 = st.columns(2)

#         with col1:
#             st.header("Upload Your Resume")
#             uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
#             if uploaded_file:
#                 # What: Prepares the authorization header for API requests.
#                 # Why: All our protected backend endpoints require a "Bearer" token to authenticate the user.
#                 # Consequence if not done: All API calls to protected endpoints would fail with a 401 Unauthorized error.
#                 headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
#                 files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                
#                 # What: A button to trigger the upload process.
#                 # Why: We separate the file selection from the upload action to give the user control.
#                 # Consequence if not done: The file might be uploaded automatically on selection, which might not be the desired user experience.
#                 if st.button("Upload and Preview"):
#                     with st.spinner('Uploading resume...'):
#                         response = requests.post(f"{BACKEND_URL}/api/resumes/upload/", headers=headers, files=files)
#                         if response.status_code == 201:
#                             st.session_state['uploaded_resume_id'] = response.json().get('id')
#                             st.success("Resume uploaded successfully!")
#                             st.info(f"Resume ID: {st.session_state['uploaded_resume_id']}")
#                         else:
#                             st.error(f"Upload failed: {response.text}")

#         with col2:
#             st.header("Paste Job Description")
#             jd_text = st.text_area("Paste the job description here...", height=300)
            
#             # What: Checks if both a resume has been uploaded AND JD text is present before enabling the button.
#             # Why: Prevents the user from trying to run an analysis with incomplete information, which would just result in an error.
#             # Consequence if not done: Users could click "Analyze" without providing the necessary inputs, leading to a poor user experience and unnecessary error messages.
#             if st.button("Analyze ✨", disabled=(not st.session_state['uploaded_resume_id'] or not jd_text)):
#                 with st.spinner('AI is analyzing... this may take a moment...'):
#                     headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
#                     data = {'resume_id': st.session_state['uploaded_resume_id'], 'jd_text': jd_text}
#                     response = requests.post(f"{BACKEND_URL}/api/analyze/", headers=headers, json=data)

#                     if response.status_code == 201:
#                         # What: Stores the latest result in session state.
#                         # Why: So we can display it immediately without another API call.
#                         # Consequence if not done: We would have to fetch the result again after creating it.
#                         st.session_state['latest_analysis'] = response.json().get('result')
#                     else:
#                         st.error(f"Analysis failed: {response.text}")

#         # Display latest analysis if it exists
#         if 'latest_analysis' in st.session_state and st.session_state['latest_analysis']:
#             st.markdown("---")
#             display_results(st.session_state['latest_analysis'])


#     elif page == "View History":
#         st.title("📜 Analysis History")
#         headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
#         response = requests.get(f"{BACKEND_URL}/api/history/", headers=headers)
#         if response.status_code == 200:
#             history = response.json()
#             if not history:
#                 st.info("No past analyses found.")
#             else:
#                 for item in history:
#                     with st.container():
#                         st.subheader(f"Analysis from {pd.to_datetime(item['analyzed_at']).strftime('%B %d, %Y')}")
#                         # What: Shows a snippet of the JD for context.
#                         # Why: Helps the user remember which job this analysis was for.
#                         # Consequence if not done: The user would just see a list of results with no context about the job they were for.
#                         st.caption(f"Job Description: *{item['job_description_text'][:100]}...*")
#                         display_results(item['result'])
#                         st.markdown("---")

#         else:
#             st.error("Could not fetch history.")

#     if st.sidebar.button("Logout"):
#         st.session_state['auth_token'] = None
#         st.rerun()




import os
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")


# --- Page Configuration (Do this first!) ---
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Helper Functions for API calls (No changes needed) ---

def login_user(username, password):
    response = requests.post(f"{BACKEND_URL}/api/token/", data={"username": username, "password": password})
    return response

def register_user(username, email, password):
    response = requests.post(f"{BACKEND_URL}/api/register/", json={"username": username, "email": email, "password": password})
    return response

# --- UI Rendering Functions (No changes needed) ---

def display_results(result):
    """Displays the analysis results in a more structured and visually appealing way."""
    st.subheader("📊 Analysis Results")

    # Use a container with a border for a card-like effect
    with st.container(border=True):
        score = result.get('suitability_score', 0)
        st.metric(label="**Suitability Score**", value=f"{score}%")
        st.progress(score, text=f"{score}% Match")
        st.info(f"**Suggested Job Title:** {result.get('suggested_title', 'N/A')}", icon="✨")

    st.write("") # Add some space

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("##### ✅ Matching Skills")
            matching_skills = result.get('matching_skills', [])
            if matching_skills:
                for skill in matching_skills:
                    st.markdown(f"- {skill}")
            else:
                st.write("No matching skills found.")

    with col2:
        with st.container(border=True):
            st.markdown("##### ❌ Missing Skills")
            missing_skills = result.get('missing_skills', [])
            if missing_skills:
                for skill in missing_skills:
                    st.markdown(f"- {skill}")
            else:
                st.success("No missing skills found!")

    st.write("") # Add some space

    with st.expander("💡 **Tailored Suggestions for Improvement**"):
        st.markdown(result.get('tailored_suggestions', 'No suggestions available.'))

# --- Main Application Logic ---

# Initialize session state variables
if 'auth_token' not in st.session_state:
    st.session_state['auth_token'] = None
# This new state will hold info about the uploaded file
if 'uploaded_resume_info' not in st.session_state:
    st.session_state['uploaded_resume_info'] = None
if 'latest_analysis' not in st.session_state:
    st.session_state['latest_analysis'] = None

# --- Authentication Pages (No changes needed) ---
if not st.session_state.get('auth_token'):
    st.title("Welcome to the AI Resume Analyzer 🧠")
    st.caption("Please log in or create an account to continue")

    login_tab, signup_tab = st.tabs(["**Login**", "**Sign Up**"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", type="primary")

            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    response = login_user(username, password)
                    if response.status_code == 200:
                        st.session_state['auth_token'] = response.json().get('access')
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")

    with signup_tab:
     with st.form("signup_form"):
        username = st.text_input("Choose a Username", key="signup_username")
        email = st.text_input("Your Email", key="signup_email")
        password = st.text_input("Choose a Password", type="password", key="signup_password")
        submitted = st.form_submit_button("Sign Up", type="primary")

        if submitted:
            if not username or not email or not password:
                st.error("Please fill in all fields.")
            else:
                response = register_user(username, email, password)
                if response is None:
                    st.error("Signup request failed due to network issues.")
                else:
                    # Safely handle JSON decoding
                    try:
                        data = response.json()
                    except requests.exceptions.JSONDecodeError:
                        st.error(f"Failed to create account. Server returned non-JSON response:\n{response.text}")
                    else:
                        if response.status_code == 201:
                            st.success("Account created! You can now log in.")
                        else:
                            # Backend may provide 'detail' key or something else
                            error_message = data.get("detail") or data.get("message") or "Unknown error"
                            st.error(f"Failed to create account: {error_message}")

# --- Main App & History Pages ---
else:
    # Sidebar Navigation
    with st.sidebar:
        st.title("Navigation")
        page = st.radio("Go to", ["Analyze New Resume 📄", "View History 📜"], label_visibility="hidden")
        st.write("---")
        if st.button("Logout 🚪"):
            # Clear all session state on logout for a clean slate
            for key in st.session_state.keys():
                del st.session_state[key]
            st.rerun()

    # ==================================================================
    # === THIS IS THE SECTION WITH THE INTERACTIVE IMPROVEMENTS ========
    # ==================================================================
    if "Analyze New Resume" in page:
        st.title("AI-Powered Resume Analyzer")
        st.markdown("Follow the steps below to get an instant analysis of your resume.")

        # --- STEP 1: RESUME UPLOAD ---
        if st.session_state.get('uploaded_resume_info') is None:
            st.subheader("Step 1: Upload Your Resume")
            uploaded_file = st.file_uploader(
                "Choose a PDF file to begin",
                type="pdf",
                label_visibility="collapsed"
            )
            if uploaded_file:
                with st.status("Uploading and processing resume...", expanded=True) as status:
                    headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
                    response = requests.post(f"{BACKEND_URL}/api/resumes/upload/", headers=headers, files=files)
                    if response.status_code == 201:
                        # Store file info in session state
                        st.session_state['uploaded_resume_info'] = {
                            'id': response.json().get('id'),
                            'name': uploaded_file.name
                        }
                        status.update(label="✅ Upload successful!", state="complete", expanded=False)
                        st.rerun() # Rerun to move to the next step
                    else:
                        status.update(label="Upload failed!", state="error", expanded=True)
                        st.error(f"Upload failed: {response.text}")
        
        # --- STEP 2 & 3: JOB DESCRIPTION & ANALYSIS ---
        else:
            # Show which file is ready for analysis
            file_name = st.session_state['uploaded_resume_info']['name']
            st.success(f"✅ **{file_name}** is uploaded and ready.")
            if st.button("Upload a different resume", type="secondary"):
                st.session_state['uploaded_resume_info'] = None
                st.rerun()
            
            st.divider()

            st.subheader("Step 2: Paste Job Description")
            jd_text = st.text_area("Paste the job description here...", height=250, label_visibility="collapsed")
            
            st.write("") # Spacer

            st.subheader("Step 3: Analyze")
            if st.button("Analyze Now ✨", type="primary", use_container_width=True, disabled=(not jd_text)):
                with st.status("AI is analyzing... this may take a moment...", expanded=True) as status:
                    headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
                    data = {'resume_id': st.session_state['uploaded_resume_info']['id'], 'jd_text': jd_text}
                    response = requests.post(f"{BACKEND_URL}/api/analyze/", headers=headers, json=data)
                    
                    if response.status_code == 201:
                        st.session_state['latest_analysis'] = response.json().get('result')
                        # Reset resume info for the next analysis
                        st.session_state['uploaded_resume_info'] = None
                        status.update(label="Analysis complete!", state="complete")
                        st.rerun()
                    else:
                        status.update(label="Analysis Failed!", state="error")
                        st.error(f"Analysis failed: {response.text}")

        # --- Display latest analysis results ---
        if st.session_state.get('latest_analysis'):
            st.divider()
            display_results(st.session_state['latest_analysis'])

    elif "View History" in page:
        st.title("📜 Analysis History")
        headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
        
        with st.spinner("Fetching your history..."):
            response = requests.get(f"{BACKEND_URL}/api/history/", headers=headers)
        
        if response.status_code == 200:
            history = response.json()
            if not history:
                st.info("You have no past analyses. Go ahead and analyze a new resume!")
            else:
                history.sort(key=lambda x: x['analyzed_at'], reverse=True)
                for item in history:
                    with st.container(border=True):
                        date = datetime.fromisoformat(item['analyzed_at'].replace('Z', '+00:00'))
                        st.subheader(f"Analysis from {date.strftime('%B %d, %Y at %I:%M %p')}")
                        st.caption(f"Job Description Snippet: *{item['job_description_text'][:150]}...*")
                        with st.expander("View Full Analysis"):
                            display_results(item['result'])
                    st.write("")
        else:
            st.error("Could not fetch your analysis history.")