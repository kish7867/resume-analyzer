import os
import json
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# -------------------------------
# PDF TEXT EXTRACTION
# -------------------------------
def extract_text_from_pdf(file_object):
    """
    Extracts text from a given PDF file object.
    """
    try:
        reader = PdfReader(file_object)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text.strip()

    except Exception as e:
        print(f"❌ Error extracting text from PDF: {e}")
        return None


# -------------------------------
# RESUME ANALYSIS USING GROQ
# -------------------------------
def analyze_resume_with_llama(resume_text, job_description_text):
    """
    Analyzes resume against a job description using Groq (LLaMA).
    Returns structured JSON only.
    """

    prompt = f"""
You are an AI Resume Analyzer.

Analyze the following resume against the provided job description.
Return ONLY valid JSON. Do NOT add explanations, markdown, or extra text.

The JSON object MUST contain:
- "suitability_score": integer (0–100)
- "matching_skills": list of strings
- "missing_skills": list of strings
- "suggested_title": string
- "tailored_suggestions": string

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
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # Free + fast (recommended)
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        content = response.choices[0].message.content.strip()

        # Debug log
        print("Raw Groq response:", content)

        # Remove accidental markdown fences
        if content.startswith("```"):
            content = content.strip("`").replace("json", "", 1).strip()

        return json.loads(content)

    except json.JSONDecodeError as e:
        print("❌ JSON parsing error:", e)
        return None

    except Exception as e:
        print("❌ Groq API error:", e)
        return None
