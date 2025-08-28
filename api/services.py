import spacy
import fitz  # PyMuPDF
from .models import Skill, ExtractedSkill
import os
from django.conf import settings

nlp = spacy.load("en_core_web_sm") 

def extract_text_from_pdf(file_path):
    """Extracts text from a given PDF file."""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def extract_skills(text):
    """Extracts skills from text using a custom spaCy pipeline."""
    doc = nlp(text)
    ruler_path = os.path.join(settings.BASE_DIR, 'api', 'skills.jsonl')
    if "entity_ruler" not in nlp.pipe_names:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        ruler.from_disk(ruler_path)

    skills = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            skills.append(ent.text)
    return list(set([skill.lower() for skill in skills]))
