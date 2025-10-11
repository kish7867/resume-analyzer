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

    # elif "View History" in page:
    #     st.title("📜 Analysis History")
    #     headers = {'Authorization': f'Bearer {st.session_state["auth_token"]}'}
        
    #     with st.spinner("Fetching your history..."):
    #         response = requests.get(f"{BACKEND_URL}/api/history/", headers=headers)
        
    #     if response.status_code == 200:
    #         history = response.json()
    #         if not history:
    #             st.info("You have no past analyses. Go ahead and analyze a new resume!")
    #         else:
    #             history.sort(key=lambda x: x['analyzed_at'], reverse=True)
    #             for item in history:
    #                 with st.container(border=True):
    #                     date = datetime.fromisoformat(item['analyzed_at'].replace('Z', '+00:00'))
    #                     st.subheader(f"Analysis from {date.strftime('%B %d, %Y at %I:%M %p')}")
    #                     st.caption(f"Job Description Snippet: *{item['job_description_text'][:150]}...*")
    #                     with st.expander("View Full Analysis"):
    #                         display_results(item['result'])
    #                 st.write("")
    #     else:
    #         st.error("Could not fetch your analysis history.")

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
                # Sort history by analyzed_at descending
                history.sort(key=lambda x: x['analyzed_at'], reverse=True)

                # Helper function to format UTC timestamp to local timezone
                def format_local_time(utc_iso, tz_name='Asia/Kolkata'):
                    from datetime import datetime
                    import pytz
                    # Parse UTC datetime from ISO format
                    utc_date = datetime.fromisoformat(utc_iso.replace('Z', '+00:00'))
                    # Convert to local timezone
                    local_tz = pytz.timezone(tz_name)
                    local_date = utc_date.astimezone(local_tz)
                    # Return formatted string
                    return local_date.strftime('%B %d, %Y at %I:%M %p')
                
                # Display each analysis
                for item in history:
                    with st.container():
                        # Format analyzed_at to local time
                        formatted_date = format_local_time(item['analyzed_at'])

                        st.subheader(f"Analysis from {formatted_date}")
                        st.caption(f"Job Description Snippet: *{item['job_description_text'][:150]}...*")

                        with st.expander("View Full Analysis"):
                            display_results(item['result'])

                        st.markdown("---")  # separator for readability

    
        else:
            st.error("Could not fetch your analysis history. Please try again later.")