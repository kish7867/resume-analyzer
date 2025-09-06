import os
import google.generativeai as genai
from PyPDF2 import PdfReader
import json
from dotenv import load_dotenv

# Loads the environment variables from the .env file in your project root.

load_dotenv()

# Configures the Google Generative AI client with the API key.
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# A function to extract text from an uploaded PDF file object.

def extract_text_from_pdf(file_object):
    """
    Extracts text from a given PDF file object.
    """
    try:
        # Creates a PdfReader object from the file stream.
        reader = PdfReader(file_object)
        
        # Initializes an empty string to accumulate text from all pages.
        text = ""
        
        # Loops through each page in the PDF document.
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# The main function that orchestrates the AI analysis using Gemini.
def analyze_resume_with_gemini(resume_text, job_description_text):
    """
    Analyzes resume against a job description using Gemini API.
    """

    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Defines the detailed instructions (the "prompt") for the AI.
    prompt = f"""
    Analyze the following resume against the provided job description. 
    Provide your analysis in a structured JSON format. Do not include any introductory text or markdown formatting like ```json.

    The JSON object should have the following keys:
    - "suitability_score": A score from 0 to 100 representing how well the resume matches the job description.
    - "matching_skills": A list of key skills from the resume that are also mentioned in the job description.
    - "missing_skills": A list of key skills from the job description that are not found in the resume.
    - "suggested_title": A suitable job title for the candidate based on their resume and the job description.
    - "tailored_suggestions": A paragraph providing specific advice on how to improve the resume for this particular job, such as which projects to highlight or which skills to elaborate on.

    Here is the resume text:
    ---
    {resume_text}
    ---

    Here is the job description text:
    ---
    {job_description_text}
    ---
    """

    try:
        # Sends the crafted prompt to the Gemini API to get the analysis.
        # This is the actual network call that communicates with Google's AI servers to perform the complex analysis.
        response = model.generate_content(prompt)
        
        # Attempts to parse the AI's text response as JSON.
        # The API returns a response object, and we need to access its text content, which we've instructed to be in JSON format. The `json.loads()` function converts this JSON string into a Python dictionary.
        return json.loads(response.text)
    except Exception as e:
        # Catches any errors during the API call or JSON parsing.
        print(f"Error calling Gemini API or parsing JSON: {e}")
        return None