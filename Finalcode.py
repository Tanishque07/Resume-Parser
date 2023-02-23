import sys
import fitz
import spacy
import json
import re
from spacy.matcher import Matcher
import nltk
import string

# from spacy.pipeline import ner

nlp = spacy.load("en_core_web_sm")
skills = "jz_skill_patterns.jsonl"
ruler = nlp.add_pipe("entity_ruler")
ruler.from_disk(skills)
matcher = Matcher(nlp.vocab)

from nltk.corpus import stopwords
# Grad all general stop words
nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S',
            'ME', 'M.E', 'M.E.', 'MS', 'M.S',
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
        ]

def convertToText(fname):
  doc = fitz.open(fname)
  text = ""
  for page in doc:
    text = text + str(page.get_text())
  tx = " ".join(text.split("\n"))
  return tx

def extract_name(doc):
    nlp_text = nlp(doc)

    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

    matcher.add('NAME',[pattern])

    matches = matcher(nlp_text)

    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text


def extract_mobile_number(doc):
    phone_regex = r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
    phone_match = re.search(phone_regex, doc)
    phone = phone_match.group(0) if phone_match else None
    return phone

def extract_email(doc):
    email_regex = r"([a-zA-Z0-9.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z0-9_-]+)"
    email_match = re.search(email_regex, doc)
    email = email_match.group(0) if email_match else None
    return email

def extract_education(doc):
    nlp_text = nlp(doc)

    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]

    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{2})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education



def get_skills(doc):
    myset = []
    subset = []
    for ent in doc.ents:
        if ent.label_ == "SKILL":
            subset.append(ent.text)
    myset.append(subset)
    return subset


def parse_resume(resume_file):

    # with open(resume_file, 'r',encoding='latin1') as f:
    #   text = f.read()
    text = convertToText(resume_file)
    doc = nlp(text)
    education = extract_education(text)
    skills = get_skills(doc)
    name=extract_name(text)
    Mobile_=extract_mobile_number(text)
    email=extract_email(text)
    parsed_data = {
        'Name':name,
        "Mobile number": Mobile_,
        "E-mail":email,
        'education': education,
        "skill": skills
    }
    return json.dumps(parsed_data)

parsed_resume = parse_resume('/content/resume.pdf')
print(parsed_resume)
