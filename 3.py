import spacy
from spacy.pipeline import EntityRuler
from spacy.lang.en import English
from spacy.tokens import Doc

import json
import re

from tkinter import filedialog

# from spacy.pipeline import ner

nlp = spacy.load("en_core_web_sm")
skill_pattern_path = "jz_skill_patterns.jsonl"
ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(skill_pattern_path)


def extract_education(doc):
    education = []
    for ent in doc.ents:
        if ent.label_ == 'EDUCATION':
            education.append(ent.text)
    return education


def extract_experience(doc):
    experience = []
    for ent in doc.ents:
        if ent.label_ == 'WORK':
            experience.append(ent.text)
    return experience


def get_skills(doc):
    myset = []
    subset = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            subset.append(ent.text)
    myset.append(subset)
    return subset


def parse_resume(resume_file):
    with open(resume_file, 'r') as f:
        text = f.read()
    doc = nlp(text)
    education = extract_education(doc)
    experience = extract_experience(doc)
    skills = get_skills(doc)
    parsed_data = {
        'education': education,
        'experience': experience,
        "skill": skills
    }
    return json.dumps(parsed_data)


im = filedialog.askopenfilename()
parsed_resume = parse_resume(im)
print(parsed_resume)
