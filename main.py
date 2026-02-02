from agents import (
    job_analyzer,
    resume_analyzer,
    cover_letter_writer,
    skill_matcher
)

def coordinator(job_text, resume_text):

    job_skills = job_analyzer(job_text)
    resume_skills = resume_analyzer(resume_text)
    skill_match = skill_matcher(job_skills, resume_skills)
    cover_letter = cover_letter_writer(job_text, resume_text)

    return {
    "job_skills": job_skills,
    "resume_skills": resume_skills,
    "skill_match": skill_match,
    "cover_letter": cover_letter
    }
