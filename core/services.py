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
        # PyPDF2 library uses this object to read and parse the contents of the PDF file
        reader = PdfReader(file_object)
        
        # Initializes an empty string to accumulate text from all pages.
        # Concatenate the text from each page to form the complete resume content.
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
    Ensures valid JSON is returned.
    """
    model = genai.GenerativeModel("gemini-2.0-flash")  # use consistent model

    prompt = f"""
    Analyze the following resume against the provided job description. 
    Provide your analysis in a structured JSON format. Do not include any introductory text or markdown formatting like ```json.

    The JSON object should have the following keys:
    - "suitability_score": A score from 0 to 100 representing how well the resume matches the job description.
    - "matching_skills": A list of key skills from the resume that are also mentioned in the job description.
    - "missing_skills": A list of key skills from the job description that are not found in the resume.
    - "suggested_title": A suitable job title for the candidate based on their resume and the job description.
    - "tailored_suggestions": A paragraph providing specific advice on how to improve the resume for this particular job, such as which projects to highlight or which skills to elaborate on.

    Resume:
    ---
    {resume_text}
    ---

    Job Description:
    ---
    {job_description_text}
    ---
    """

    try:
        response = model.generate_content(prompt)

        # Debug: log the raw response
        print("Raw Gemini response:", response)

        # Extract text safely
        content = ""
        if hasattr(response, "text") and response.text:
            content = response.text.strip()
        elif hasattr(response, "candidates") and response.candidates:
            content = response.candidates[0].content.parts[0].text.strip()

        print("Extracted content:", content)

        # Clean out markdown fences if Gemini adds them
        if content.startswith("```"):
            content = content.strip("`").replace("json", "", 1).strip()

        # Try parsing JSON
        return json.loads(content)

    except json.JSONDecodeError as e:
        print("❌ JSON parsing error:", e)
        return None
    except Exception as e:
        print("❌ Gemini API error:", e)
        return None
