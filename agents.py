from transformers import pipeline

# Load one free model for all agents
generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-large"
)

SKILL_EQUIVALENCE = {
    "apis": ["rest", "rest api", "flask", "fastapi"],
    "data analytics": ["pandas", "numpy", "data analysis"],
    "machine learning": ["ml", "scikit-learn", "basic machine learning"],
    "backend": ["flask", "django", "fastapi"],
}
def normalize(text):
    return text.lower()


import re

def clean_skills(text):
    text = text.lower()
    text = re.sub(r"i know|basic|and|with", "", text)
    return [s.strip() for s in text.split(",") if s.strip()]


def job_analyzer(job_text):
    skills = ["python", "flask", "apis", "machine learning", "sql"]
    job_text = job_text.lower()

    return [skill for skill in skills if skill in job_text]


def resume_analyzer(resume_text):
    skills = ["python", "pandas", "machine learning", "sql", "excel"]
    resume_text = resume_text.lower()

    return [skill for skill in skills if skill in resume_text]


def cover_letter_writer(job_text, resume_text):
    prompt = f"""You are a job applicant.

Write a SHORT professional cover letter from the candidate's perspective (first person: "I").

Rules:
- Say "I am applying for the role"
- Do NOT say "I am looking for a developer"
- Match skills from resume to job
- Max 5 sentences

Job description:
{job_text}

Candidate resume:
{resume_text}
"""

    response = generator(
    prompt,
    max_length=250,
    do_sample=True,
    temperature=0.9,
    top_p=0.9,
    top_k=50
    )

    text = response[0]["generated_text"]
    banned = [
        "I am looking for",
        "looking for a developer",
    ]
    for phrase in banned:
        text = text.replace(phrase, "")
    return text.strip()

def skill_matcher(job_skills, resume_skills):
    job_set = {s.strip().lower() for s in job_skills}
    resume_set = {s.strip().lower() for s in resume_skills}

    matched = job_set & resume_set
    missing = job_set - resume_set

    return {
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "match_percent": round(len(matched) / max(len(job_set), 1) * 100, 2)
    }
