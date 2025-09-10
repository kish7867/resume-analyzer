🧠 AI Resume Analyzer

A full-stack web application that uses the Google Gemini API to analyze resumes against job descriptions. Get a suitability score, skill comparison, tailored feedback, and suggested job titles. Built with Django for the backend and Streamlit for a modern, interactive frontend.

Check out the live frontend: https://resume-analyzer-frontend-6sgt.onrender.com

✨ Key Features

User Authentication: Secure signup, login, and session management.

Resume Upload: Easily upload PDF resumes for analysis.

AI-Powered Analysis:

Calculates a suitability score.

Highlights matching and missing skills.

Provides personalized suggestions to improve your resume.

Suggests a best-fit job title.

Analysis History: Keep track of all your past resume evaluations.

Clean, Responsive UI: Built with Streamlit for a smooth, modern experience.

🧰 Tech Stack

Backend: Django, Django REST Framework

Frontend: Streamlit

Database: SQLite (local), PostgreSQL (production-ready)

AI: Google Gemini API

PDF Parsing: PyPDF2

🛠️ Local Development

Follow these steps to get the project running locally:

1. Prerequisites:-

Python 3.8+

Git

2. Clone the Repository:-

git clone https://github.com/your-username/resume-analyzer-project.git
cd resume-analyzer-project
   
3. Set Up a Virtual Environment:-

# Create a virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

4. Install Dependencies:-

pip install -r requirements.txt

5. Configure Environment Variables:-

 1. Copy the example .env file:-
  cp .env.example .env

 2. Create this file in your root directory as a template for your .env file:-
    # Copy this file to .env and fill in your actual values.
    # DO NOT COMMIT the actual .env to version control.

    # Django Settings
    DJANGO_SECRET_KEY="your-super-secret-key-for-local-dev"
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost

    # For production databases, e.g., PostgreSQL or MySQL:
    # DATABASE_URL="postgres://user:password@host:port/dbname"

    # Gemini API Key
    GEMINI_API_KEY="your-google-gemini-api-key"

    # CORS (for local Streamlit frontend)
    CORS_ALLOWED_ORIGINS=http://localhost:8501

    #  Streamlit backend URL
    BACKEND_URL=http://127.0.0.1:8000

6. Set Up the Database:-

# Apply migrations
python manage.py migrate

# Create a superuser to access the Django admin
python manage.py createsuperuser

7. Run the Application

You’ll need two terminals: one for the backend and one for the frontend.

Terminal 1 – Django Backend: python manage.py runserver
Backend URL: http://127.0.0.1:8000

Terminal 2 – Streamlit Frontend: streamlit run app.py
streamlit run app.py

Open the frontend in your browser and start analyzing resumes! 🚀

🚀 Deployment

This project is deployment-ready using Render:

PostgreSQL Database – for production data storage.

Django Backend – deploy as a web service using Gunicorn.

Streamlit Frontend – deploy as a separate web service.
